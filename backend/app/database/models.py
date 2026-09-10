import datetime
from sqlalchemy import Column, Integer, String, Float, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.database import Base

class Video(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    filename = Column(String(255), nullable=False)
    original_name = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    processed_path = Column(String(512), nullable=True)
    thumbnail_path = Column(String(512), nullable=True)
    duration = Column(Float, default=0.0)
    fps = Column(Float, default=30.0)
    width = Column(Integer, default=1280)
    height = Column(Integer, default=720)
    frame_count = Column(Integer, default=0)
    source_type = Column(String(50), default="upload") # upload or url
    source_url = Column(String(512), nullable=True)
    status = Column(String(50), default="ready") # ready, processing, completed, failed
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    events = relationship("Event", back_populates="video", cascade="all, delete-orphan")
    analysis_jobs = relationship("AnalysisJob", back_populates="video", cascade="all, delete-orphan")
    tracked_objects = relationship("TrackedObject", back_populates="video", cascade="all, delete-orphan")


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    video_id = Column(Integer, ForeignKey("videos.id"), nullable=False, index=True)
    timestamp = Column(String(50), nullable=False) # "00:42"
    timestamp_seconds = Column(Float, default=0.0)
    behaviour = Column(String(100), nullable=False, index=True) # e.g. "DROP", "DRAG", "PALLET_OVERHANG"
    behaviour_name = Column(String(200), nullable=False) # e.g. "Possible Product Drop"
    object_id = Column(String(100), nullable=False) # e.g. "Carton #8"
    risk_score = Column(Integer, default=0) # 0 - 100
    risk_level = Column(String(50), default="MEDIUM", index=True) # SAFE, LOW, MEDIUM, HIGH, CRITICAL
    zone = Column(String(100), default="General Area")
    evidence_json = Column(Text, default="[]") # JSON list of string evidence
    recommendation = Column(Text, default="")
    clip_path = Column(String(512), nullable=True)
    review_status = Column(String(50), default="UNREVIEWED", index=True) # UNREVIEWED, REVIEWED, DISMISSED
    review_notes = Column(Text, nullable=True)
    confidence = Column(Float, default=0.85)
    severity = Column(String(50), default="HIGH")
    duration = Column(Float, default=1.0) # seconds
    frame_start = Column(Integer, default=0)
    frame_end = Column(Integer, default=0)
    factors_json = Column(Text, default="[]") # Risk factor breakdown
    sop_rule_code = Column(String(100), nullable=True)
    metadata_json = Column(Text, default="{}")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    video = relationship("Video", back_populates="events")
    feedback = relationship("Feedback", back_populates="event", cascade="all, delete-orphan")


class TrackedObject(Base):
    __tablename__ = "tracked_objects"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    video_id = Column(Integer, ForeignKey("videos.id"), nullable=False)
    track_id = Column(Integer, nullable=False)
    class_name = Column(String(100), nullable=False) # person, carton, pallet, etc.
    label = Column(String(100), nullable=False) # "Carton #8", "Operator #2"
    first_seen = Column(Float, default=0.0)
    last_seen = Column(Float, default=0.0)
    trajectory_json = Column(Text, default="[]")
    zone_history_json = Column(Text, default="[]")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    video = relationship("Video", back_populates="tracked_objects")


class Zone(Base):
    __tablename__ = "zones"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    polygon_json = Column(Text, nullable=False) # [[x1, y1], [x2, y2], ...] normalized 0-1
    description = Column(String(255), default="")
    color = Column(String(50), default="#3b82f6")
    is_active = Column(Boolean, default=True)


class SopRule(Base):
    __tablename__ = "sop_rules"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    code = Column(String(100), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    severity = Column(String(50), default="HIGH")
    conditions_json = Column(Text, default="{}")
    recommendation = Column(Text, default="")
    description = Column(Text, default="")
    is_active = Column(Boolean, default=True)


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    feedback_type = Column(String(50), nullable=False) # "correct", "incorrect", "unsure"
    comment = Column(Text, nullable=True)
    user_id = Column(String(100), default="Supervisor")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    event = relationship("Event", back_populates="feedback")


class AnalysisJob(Base):
    __tablename__ = "analysis_jobs"

    id = Column(String(100), primary_key=True, index=True)
    video_id = Column(Integer, ForeignKey("videos.id"), nullable=False)
    status = Column(String(50), default="queued") # queued, processing, completed, failed
    progress = Column(Integer, default=0) # 0 to 100
    current_frame = Column(Integer, default=0)
    total_frames = Column(Integer, default=0)
    step_description = Column(String(255), default="Initializing...")
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    video = relationship("Video", back_populates="analysis_jobs")
