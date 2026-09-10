# CargoIQ

## See the Risk. Stop the Damage.

CargoIQ turns warehouse video into explainable operational intelligence. It detects observed cargo-handling behaviours, evaluates configurable SOP rules, calculates a deterministic risk score, and gives supervisors evidence-backed preventive actions. It identifies **potential operational risk**, not confirmed physical product damage.

## What is included

- React + TypeScript command center with video ingestion, analysis progress, incident review, replay, analytics, feedback, SOP library, and assistant.
- FastAPI + SQLite service with asynchronous analysis jobs and WebSocket updates.
- YOLO object detection, persistent tracking, temporal object memory, scene relationships, configurable warehouse zones, SOP-as-code, and deterministic risk factors.
- All ten CargoIQ behaviour modules, with five showcase scenarios: possible drop, dragging, pallet overhang, improper staging, and incorrect stacking.
- Evidence clips and processed-video playback generated from real input video.

## Local setup

CargoIQ requires Python 3.11 or 3.12, Node.js 18+, and FFmpeg. Python 3.14 is not currently a dependable target for the Ultralytics/Torch stack.

```powershell
Copy-Item .env.example .env
py -3.11 -m venv backend\.venv
& .\backend\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r backend\requirements.txt
```

Start the backend in one terminal:

```powershell
& .\backend\.venv\Scripts\Activate.ps1
Set-Location backend
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Start the frontend in another terminal:

```powershell
Set-Location frontend
npm install
npm run dev
```

Open `http://localhost:5173`. The API health check is available at `http://127.0.0.1:8000/api/system/health`.

## Demo mode

After the backend dependencies are installed, generate the local demo asset and its database records with:

```powershell
& .\backend\.venv\Scripts\python.exe scripts\seed_demo.py
```

The seed is intentionally local-only: generated videos, replay clips, thumbnails, databases, virtual environments, and build output are ignored by Git.

## Safety and responsible AI

- No facial recognition or employee identity profiling.
- A model failure produces no detections and is clearly shown in system health.
- Risk scores come from the deterministic risk engine, never from the LLM.
- The assistant is grounded in recorded incident/SOP data and states when evidence is unavailable.
- Supervisor review and feedback are recorded against each incident.

## Verification

```powershell
Set-Location frontend
npm run build

Set-Location ..\backend
& .\.venv\Scripts\python.exe -m pytest -q tests
```
