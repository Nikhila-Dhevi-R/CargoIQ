from typing import List, Dict, Any, Optional
from pathlib import Path
import os
import numpy as np
from app.core.config import BASE_DIR, settings
from app.core.logging import logger
from app.perception.classes import CLASS_MAPPING, TARGET_CLASSES

# Keep Ultralytics runtime data local to CargoIQ. Some managed Windows profiles
# block writes to AppData/Roaming, which otherwise prevents the model from
# importing even when its package and weights are installed.
ULTRALYTICS_CONFIG_ROOT = BASE_DIR / ".ultralytics"
(ULTRALYTICS_CONFIG_ROOT / "Ultralytics").mkdir(parents=True, exist_ok=True)
os.environ["YOLO_CONFIG_DIR"] = str(ULTRALYTICS_CONFIG_ROOT)

class WarehouseDetector:
    def __init__(self, model_name: Optional[str] = None, conf_thresh: Optional[float] = None):
        self.conf_thresh = conf_thresh or settings.CONFIDENCE_THRESHOLD
        self.model_name = model_name or settings.YOLO_MODEL
        self.model = None
        self.model_error: Optional[str] = None
        self._load_model()

    def _load_model(self):
        try:
            from ultralytics import YOLO
            configured = Path(self.model_name)
            resolved_name = configured
            if not configured.is_absolute() and not configured.is_file() and (BASE_DIR / configured).is_file():
                resolved_name = BASE_DIR / configured
            logger.info("Loading YOLO model: %s", resolved_name)
            self.model = YOLO(str(resolved_name))
            logger.info("YOLO model successfully loaded.")
        except Exception as e:
            self.model_error = str(e)
            logger.warning("Unable to load YOLO model '%s': %s", self.model_name, e)
            self.model = None

    @property
    def is_available(self) -> bool:
        return self.model is not None

    @classmethod
    def configured_model_exists(cls, model_name: Optional[str] = None) -> bool:
        """Return whether a local configured model is present without loading it."""
        configured = Path(model_name or settings.YOLO_MODEL)
        if configured.is_absolute():
            return configured.is_file()
        return configured.is_file() or (BASE_DIR / configured).is_file()

    def detect(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """
        Runs object detection on frame.
        Returns list of detections with format:
        {
            "class_name": str,
            "confidence": float,
            "bbox": [x1, y1, x2, y2],
            "center": [x, y]
        }
        """
        h, w = frame.shape[:2]
        detections = []

        if self.model is not None:
            try:
                results = self.model.predict(frame, conf=self.conf_thresh, verbose=False)
                for r in results:
                    boxes = r.boxes
                    if boxes is None:
                        continue
                    for box in boxes:
                        cls_id = int(box.cls[0].item())
                        raw_name = r.names.get(cls_id, "unknown")
                        cname = CLASS_MAPPING.get(raw_name, raw_name)
                        conf = float(box.conf[0].item())
                        xyxy = [float(c) for c in box.xyxy[0].tolist()]
                        cx = (xyxy[0] + xyxy[2]) / 2.0
                        cy = (xyxy[1] + xyxy[3]) / 2.0

                        detections.append({
                            "class_name": cname,
                            "confidence": round(conf, 2),
                            "bbox": xyxy,
                            "center": [round(cx, 1), round(cy, 1)]
                        })
                return detections
            except Exception as e:
                self.model_error = str(e)
                logger.error("YOLO inference failed; no detections will be emitted: %s", e)
                return []

        # CargoIQ must never label contours as people, cartons, or pallets when
        # the configured model is unavailable. An empty result is honest and is
        # surfaced through job/system status for the supervisor to act on.
        return []
