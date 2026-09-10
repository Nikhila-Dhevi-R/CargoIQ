from fastapi import APIRouter, HTTPException
from app.schemas.assistant import ChatRequest, IncidentExplainRequest, ShiftSummaryRequest
from app.assistant.assistant_service import AssistantService

router = APIRouter(prefix="/assistant", tags=["Assistant"])

@router.post("/chat")
async def assistant_chat(req: ChatRequest):
    if not req.message or not req.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")
    result = await AssistantService.chat(req.message, req.video_id, req.event_id)
    return {
        "success": True,
        "data": result,
        "error": None
    }

@router.post("/explain")
async def explain_incident(req: IncidentExplainRequest):
    result = await AssistantService.explain_incident(req.event_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return {
        "success": True,
        "data": result,
        "error": None
    }

@router.post("/summary")
async def generate_shift_summary(req: ShiftSummaryRequest):
    result = await AssistantService.generate_shift_summary(req.video_id)
    return {
        "success": True,
        "data": result,
        "error": None
    }
