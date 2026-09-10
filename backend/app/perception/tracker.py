from typing import List, Dict, Any, Tuple
from app.intelligence.geometry import calculate_iou, centroid, euclidean_distance

class TrackedEntity:
    def __init__(self, track_id: int, class_name: str, bbox: List[float], conf: float = 0.85):
        self.track_id = track_id
        self.class_name = class_name
        self.bbox = bbox
        self.confidence = conf
        self.missed_frames = 0
        self.total_frames = 1
        self.label = f"Operator #{track_id}" if class_name == "person" else f"{class_name.capitalize()} #{track_id}"

    def update(self, bbox: List[float], conf: float):
        self.bbox = bbox
        self.confidence = conf
        self.missed_frames = 0
        self.total_frames += 1

class WarehouseTracker:
    """
    Persistent ByteTrack-style multi-object tracker matching detections
    across successive frames using IoU and centroid proximity.
    """
    def __init__(self, max_missed: int = 15, iou_thresh: float = 0.25):
        self.max_missed = max_missed
        self.iou_thresh = iou_thresh
        self.next_track_id = 1
        self.tracks: Dict[int, TrackedEntity] = {}

    def update(self, detections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Takes raw detections and returns tracked entities with persistent IDs.
        """
        matched_tracks = set()
        matched_dets = set()

        track_items = list(self.tracks.items())

        # First pass: IoU matching for same class
        for det_idx, det in enumerate(detections):
            best_iou = 0.0
            best_tid = None

            for tid, track in track_items:
                if tid in matched_tracks:
                    continue
                if track.class_name != det["class_name"]:
                    continue

                iou = calculate_iou(det["bbox"], track.bbox)
                if iou > best_iou and iou >= self.iou_thresh:
                    best_iou = iou
                    best_tid = tid

            if best_tid is not None:
                self.tracks[best_tid].update(det["bbox"], det["confidence"])
                matched_tracks.add(best_tid)
                matched_dets.add(det_idx)

        # Second pass: Centroid proximity matching for remaining
        for det_idx, det in enumerate(detections):
            if det_idx in matched_dets:
                continue
            det_cx, det_cy = centroid(det["bbox"])
            best_dist = 120.0
            best_tid = None

            for tid, track in track_items:
                if tid in matched_tracks:
                    continue
                if track.class_name != det["class_name"]:
                    continue

                t_cx, t_cy = centroid(track.bbox)
                dist = euclidean_distance((det_cx, det_cy), (t_cx, t_cy))
                if dist < best_dist:
                    best_dist = dist
                    best_tid = tid

            if best_tid is not None:
                self.tracks[best_tid].update(det["bbox"], det["confidence"])
                matched_tracks.add(best_tid)
                matched_dets.add(det_idx)

        # Create new tracks for unmatched detections
        for det_idx, det in enumerate(detections):
            if det_idx not in matched_dets:
                tid = self.next_track_id
                self.next_track_id += 1
                self.tracks[tid] = TrackedEntity(
                    track_id=tid,
                    class_name=det["class_name"],
                    bbox=det["bbox"],
                    conf=det["confidence"]
                )

        # Age unmatched existing tracks
        to_delete = []
        for tid, track in self.tracks.items():
            if tid not in matched_tracks:
                track.missed_frames += 1
                if track.missed_frames > self.max_missed:
                    to_delete.append(tid)

        for tid in to_delete:
            del self.tracks[tid]

        # Prepare output
        results = []
        for tid, track in self.tracks.items():
            cx, cy = centroid(track.bbox)
            results.append({
                "track_id": track.track_id,
                "class_name": track.class_name,
                "label": track.label,
                "bbox": track.bbox,
                "center": [round(cx, 1), round(cy, 1)],
                "confidence": track.confidence,
                "total_frames": track.total_frames
            })
        return results

    def reset(self):
        self.tracks.clear()
        self.next_track_id = 1
