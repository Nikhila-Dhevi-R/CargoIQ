from typing import List, Optional
from sqlalchemy.orm import Session
from app.database.models import Video, AnalysisJob

class VideoRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, **kwargs) -> Video:
        video = Video(**kwargs)
        self.db.add(video)
        self.db.commit()
        self.db.refresh(video)
        return video

    def get_by_id(self, video_id: int) -> Optional[Video]:
        return self.db.query(Video).filter(Video.id == video_id).first()

    def get_all(self, limit: int = 100) -> List[Video]:
        return self.db.query(Video).order_by(Video.created_at.desc()).limit(limit).all()

    def update_status(self, video_id: int, status: str, processed_path: Optional[str] = None):
        video = self.get_by_id(video_id)
        if video:
            video.status = status
            if processed_path:
                video.processed_path = processed_path
            self.db.commit()
            self.db.refresh(video)
        return video

    def create_job(self, job_id: str, video_id: int, total_frames: int = 0) -> AnalysisJob:
        job = AnalysisJob(
            id=job_id,
            video_id=video_id,
            status="queued",
            progress=0,
            current_frame=0,
            total_frames=total_frames,
            step_description="Queued for analysis"
        )
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job

    def get_job(self, job_id: str) -> Optional[AnalysisJob]:
        return self.db.query(AnalysisJob).filter(AnalysisJob.id == job_id).first()

    def update_job_progress(self, job_id: str, progress: int, current_frame: int, step_desc: str, status: str = "processing"):
        job = self.get_job(job_id)
        if job:
            job.progress = progress
            job.current_frame = current_frame
            job.step_description = step_desc
            job.status = status
            self.db.commit()
        return job

    def complete_job(self, job_id: str, status: str = "completed", error_msg: Optional[str] = None):
        job = self.get_job(job_id)
        if job:
            job.status = status
            job.progress = 100 if status == "completed" else job.progress
            if error_msg:
                job.error_message = error_msg
            self.db.commit()
        return job
