import time
from collections import deque
from typing import Dict, List, Any, Optional, Tuple
from app.intelligence.geometry import centroid, euclidean_distance

class TrackState:
    STATIONARY = "stationary"
    PICKED = "picked"
    CARRIED = "carried"
    RELEASED = "released"
    DROPPING = "dropping"
    DRAGGING = "dragging"
    IMPACT = "impact"

class ObjectHistory:
    def __init__(self, track_id: int, class_name: str, maxlen: int = 150):
        self.track_id = track_id
        self.class_name = class_name
        self.history: deque = deque(maxlen=maxlen) # entries: dict(frame, time_s, bbox, centroid, vx, vy, state)
        self.state_sequence: List[str] = [TrackState.STATIONARY]
        self.current_state = TrackState.STATIONARY
        self.last_near_person_id: Optional[int] = None
        self.last_near_person_time: float = -1.0

    def update(self, frame_idx: int, time_s: float, bbox: List[float], near_person_id: Optional[int] = None):
        cx, cy = centroid(bbox)
        vx, vy = 0.0, 0.0
        dt = 1.0 / 30.0

        if self.history:
            prev = self.history[-1]
            dt = max(0.001, time_s - prev["time_s"])
            vx = (cx - prev["cx"]) / dt
            vy = (cy - prev["cy"]) / dt

        if near_person_id is not None:
            self.last_near_person_id = near_person_id
            self.last_near_person_time = time_s

        speed = (vx**2 + vy**2)**0.5

        # Infer basic state
        prev_state = self.current_state
        if near_person_id is not None and speed > 15.0:
            new_state = TrackState.CARRIED
        elif self.last_near_person_time > 0 and (time_s - self.last_near_person_time < 0.5) and vy > 80.0:
            new_state = TrackState.DROPPING
        elif speed < 5.0:
            new_state = TrackState.STATIONARY
        else:
            new_state = prev_state

        if new_state != prev_state:
            self.current_state = new_state
            self.state_sequence.append(new_state)

        record = {
            "frame": frame_idx,
            "time_s": time_s,
            "bbox": bbox,
            "cx": cx,
            "cy": cy,
            "vx": vx,
            "vy": vy,
            "speed": speed,
            "near_person_id": near_person_id,
            "state": self.current_state
        }
        self.history.append(record)

    def get_trajectory(self) -> List[Tuple[float, float]]:
        return [(h["cx"], h["cy"]) for h in self.history]

    def get_recent_frames(self, n: int = 15) -> List[Dict[str, Any]]:
        return list(self.history)[-n:]

class ObjectMemory:
    def __init__(self):
        self.tracks: Dict[int, ObjectHistory] = {}

    def update_track(self, track_id: int, class_name: str, frame_idx: int, time_s: float, bbox: List[float], near_person_id: Optional[int] = None) -> ObjectHistory:
        if track_id not in self.tracks:
            self.tracks[track_id] = ObjectHistory(track_id, class_name)
        obj = self.tracks[track_id]
        obj.update(frame_idx, time_s, bbox, near_person_id)
        return obj

    def get_track(self, track_id: int) -> Optional[ObjectHistory]:
        return self.tracks.get(track_id)

    def clear(self):
        self.tracks.clear()
