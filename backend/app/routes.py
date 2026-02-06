import logging
from typing import List
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException

from .config import GUVI_MIN_TURNS, GUVI_MAX_TURNS, LLM_API_KEY, LLM_API_BASE, LLM_MODEL
from .schemas import HackathonChatRequest, HackathonChatResponse
from .session_store import get_session, update_history, merge_intel, has_intel
from .scam_detector import detect_scam_intent, extract_suspicious_keywords
from .callback import send_guvi_callback
from .extractor import extract_intelligence
from .agent import HoneyPotAgent
from .models import SessionData
from .auth import require_hackathon_key

router = APIRouter()
logger = logging.getLogger("honeypot.routes")


def _sender_to_role(sender: str) -> str:
    sender_lower = (sender or "").lower()
    if sender_lower in {"scammer", "user", "customer"}:
        return "user"
    return "assistant"


def _build_history(conversation_history) -> List[dict]:
    history = []
    for msg in conversation_history:
        role = _sender_to_role(msg.sender)
        history.append({"role": role, "content": msg.text})
    return history


@router.post("/analyze", response_model=HackathonChatResponse)
@router.post("/api/chat", response_model=HackathonChatResponse)
async def analyze_honeypot(
    request: HackathonChatRequest,
    background_tasks: BackgroundTasks,
    api_key: str = Depends(require_hackathon_key),
):
    session = get_session(request.sessionId)

    # Trust platform-provided history as source of truth.
    merged_history = list(request.conversationHistory) + [request.message]
    update_history(session, merged_history)

    # Scam detection (LLM primary, heuristic fallback)
    scam_detected, confidence = await detect_scam_intent(request.message.text)
    if scam_detected:
        session.scam_detected = True

    # Extract intelligence across all visible turns (handles catch-up replays)
    for msg in merged_history:
        intel = extract_intelligence(msg.text)
        merge_intel(session, intel)
        session.suspicious_keywords.update(extract_suspicious_keywords(msg.text))

    # Decide response
    persona = "elderly"
    if isinstance(request.metadata, dict):
        persona = request.metadata.get("persona", persona)

    if session.scam_detected:
        if not LLM_API_KEY:
            raise HTTPException(status_code=500, detail="Server not configured with LLM_API_KEY")
        agent = HoneyPotAgent(
            api_key=LLM_API_KEY,
            llm_url=LLM_API_BASE,
            llm_model=LLM_MODEL,
        )
        history = _build_history(request.conversationHistory)
        session_data = SessionData(
            session_id=request.sessionId,
            history=history,
            persona=persona,
            created_at=session.created_at,
        )
        reply = await agent.generate_response(request.message.text, session_data, history_override=history)
    else:
        reply = "I'm not sure I understand. Could you explain more?"

    # Completion condition and mandatory callback (once)
    if session.scam_detected and not session.callback_sent:
        if session.total_messages >= GUVI_MIN_TURNS and (has_intel(session) or session.total_messages >= GUVI_MAX_TURNS):
            agent_notes = (
                f"Scam detected (confidence {confidence}). "
                f"Keywords: {', '.join(sorted(session.suspicious_keywords)) or 'none'}."
            )
            background_tasks.add_task(send_guvi_callback, session, agent_notes)

    return HackathonChatResponse(status="success", reply=reply)
