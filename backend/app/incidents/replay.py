from pathlib import Path
from typing import Optional
import cv2
from app.core.config import CLIPS_DIR, settings
from app.core.logging import logger

def generate_replay_clip(
    source_video_path: str,
    event_id: int,
    timestamp_seconds: float,
    duration_seconds: float = 2.0,
    pre_seconds: Optional[float] = None,
    post_seconds: Optional[float] = None
) -> Optional[str]:
    """
    Extracts a replay clip from source video around an incident timestamp.
    Default: (timestamp - 3s) to (timestamp + duration + 3s).
    Saved as MP4 in storage/clips/replay_event_{event_id}.mp4
    """
    pre = pre_seconds if pre_seconds is not None else settings.CLIP_PRE_SECONDS
    post = post_seconds if post_seconds is not None else settings.CLIP_POST_SECONDS

    clip_filename = f"replay_event_{event_id}.mp4"
    out_clip_path = CLIPS_DIR / clip_filename

    if out_clip_path.exists() and out_clip_path.stat().st_size > 1000:
        return str(out_clip_path)

    cap = cv2.VideoCapture(source_video_path)
    if not cap.isOpened():
        logger.error(f"Cannot open video for replay clip extraction: {source_video_path}")
        return None

    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    start_sec = max(0.0, timestamp_seconds - pre)
    end_sec = min(total_frames / fps, timestamp_seconds + duration_seconds + post)

    start_frame = int(start_sec * fps)
    end_frame = int(end_sec * fps)

    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

    # Use avc1 or mp4v fourcc
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(out_clip_path), fourcc, fps, (width, height))

    curr = start_frame
    while curr <= end_frame and cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        # Stamp replay banner on clip
        cv2.putText(
            frame,
            f"CARG OIQ REPLAY - INCIDENT #{event_id} [{round(curr / fps, 1)}s]",
            (20, 35),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 0, 255),
            2,
            cv2.LINE_AA
        )
        writer.write(frame)
        curr += 1

    cap.release()
    writer.release()
    logger.info(f"Replay clip generated: {out_clip_path} (frames {start_frame} to {end_frame})")
    return str(out_clip_path)
