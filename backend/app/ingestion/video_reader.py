import cv2
from typing import Generator, Tuple, Optional
import numpy as np

class VideoReader:
    """Frame-by-frame generator to process video without loading full video into RAM."""
    def __init__(self, video_path: str):
        self.video_path = video_path
        self.cap = cv2.VideoCapture(video_path)
        if not self.cap.isOpened():
            raise ValueError(f"Failed to open video source: {video_path}")

        self.fps = self.cap.get(cv2.CAP_PROP_FPS) or 30.0
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    def frames(self, step: int = 1) -> Generator[Tuple[int, float, np.ndarray], None, None]:
        """
        Yields (frame_idx, timestamp_seconds, frame_bgr)
        """
        frame_idx = 0
        while self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                break
            if frame_idx % step == 0:
                time_s = frame_idx / self.fps
                yield frame_idx, time_s, frame
            frame_idx += 1

    def close(self):
        if self.cap and self.cap.isOpened():
            self.cap.release()
