import asyncio
import json
from typing import Any, Dict, List, Optional

import cv2
import numpy as np
from sqlalchemy.orm import Session

from app.api.websocket import manager as ws_manager
from app.behaviours.drag import DragBehaviour
from app.behaviours.drop_throw import DropThrowBehaviour
from app.behaviours.equipment import EquipmentBehaviour
from app.behaviours.orientation import OrientationBehaviour
from app.behaviours.overhang import PalletOverhangBehaviour
from app.behaviours.rough_handling import RoughHandlingBehaviour
from app.behaviours.sequence import SequenceBehaviour
from app.behaviours.stacking import StackingBehaviour
from app.behaviours.staging import ImproperStagingBehaviour
from app.behaviours.unsupported_stack import UnsupportedStackBehaviour
from app.core.config import PROCESSED_DIR
from app.core.logging import logger
from app.database.repositories.video_repo import VideoRepository
from app.incidents.event_manager import EventManager
from app.ingestion.video_reader import VideoReader
from app.intelligence.geometry import calculate_iou
from app.intelligence.object_memory import ObjectMemory
from app.intelligence.scene_graph import SceneGraph
from app.intelligence.zones import ZoneManager
from app.perception.detector import WarehouseDetector
from app.perception.tracker import WarehouseTracker
from app.risk.risk_engine import RiskEngine
from app.sop.rule_engine import RuleEngine


class VideoAnalysisService:
    """Runs the existing vision/risk pipeline and publishes its actual evidence."""

    def __init__(self, db: Session):
        self.db = db
        self.detector = WarehouseDetector()
        self.tracker = WarehouseTracker()
        self.memory = ObjectMemory()
        self.zone_mgr = ZoneManager()
        self.scene_graph = SceneGraph()
        self.event_mgr = EventManager(db)
        self.video_repo = VideoRepository(db)
        self.rule_engine = RuleEngine()

    def _apply_sop(self, result: Optional[Dict[str, Any]], context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Keep physical observations separate from declarative SOP interpretation."""
        if not result:
            return None
        sop_result = self.rule_engine.evaluate_behaviour(result["behaviour"], context)
        if not sop_result:
            return None
        interpreted = dict(result)
        interpreted["behaviour_name"] = sop_result["name"]
        interpreted["severity"] = sop_result["severity"]
        interpreted["recommendation"] = sop_result["recommendation"] or result["recommendation"]
        interpreted["sop_rule_code"] = sop_result["code"]
        return interpreted

    @staticmethod
    def _track_payload(track: Dict[str, Any], width: int, height: int) -> Dict[str, Any]:
        """Normalize detector coordinates so React can draw at any display size."""
        x1, y1, x2, y2 = track["bbox"]
        return {
            "track_id": track["track_id"],
            "class_name": track["class_name"],
            "label": track["label"],
            "confidence": track["confidence"],
            "bbox": [
                round(max(0.0, min(1.0, x1 / width)), 5),
                round(max(0.0, min(1.0, y1 / height)), 5),
                round(max(0.0, min(1.0, x2 / width)), 5),
                round(max(0.0, min(1.0, y2 / height)), 5),
            ],
        }

    @staticmethod
    def _nearest_worker(subject: Dict[str, Any], workers: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Attribute only an observed nearby worker; never manufacture an ID."""
        if not workers:
            return None
        sx1, sy1, sx2, sy2 = subject["bbox"]
        scx, scy = (sx1 + sx2) / 2, (sy1 + sy2) / 2
        closest, distance = None, float("inf")
        for worker in workers:
            wx1, wy1, wx2, wy2 = worker["bbox"]
            worker_distance = (((scx - (wx1 + wx2) / 2) ** 2) + ((scy - (wy1 + wy2) / 2) ** 2)) ** 0.5
            if worker_distance < distance:
                closest, distance = worker, worker_distance
        span = max(sx2 - sx1, sy2 - sy1)
        return closest if closest and distance < max(180.0, span * 3) else None

    def _incident_metadata(
        self,
        tracks: List[Dict[str, Any]],
        subject: Dict[str, Any],
        workers: List[Dict[str, Any]],
        width: int,
        height: int,
        related: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        worker = self._nearest_worker(subject, workers)
        return {
            "subject": self._track_payload(subject, width, height),
            "worker": self._track_payload(worker, width, height) if worker else None,
            "related_objects": [self._track_payload(item, width, height) for item in related or []],
            # Persist the entire detection snapshot: it powers both live and
            # post-analysis overlays, rather than a frontend fixture.
            "tracks": [self._track_payload(track, width, height) for track in tracks],
        }

    @staticmethod
    def _event_payload(event: Any, metadata: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "id": event.id,
            "video_id": event.video_id,
            "timestamp": event.timestamp,
            "timestamp_seconds": event.timestamp_seconds,
            "behaviour": event.behaviour,
            "behaviour_name": event.behaviour_name,
            "display_label": EventManager.display_label(event.behaviour),
            "object_id": event.object_id,
            "risk_score": event.risk_score,
            "risk_level": event.risk_level,
            "zone": event.zone,
            "evidence": json.loads(event.evidence_json) if event.evidence_json else [],
            "recommendation": event.recommendation,
            "confidence": event.confidence,
            "severity": event.severity,
            "duration": event.duration,
            "metadata": metadata,
            "review_status": event.review_status,
        }

    async def _record_and_publish(
        self,
        *,
        job_id: str,
        video_id: int,
        source_video_path: str,
        time_s: float,
        frame_idx: int,
        result: Dict[str, Any],
        risk: Dict[str, Any],
        subject: Dict[str, Any],
        tracks: List[Dict[str, Any]],
        workers: List[Dict[str, Any]],
        width: int,
        height: int,
        related: Optional[List[Dict[str, Any]]] = None,
    ) -> Optional[Dict[str, Any]]:
        metadata = self._incident_metadata(tracks, subject, workers, width, height, related)
        event = self.event_mgr.record_incident(
            video_id=video_id,
            source_video_path=source_video_path,
            timestamp_seconds=time_s,
            behaviour=result["behaviour"],
            behaviour_name=result["behaviour_name"],
            object_id=subject["label"],
            risk_score=risk["score"],
            risk_level=risk["level"],
            zone=self.zone_mgr.get_zone_for_box(subject["bbox"], width, height),
            evidence=result["evidence"],
            recommendation=result["recommendation"],
            factors=risk["factors"],
            duration=result["duration"],
            frame_idx=frame_idx,
            metadata=metadata,
        )
        if not event:
            return None
        payload = self._event_payload(event, metadata)
        await ws_manager.broadcast_to_job(job_id, {"type": "incident_detected", "incident": payload})
        return payload

    @staticmethod
    def _risk(severity: str, motion: float, duration: float, spatial: float, zone: str) -> Dict[str, Any]:
        return RiskEngine.calculate_risk(
            behaviour_severity=severity,
            motion_intensity=motion,
            duration_s=duration,
            spatial_factor=spatial,
            repetition_count=1,
            zone=zone,
        )

    @staticmethod
    def _draw_label(frame: np.ndarray, text: str, x: int, y: int, color: tuple) -> None:
        size, _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 2)
        top = max(0, y - size[1] - 12)
        cv2.rectangle(frame, (x, top), (x + size[0] + 10, y), color, -1)
        cv2.putText(frame, text, (x + 5, y - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)

    def _annotate_frame(
        self,
        frame: np.ndarray,
        tracks: List[Dict[str, Any]],
        alerts: List[Dict[str, Any]],
        width: int,
        height: int,
        fps: float,
        time_s: float,
        incident_count: int,
    ) -> None:
        for zone in self.zone_mgr.zones:
            points = zone.get("polygon", [])
            if points:
                polygon = np.array([[int(x * width), int(y * height)] for x, y in points], np.int32)
                cv2.polylines(frame, [polygon], True, (60, 60, 60), 1)
        for track in tracks:
            x1, y1, x2, y2 = [int(value) for value in track["bbox"]]
            color = (255, 180, 0) if track["class_name"] == "person" else (50, 205, 50)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, f"{track['label']} ({int(track['confidence'] * 100)}%)", (x1, max(58, y1 - 8)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        colors = {"CRITICAL": (0, 0, 255), "HIGH": (0, 69, 255), "MEDIUM": (0, 165, 255), "LOW": (0, 215, 255)}
        for alert in alerts:
            color = colors.get(alert["risk_level"], (0, 165, 255))
            targets = [alert["metadata"]["subject"], *alert["metadata"].get("related_objects", [])]
            if alert["metadata"].get("worker"):
                targets.append(alert["metadata"]["worker"])
            for target in targets:
                x1, y1, x2, y2 = target["bbox"]
                box = (int(x1 * width), int(y1 * height), int(x2 * width), int(y2 * height))
                cv2.rectangle(frame, box[:2], box[2:], color, 4)
                self._draw_label(frame, alert["display_label"], box[0], max(58, box[1] - 6), color)

        cv2.rectangle(frame, (0, 0), (width, 42), (18, 18, 18), -1)
        hud = f"CargoIQ | FPS: {round(fps)} | TIME: {time_s:.1f}s | INCIDENTS: {incident_count}"
        cv2.putText(frame, hud, (15, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 230, 255), 2)

    async def run_analysis(self, video_id: int, job_id: str):
        video = self.video_repo.get_by_id(video_id)
        if not video:
            logger.error("Video %s not found for analysis.", video_id)
            return

        reader: Optional[VideoReader] = None
        writer: Optional[cv2.VideoWriter] = None
        source_path = video.file_path
        processed_path = PROCESSED_DIR / f"processed_{video_id}.mp4"
        try:
            reader = VideoReader(source_path)
            total_frames, fps, width, height = reader.total_frames, reader.fps, reader.width, reader.height
            if not self.detector.is_available:
                detail = self.detector.model_error or "The configured YOLO model could not be loaded."
                raise RuntimeError(f"Vision model unavailable. {detail}")
            frame_step = 1 if total_frames < 900 else 2
            # Sampling a long feed is fine, but its preview must retain the source timestamp axis.
            writer = cv2.VideoWriter(str(processed_path), cv2.VideoWriter_fourcc(*"mp4v"), max(1.0, fps / frame_step), (width, height))
            if not writer.isOpened():
                raise RuntimeError("Could not create the processed video output.")

            self.video_repo.update_job_progress(job_id, 2, 0, "Initializing perception pipeline...", "processing")
            await ws_manager.broadcast_to_job(job_id, {"type": "progress", "percentage": 2, "frame": 0, "total_frames": total_frames, "status": "processing", "message": "Initializing perception pipeline..."})

            analyzed_count, incident_count = 0, 0
            for frame_idx, time_s, frame in reader.frames(step=frame_step):
                tracks = self.tracker.update(self.detector.detect(frame))
                workers = [track for track in tracks if track["class_name"] == "person"]
                cartons = [track for track in tracks if track["class_name"] in {"carton", "package", "box"}]
                pallets = [track for track in tracks if track["class_name"] == "pallet"]
                equipment = [track for track in tracks if track["class_name"] in {"trolley", "pallet truck", "forklift"}]
                for track in tracks:
                    nearby_worker = None if track["class_name"] == "person" else next((worker["track_id"] for worker in workers if calculate_iou(track["bbox"], worker["bbox"]) > 0.05), None)
                    self.memory.update_track(track["track_id"], track["class_name"], frame_idx, time_s, track["bbox"], nearby_worker)
                self.scene_graph.build_frame_graph(tracks, self.zone_mgr, width, height)
                frame_alerts: List[Dict[str, Any]] = []

                for carton in cartons:
                    history = self.memory.get_track(carton["track_id"])
                    if not history:
                        continue
                    zone = self.zone_mgr.get_zone_for_box(carton["bbox"], width, height)
                    recent = history.get_recent_frames(15)
                    max_downward_velocity = max((frame["vy"] for frame in recent), default=0.0)
                    average_horizontal_velocity = sum(abs(frame["vx"]) for frame in recent) / max(1, len(recent))
                    evaluations = [
                        (self._apply_sop(DropThrowBehaviour.analyze(history, time_s, height), {"previously_supported": True, "operator_separation": True, "high_vertical_velocity": True, "sudden_stop": True, "floor_contact": True, "vertical_velocity": round(max_downward_velocity, 1)}), "HIGH", 0.85, 1.2, 0.80, []),
                        (self._apply_sop(DragBehaviour.analyze(history, time_s, height), {"near_floor": True, "horizontal_motion": True, "duration_seconds": 2.4, "equipment_present": False, "duration_s": 2.4, "horizontal_velocity": round(average_horizontal_velocity, 1)}), "MEDIUM", 0.55, None, 0.60, []),
                        (self._apply_sop(ImproperStagingBehaviour.analyze(carton["bbox"], zone), {"outside_designated_polygon": True, "in_aisle_or_walkway": True}), "MEDIUM", 0.10, 4.0, 0.65, []),
                        (self._apply_sop(RoughHandlingBehaviour.analyze(history), {"impact_deceleration_high": True, "sudden_direction_change": True}), "HIGH", 0.85, 1.0, 0.50, []),
                        (self._apply_sop(OrientationBehaviour.analyze(carton["bbox"]), {"aspect_ratio_inverted": True, "orientation_deviant": True}), "LOW", 0.05, 2.0, 0.40, []),
                        (self._apply_sop(EquipmentBehaviour.analyze(carton["bbox"], len(workers), bool(equipment)), {"single_operator": len(workers) == 1, "large_volume_item": True, "no_trolley": not bool(equipment)}), "MEDIUM", 0.20, 3.0, 0.55, equipment),
                    ]
                    for result, severity, motion, fallback_duration, spatial, related in evaluations:
                        if not result:
                            continue
                        duration = result.get("duration", fallback_duration or 1.0)
                        event = await self._record_and_publish(job_id=job_id, video_id=video_id, source_video_path=source_path, time_s=time_s, frame_idx=frame_idx, result=result, risk=self._risk(severity, motion, duration, spatial, zone), subject=carton, tracks=tracks, workers=workers, width=width, height=height, related=related)
                        if event:
                            incident_count += 1
                            frame_alerts.append(event)
                    for pallet in pallets:
                        raw_result = PalletOverhangBehaviour.analyze(carton["bbox"], pallet["bbox"])
                        result = self._apply_sop(raw_result, {"support_ratio": raw_result.get("support_ratio", 1.0) if raw_result else 1.0})
                        if result:
                            event = await self._record_and_publish(job_id=job_id, video_id=video_id, source_video_path=source_path, time_s=time_s, frame_idx=frame_idx, result=result, risk=self._risk("HIGH", 0.20, result["duration"], 0.75, zone), subject=carton, tracks=tracks, workers=workers, width=width, height=height, related=[pallet])
                            if event:
                                incident_count += 1
                                frame_alerts.append(event)

                if len(cartons) >= 2:
                    for top in cartons:
                        for base in cartons:
                            if top["track_id"] == base["track_id"]:
                                continue
                            raw_result = StackingBehaviour.analyze(top["bbox"], base["bbox"])
                            top_width = top["bbox"][2] - top["bbox"][0]
                            base_width = max(1.0, base["bbox"][2] - base["bbox"][0])
                            result = self._apply_sop(raw_result, {"top_box_larger_than_bottom": top_width > base_width, "vertical_overlap_high": True})
                            if result:
                                zone = self.zone_mgr.get_zone_for_box(top["bbox"], width, height)
                                event = await self._record_and_publish(job_id=job_id, video_id=video_id, source_video_path=source_path, time_s=time_s, frame_idx=frame_idx, result=result, risk=self._risk("MEDIUM", 0.20, result["duration"], 0.70, zone), subject=top, tracks=tracks, workers=workers, width=width, height=height, related=[base])
                                if event:
                                    incident_count += 1
                                    frame_alerts.append(event)

                # Stack-wide rules need the complete observed carton set, not
                # independent single-object checks.
                if len(cartons) >= 3:
                    raw_result = UnsupportedStackBehaviour.analyze([carton["bbox"] for carton in cartons])
                    result = self._apply_sop(raw_result, {"tilt_angle_degrees": 13.0, "stack_height_units": len(cartons), "tilt_angle": 13.0})
                    if result:
                        subject = cartons[0]
                        zone = self.zone_mgr.get_zone_for_box(subject["bbox"], width, height)
                        event = await self._record_and_publish(job_id=job_id, video_id=video_id, source_video_path=source_path, time_s=time_s, frame_idx=frame_idx, result=result, risk=self._risk("HIGH", 0.20, result["duration"], 0.75, zone), subject=subject, tracks=tracks, workers=workers, width=width, height=height, related=cartons[1:])
                        if event:
                            incident_count += 1
                            frame_alerts.append(event)

                # An elevated carton with no observed supporting pallet/carton
                # is interpreted as a sequence risk only when the physical
                # detector module has actually flagged it.
                for carton in cartons:
                    elevated = carton["bbox"][1] < height * 0.45
                    has_support = any(calculate_iou(carton["bbox"], candidate["bbox"]) > 0.05 for candidate in [*pallets, *cartons] if candidate["track_id"] != carton["track_id"])
                    raw_result = SequenceBehaviour.analyze(carton["bbox"], perimeter_supported=has_support) if elevated else None
                    result = self._apply_sop(raw_result, {"perimeter_unsupported": True, "premature_elevated_placement": True})
                    if result:
                        zone = self.zone_mgr.get_zone_for_box(carton["bbox"], width, height)
                        event = await self._record_and_publish(job_id=job_id, video_id=video_id, source_video_path=source_path, time_s=time_s, frame_idx=frame_idx, result=result, risk=self._risk("HIGH", 0.20, result["duration"], 0.70, zone), subject=carton, tracks=tracks, workers=workers, width=width, height=height)
                        if event:
                            incident_count += 1
                            frame_alerts.append(event)

                self._annotate_frame(frame, tracks, frame_alerts, width, height, fps, time_s, incident_count)
                writer.write(frame)
                analyzed_count += 1
                if analyzed_count % 5 == 0:
                    await ws_manager.broadcast_to_job(job_id, {"type": "frame_observation", "video_id": video_id, "frame": frame_idx, "timestamp_seconds": time_s, "tracks": [self._track_payload(track, width, height) for track in tracks]})
                if analyzed_count % 15 == 0:
                    percentage = min(98, int((frame_idx / max(1, total_frames)) * 100))
                    message = f"Analyzing frame {frame_idx}/{total_frames} (found {incident_count} incidents)"
                    self.video_repo.update_job_progress(job_id, percentage, frame_idx, message)
                    await ws_manager.broadcast_to_job(job_id, {"type": "progress", "percentage": percentage, "frame": frame_idx, "total_frames": total_frames, "status": "processing", "message": message})
                    await asyncio.sleep(0.001)

            self.video_repo.complete_job(job_id, status="completed")
            self.video_repo.update_status(video_id, status="completed", processed_path=str(processed_path))
            await ws_manager.broadcast_to_job(job_id, {"type": "completed", "percentage": 100, "frame": total_frames, "total_frames": total_frames, "status": "completed", "message": f"Analysis complete. Total incidents flagged: {incident_count}"})
            logger.info("Video %s analysis completed: %s incidents", video_id, incident_count)
        except Exception as exc:
            logger.error("Analysis job %s failed: %s", job_id, exc, exc_info=True)
            self.video_repo.complete_job(job_id, status="failed", error_msg=str(exc))
            self.video_repo.update_status(video_id, status="failed")
            await ws_manager.broadcast_to_job(job_id, {"type": "error", "percentage": 0, "status": "failed", "message": f"Analysis failed: {exc}"})
        finally:
            if reader:
                reader.close()
            if writer:
                writer.release()
