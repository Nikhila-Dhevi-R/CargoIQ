from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field

class VideoBase(BaseModel):
    filename: str
    original_name: str
    duration: float = 0.0
    fps: float = 30.0
    width: int = 1280
    height: int = 720
    frame_count: int = 0
    source_type: str = "upload"
    source_url: Optional[str] = None
    status: str = "ready"

class VideoCreate(BaseModel):
    url: Optional[str] = None

class VideoResponse(VideoBase):
    id: int
    file_path: str
    processed_path: Optional[str] = None
    thumbnail_path: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class AnalysisJobResponse(BaseModel):
    job_id: str
    video_id: int
    status: str
    progress: int
    current_frame: int
    total_frames: int
    step_description: str
    error_message: Optional[str] = None
