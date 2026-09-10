from pathlib import Path
from typing import Optional
import cv2
from app.core.config import THUMBNAILS_DIR

def generate_thumbnail(video_path: str, thumbnail_name: str) -> Optional[str]:
    """Extracts first or middle frame as thumbnail."""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return None

    # Read at frame 15
    cap.set(cv2.CAP_PROP_POS_FRAMES, 15)
    ret, frame = cap.read()
    if not ret:
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        ret, frame = cap.read()

    cap.release()

    if not ret or frame is None:
        return None

    out_path = THUMBNAILS_DIR / f"{thumbnail_name}.jpg"
    cv2.imwrite(str(out_path), frame)
    return str(out_path)
