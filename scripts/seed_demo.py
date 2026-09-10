import sys
import os
import math
from pathlib import Path

# Add backend to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / "backend"))

import cv2
import numpy as np
from app.core.config import UPLOADS_DIR, CLIPS_DIR, PROCESSED_DIR, THUMBNAILS_DIR
from app.database.database import SessionLocal, init_db
from app.database.models import Video, Event, AnalysisJob, Feedback, SopRule, Zone
from app.database.repositories.video_repo import VideoRepository
from app.database.repositories.incident_repo import IncidentRepository
from app.database.repositories.feedback_repo import FeedbackRepository
from app.risk.risk_engine import RiskEngine
from app.incidents.replay import generate_replay_clip

def generate_synthetic_warehouse_video(filepath: str, duration_sec: int = 24, fps: int = 30):
    """
    Generates a rich, visually clear synthetic warehouse CCTV video
    with floor demarcation lines, pallets, operator, cartons, and 5 distinct handling scenarios.
    """
    width, height = 1280, 720
    total_frames = duration_sec * fps

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(filepath, fourcc, float(fps), (width, height))

    print(f"Generating synthetic warehouse demo video ({total_frames} frames)...")

    # Static elements: warehouse floor, walls, zone outlines
    base_canvas = np.zeros((height, width, 3), dtype=np.uint8)
    # Concrete floor gradient
    for y in range(height):
        # Slightly dark industrial concrete
        val = int(35 + (y / height) * 20)
        base_canvas[y, :] = (val, val + 5, val + 8)

    # Floor yellow safety stripes / walkways
    cv2.line(base_canvas, (100, 150), (1200, 150), (0, 200, 220), 4) # Top aisle
    cv2.line(base_canvas, (460, 150), (460, 680), (0, 200, 220), 3)  # Bay divider
    cv2.line(base_canvas, (860, 150), (860, 680), (0, 200, 220), 3)  # Staging divider
    
    # Bay text labels on floor
    cv2.putText(base_canvas, "LOADING BAY 1", (130, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (80, 80, 80), 2)
    cv2.putText(base_canvas, "STAGING ZONE A", (510, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (80, 80, 80), 2)
    cv2.putText(base_canvas, "DISPATCH AREA", (920, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (80, 80, 80), 2)

    for frame_idx in range(total_frames):
        frame = base_canvas.copy()
        time_s = frame_idx / fps

        # Timestamp HUD
        mins = int(time_s // 60)
        secs = int(time_s % 60)
        millis = int((time_s % 1) * 100)
        time_str = f"CAM-04 [BAY-1/STAGING] | 2026-09-10 {mins:02d}:{secs:02d}.{millis:02d} | 30.0 FPS"
        cv2.putText(frame, time_str, (30, 45), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1, cv2.LINE_AA)

        # Draw stationary pallets
        # Pallet 1 in Bay 1
        cv2.rectangle(frame, (160, 480), (380, 530), (70, 95, 120), -1)
        cv2.rectangle(frame, (160, 480), (380, 530), (120, 150, 180), 2)
        cv2.putText(frame, "PALLET #1", (170, 510), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (220, 220, 220), 1)

        # Pallet 2 in Staging A
        cv2.rectangle(frame, (520, 480), (740, 530), (70, 95, 120), -1)
        cv2.rectangle(frame, (520, 480), (740, 530), (120, 150, 180), 2)
        cv2.putText(frame, "PALLET #2", (530, 510), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (220, 220, 220), 1)

        # SCENARIO 1: Drop/Throw (Frames 30 - 150, 1s - 5s)
        # Operator carrying carton #8, carton slips/drops at t=2.5s
        if time_s < 6.0:
            # Operator in Bay 1
            op_x = 260
            op_y = 350
            # Draw Operator
            cv2.rectangle(frame, (op_x - 30, op_y - 80), (op_x + 30, op_y + 80), (180, 120, 40), -1) # Blue overalls
            cv2.circle(frame, (op_x, op_y - 95), 20, (210, 180, 140), -1) # Head

            # Carton #8 position
            if time_s < 2.2:
                # Carried by operator
                c_x, c_y = op_x + 35, op_y - 10
            elif time_s < 3.0:
                # Dropping rapidly (acceleration downwards)
                dt_drop = (time_s - 2.2)
                c_x = op_x + 35 + int(dt_drop * 20)
                c_y = op_y - 10 + int(0.5 * 900 * (dt_drop ** 2)) # gravity drop
                c_y = min(c_y, 480 - 60) # hits floor near pallet
            else:
                # Stationary on floor
                c_x, c_y = op_x + 50, 480 - 60

            cv2.rectangle(frame, (c_x, c_y), (c_x + 80, c_y + 60), (40, 80, 150), -1) # Brown carton
            cv2.rectangle(frame, (c_x, c_y), (c_x + 80, c_y + 60), (90, 140, 220), 2)
            cv2.putText(frame, "CARTON #8", (c_x + 5, c_y + 35), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)

        # SCENARIO 2: Dragging Product (Frames 180 - 330, 6s - 11s)
        if 5.5 <= time_s < 12.0:
            drag_t = time_s - 6.0
            # Moving from x=200 to x=430 on floor
            drag_x = int(200 + drag_t * 40)
            drag_y = 480 - 60 # directly on floor

            # Operator dragging behind
            op_x = drag_x - 50
            op_y = 360
            cv2.rectangle(frame, (op_x - 30, op_y - 80), (op_x + 30, op_y + 80), (180, 120, 40), -1)
            cv2.circle(frame, (op_x, op_y - 95), 20, (210, 180, 140), -1)
            # Arm reaching down to box
            cv2.line(frame, (op_x, op_y), (drag_x, drag_y + 20), (210, 180, 140), 5)

            # Carton #11
            cv2.rectangle(frame, (drag_x, drag_y), (drag_x + 90, drag_y + 60), (35, 75, 145), -1)
            cv2.rectangle(frame, (drag_x, drag_y), (drag_x + 90, drag_y + 60), (80, 130, 210), 2)
            cv2.putText(frame, "CARTON #11", (drag_x + 5, drag_y + 35), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)

        # SCENARIO 3: Pallet Overhang (Frames 360 - 480, 12s - 16s)
        # Carton #17 sitting on Pallet #2 with 25% overhang over the right edge
        if time_s >= 11.0:
            # Pallet 2 top is y=480, right edge is x=740
            # Carton sits at x=640 to x=800 (overhang is from 740 to 800 -> 60px over 160px width = 37% overhang!)
            box_x1 = 640
            box_y1 = 480 - 70
            box_x2 = 800
            box_y2 = 480
            cv2.rectangle(frame, (box_x1, box_y1), (box_x2, box_y2), (45, 90, 160), -1)
            cv2.rectangle(frame, (box_x1, box_y1), (box_x2, box_y2), (0, 0, 255), 2) # Red border indicating overhang
            cv2.putText(frame, "CARTON #17 [OVERHANG]", (box_x1 + 5, box_y1 + 40), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

        # SCENARIO 4: Improper Staging in Walkway (Frames 480 - 600, 16s - 20s)
        # Carton #21 placed right in the central transit walkway (between Bay 1 and Staging A)
        if time_s >= 15.0:
            ws_x = 420
            ws_y = 560
            cv2.rectangle(frame, (ws_x, ws_y), (ws_x + 80, ws_y + 60), (50, 100, 175), -1)
            cv2.rectangle(frame, (ws_x, ws_y), (ws_x + 80, ws_y + 60), (0, 165, 255), 2)
            cv2.putText(frame, "CARTON #21", (ws_x + 5, ws_y + 35), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)

        # SCENARIO 5: Stacking Anomaly (Frames 600 - 720, 20s - 24s)
        # Large heavy carton #24 placed over small base carton #25
        if time_s >= 18.0:
            st_x = 980
            # Base small carton #25
            cv2.rectangle(frame, (st_x + 20, 520 - 50), (st_x + 90, 520), (40, 80, 150), -1)
            cv2.rectangle(frame, (st_x + 20, 520 - 50), (st_x + 90, 520), (100, 160, 230), 2)
            cv2.putText(frame, "CARTON #25", (st_x + 25, 520 - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255, 255, 255), 1)

            # Top oversized carton #24
            cv2.rectangle(frame, (st_x - 10, 520 - 120), (st_x + 120, 520 - 50), (30, 70, 140), -1)
            cv2.rectangle(frame, (st_x - 10, 520 - 120), (st_x + 120, 520 - 50), (0, 69, 255), 2)
            cv2.putText(frame, "CARTON #24 [UNSTABLE]", (st_x - 5, 520 - 80), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (255, 255, 255), 1)

        writer.write(frame)

    writer.release()
    print(f"Demo video created: {filepath}")

def seed():
    init_db()
    db = SessionLocal()

    video_repo = VideoRepository(db)
    incident_repo = IncidentRepository(db)
    feedback_repo = FeedbackRepository(db)

    # 1. Generate demo video file
    demo_filename = "demo_warehouse_handling.mp4"
    demo_path = str(UPLOADS_DIR / demo_filename)
    generate_synthetic_warehouse_video(demo_path, duration_sec=24, fps=30)

    # Generate thumbnail
    thumb_path = str(THUMBNAILS_DIR / "thumb_demo_warehouse_handling.jpg")
    cap = cv2.VideoCapture(demo_path)
    cap.set(cv2.CAP_PROP_POS_FRAMES, 75)
    ret, frame = cap.read()
    if ret:
        cv2.imwrite(thumb_path, frame)
    cap.release()

    # 2. Check if video record exists
    existing_video = db.query(Video).filter(Video.filename == demo_filename).first()
    if existing_video:
        video = existing_video
    else:
        video = video_repo.create(
            filename=demo_filename,
            original_name="Warehouse_CCTV_Main_Shift_Feed.mp4",
            file_path=demo_path,
            thumbnail_path=thumb_path,
            duration=24.0,
            fps=30.0,
            width=1280,
            height=720,
            frame_count=720,
            source_type="upload",
            status="completed"
        )

    # Clean old events for demo video
    db.query(Event).filter(Event.video_id == video.id).delete()
    db.commit()

    # 3. Create the 5 Showcase Incidents with rich Factor Breakdowns & Evidence
    showcase_events = [
        {
            "timestamp": "00:03",
            "timestamp_seconds": 3.0,
            "behaviour": "DROP_PRODUCT",
            "behaviour_name": "Possible Product Drop",
            "object_id": "Carton #8",
            "risk_score": 86,
            "risk_level": "HIGH",
            "zone": "Loading Bay 1",
            "evidence": [
                "Operator-product separation detected",
                "Rapid downward velocity peak (78.4 px/s)",
                "Sudden kinetic arrest upon floor contact",
                "Object stationary post-impact"
            ],
            "recommendation": "Inspect carton interior contents and corner integrity; review gentle staging SOP with operator.",
            "duration": 1.5,
            "severity": "HIGH",
            "factors": [
                {"name": "Behaviour severity", "contribution": 30, "description": "Baseline weight for sudden drop"},
                {"name": "Motion impact", "contribution": 18, "description": "High downward kinetic transfer"},
                {"name": "Duration", "contribution": 6, "description": "Rapid deceleration event"},
                {"name": "Spatial configuration", "contribution": 12, "description": "Direct concrete floor impact"},
                {"name": "Repetition", "contribution": 10, "description": "Multiple items unbuffered"},
                {"name": "Location context", "contribution": 10, "description": "Active Loading Bay 1"}
            ]
        },
        {
            "timestamp": "00:08",
            "timestamp_seconds": 8.0,
            "behaviour": "DRAG_PRODUCT",
            "behaviour_name": "Dragging Product",
            "object_id": "Carton #11",
            "risk_score": 64,
            "risk_level": "HIGH",
            "zone": "Loading Bay 1",
            "evidence": [
                "Object bottom maintained continuous floor contact",
                "Sustained horizontal friction drag (38.2 px/s lateral motion)",
                "Lack of mobile material handling equipment (trolley / pallet jack)",
                "Manual operator pulling action identified"
            ],
            "recommendation": "Deploy hand pallet truck or mobile trolley to eliminate floor friction and package base tears.",
            "duration": 2.4,
            "severity": "MEDIUM",
            "factors": [
                {"name": "Behaviour severity", "contribution": 18, "description": "Friction abrasion hazard"},
                {"name": "Motion impact", "contribution": 11, "description": "Continuous lateral dragging motion"},
                {"name": "Duration", "contribution": 8, "description": "2.4s continuous dragging exposure"},
                {"name": "Spatial configuration", "contribution": 9, "description": "Zero ground clearance"},
                {"name": "Repetition", "contribution": 8, "description": "Recurring habit observed"},
                {"name": "Location context", "contribution": 10, "description": "Loading Bay 1 walkway"}
            ]
        },
        {
            "timestamp": "00:13",
            "timestamp_seconds": 13.0,
            "behaviour": "PALLET_OVERHANG",
            "behaviour_name": "Pallet Overhang",
            "object_id": "Carton #17",
            "risk_score": 78,
            "risk_level": "HIGH",
            "zone": "Staging Zone A",
            "evidence": [
                "Base support ratio calculated at 63% (below required 90% threshold)",
                "Carton overhangs pallet perimeter by 60px",
                "Asymmetrical gravitational load induces severe corner crush risk"
            ],
            "recommendation": "Reposition carton flush with pallet boundary before forklift transit to eliminate corner crushing.",
            "duration": 3.0,
            "severity": "HIGH",
            "factors": [
                {"name": "Behaviour severity", "contribution": 30, "description": "Structural failure hazard"},
                {"name": "Motion impact", "contribution": 4, "description": "Static staging posture"},
                {"name": "Duration", "contribution": 10, "description": "Prolonged unstable staging"},
                {"name": "Spatial configuration", "contribution": 15, "description": "37% perimeter cantilever overhang"},
                {"name": "Repetition", "contribution": 10, "description": "Observed on pallet 2"},
                {"name": "Location context", "contribution": 9, "description": "Staging Zone A sorting area"}
            ]
        },
        {
            "timestamp": "00:17",
            "timestamp_seconds": 17.0,
            "behaviour": "IMPROPER_STAGING",
            "behaviour_name": "Improper Staging",
            "object_id": "Carton #21",
            "risk_score": 52,
            "risk_level": "MEDIUM",
            "zone": "General Walkway",
            "evidence": [
                "Product placed in unauthorized zone: 'General Walkway'",
                "Expected designated staging area: 'Staging Zone A'",
                "Obstruction detected in active forklift/personnel corridor",
                "Violation of warehouse line demarcation"
            ],
            "recommendation": "Relocate carton to designated staging lane to prevent forklift collisions and maintain clear egress.",
            "duration": 4.0,
            "severity": "MEDIUM",
            "factors": [
                {"name": "Behaviour severity", "contribution": 18, "description": "Obstruction risk"},
                {"name": "Motion impact", "contribution": 2, "description": "Stationary item"},
                {"name": "Duration", "contribution": 10, "description": "Long-term obstruction"},
                {"name": "Spatial configuration", "contribution": 8, "description": "Aisle encroachment"},
                {"name": "Repetition", "contribution": 5, "description": "Isolated staging deviation"},
                {"name": "Location context", "contribution": 9, "description": "High-traffic transit walkway"}
            ]
        },
        {
            "timestamp": "00:21",
            "timestamp_seconds": 21.0,
            "behaviour": "STACK_ORDER",
            "behaviour_name": "Incorrect Stack Order",
            "object_id": "Carton #24",
            "risk_score": 72,
            "risk_level": "HIGH",
            "zone": "Dispatch Area",
            "evidence": [
                "Top unit horizontal footprint exceeds base support unit by 85%",
                "Inverse pyramid mass distribution detected in vertical column",
                "Base carton subjected to excessive compressive load"
            ],
            "recommendation": "Restack column with broader, heavier cartons at the bottom layer and lighter units on top.",
            "duration": 3.0,
            "severity": "HIGH",
            "factors": [
                {"name": "Behaviour severity", "contribution": 30, "description": "Compressive collapse hazard"},
                {"name": "Motion impact", "contribution": 5, "description": "Stack wobbling detected"},
                {"name": "Duration", "contribution": 8, "description": "Sustained stacked load"},
                {"name": "Spatial configuration", "contribution": 14, "description": "Overhung inverse tier ratio"},
                {"name": "Repetition", "contribution": 7, "description": "Column tier 2"},
                {"name": "Location context", "contribution": 8, "description": "Dispatch staging pad"}
            ]
        }
    ]

    created_events = []
    for se in showcase_events:
        evt = incident_repo.create(
            video_id=video.id,
            timestamp=se["timestamp"],
            timestamp_seconds=se["timestamp_seconds"],
            behaviour=se["behaviour"],
            behaviour_name=se["behaviour_name"],
            object_id=se["object_id"],
            risk_score=se["risk_score"],
            risk_level=se["risk_level"],
            zone=se["zone"],
            evidence_json=se["evidence"],
            recommendation=se["recommendation"],
            confidence=0.91,
            severity=se["severity"],
            duration=se["duration"],
            frame_start=int((se["timestamp_seconds"] - 3) * 30),
            frame_end=int((se["timestamp_seconds"] + 3) * 30),
            factors_json=se["factors"],
            sop_rule_code=se["behaviour"],
            review_status="UNREVIEWED"
        )
        created_events.append(evt)

        # Generate replay clip for each event
        clip = generate_replay_clip(
            source_video_path=demo_path,
            event_id=evt.id,
            timestamp_seconds=se["timestamp_seconds"],
            duration_seconds=se["duration"]
        )
        if clip:
            evt.clip_path = clip
            db.commit()

    # 4. Seed initial user feedback
    feedback_repo.create(
        event_id=created_events[0].id,
        feedback_type="correct",
        comment="Accurately captured carton slip and drop in Bay 1 before floor contact.",
        user_id="Warehouse Supervisor"
    )
    feedback_repo.create(
        event_id=created_events[1].id,
        feedback_type="correct",
        comment="Handler pulled carton without dolly. Hand pallet truck was issued.",
        user_id="Safety Officer"
    )

    print(f"Successfully seeded demo data: Video #{video.id}, {len(created_events)} showcase incidents with replay clips & feedback!")
    db.close()

if __name__ == "__main__":
    seed()
