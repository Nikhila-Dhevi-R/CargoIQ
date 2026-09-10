# CargoIQ integration status

Audit date: 2026-09-10

The repository already provides a React/Vite supervisor interface, FastAPI API,
SQLite persistence, asynchronous video processing, YOLO integration, a
ByteTrack-style tracker, event replay, WebSockets, SOP rules, a deterministic
risk engine, analytics, feedback, and a grounded assistant/MCP layer. The
original product name remains **KAVACH AI** in several user-facing and runtime
locations; CargoIQ is the current product identity.

| Feature | Existing Status | Current Implementation | Missing Work | Priority |
| --- | --- | --- | --- | --- |
| Product identity | Partial | Working app is branded KAVACH AI | Rename user-facing/runtime branding to CargoIQ | High |
| React command center | Implemented | Vite, React, Router, React Query, responsive pages | Remove stale wording and disconnected controls | High |
| FastAPI + SQLite | Implemented | Routers, SQLAlchemy models, repositories, standard response envelopes | Add safer error envelopes and settings persistence | High |
| Video upload/metadata | Implemented | Upload, URL download, metadata, thumbnails, streaming reader | Harden validation and expose useful ingestion errors | High |
| Async analysis + WebSocket | Implemented | Background job, progress persistence, WebSocket events | Include full progress/error fields in status response | High |
| YOLO detection | Partial | Ultralytics detection and normalized output | Remove contour fallback that labels objects as detections; report model availability honestly | Critical |
| Tracking | Partial | IoU/centroid persistent tracker | ByteTrack-compatible tracking is custom, not the ByteTrack library; persist tracked-object summaries | Medium |
| Object memory/geometry/zones | Partial | Temporal motion state, IoU, support ratio, polygons | Strengthen scene relationships and configurable thresholds | Medium |
| Ten behaviour modules | Partial | All ten modules/rules exist | Analysis currently invokes only five modules and bypasses declarative SOP evaluation | Critical |
| SOP-as-code | Partial | YAML loader, rule engine, DB seed and UI cards | Evaluate rule contexts in pipeline and honour enabled state | Critical |
| Deterministic risk | Implemented | Six weighted factor contributions and levels | Add tests for factor boundaries | Medium |
| Events, evidence, replay | Implemented | Persisted incidents, replay clips, frontend player/review/feedback | Replace unsafe `eval` JSON fallback; surface replay failures clearly | Critical |
| Analytics | Partial | Backend-derived KPIs, behaviours, zones, trends | Add backend heatmap endpoint and zero-state handling | Medium |
| Assistant + MCP | Partial | Ollama client, context builder, structured MCP queries | Rename branding; ensure no template claims beyond recorded evidence | High |
| System health | Partial | DB, Ollama, FFmpeg checks | Check actual loaded/available vision model rather than reporting it as loaded | Critical |
| Settings | Partial | Health/status and zones shown | Confidence slider is local-only; add read/write API-backed settings | High |
| Tests | Partial | Geometry, risk, SOP loading, overhang smoke tests | Add behaviour, repository, API, review and safety tests | High |
| Environment/deployment | Partial | Windows launch script and requirements | Add `.env.example`; eliminate committed virtual environments and generated media | Critical |

## Audit findings requiring immediate remediation

1. `backend/venv` is tracked in Git (about 29,000 files), and its interpreter
   is machine-specific and cannot launch after moving the checkout.
2. The detector falls back to contour heuristics that fabricate `person`,
   `carton`, and `pallet` labels when YOLO fails. This conflicts with CargoIQ's
   evidence-only principle.
3. The health API reports the vision model as loaded without checking it.
4. Incident parsing uses Python `eval` as a JSON fallback.
5. The dashboard UI uses live backend queries, but assistant welcome/citations,
   settings controls, and legacy product wording need integration cleanup.

## Implementation order

1. Safety, configuration, source-control hygiene, and CargoIQ naming.
2. Make vision and system health truthful; harden API error handling.
3. Connect SOP rules and all behaviour modules into the analysis pipeline.
4. Add backend-driven settings and analytics heatmap.
5. Expand tests and verify backend/frontend end-to-end with a functioning
   environment.
