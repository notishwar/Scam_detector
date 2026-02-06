import time
import os
from typing import Optional, List
from fastapi import FastAPI, Depends, HTTPException, Header, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from .models import (
    ChatMessage,
    AgentResponse,
    ExtractedIntel,
    HackathonChatRequest,
    HackathonChatResponse,
    SessionData,
)
from .auth import get_api_key
from .sessions import get_session, update_session_history
from .extractor import extract_intelligence
from .detector import detect_scam_heuristics, KEYWORDS
from .agent import HoneyPotAgent
from .logger import log_interaction, log_intel
import httpx

app = FastAPI(title="Agentic Honey-Pot API")

GUVI_CALLBACK_URL = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"
GUVI_TURN_THRESHOLD = 6

# Allow CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def health_check():
    return {"status": "running", "service": "Agentic Honey-Pot"}

@app.post("/message", response_model=AgentResponse)
async def process_message(
    chat_msg: ChatMessage,
    api_key: str = Depends(get_api_key)
):
    # 1. Get/Create Session
    session = get_session(api_key, chat_msg.session_id)
    session.persona = chat_msg.persona # Update persona if changed (simple approach)
    
    # 2. Intel Extraction
    extracted_intel_data = extract_intelligence(chat_msg.message)
    log_intel(chat_msg.session_id, extracted_intel_data.dict())
    
    # 3. Scam Detection
    scam_confidence, risk_tags = detect_scam_heuristics(chat_msg.message, extracted_intel_data)
    
    # 4. Agent Interaction
    # Update history with user message
    update_session_history(api_key, chat_msg.session_id, "user", chat_msg.message)
    
    agent = HoneyPotAgent(
        api_key=api_key, 
        llm_url=chat_msg.llm_url, 
        llm_model=chat_msg.llm_model
    )
    
    # Generate reply
    # Context: If scam confidence is high, the agent should definitely engage.
    # The prompts are already designed to be "honeypots" so we always reply as the persona.
    reply = await agent.generate_response(chat_msg.message, session)
    
    # Update history with agent reply
    update_session_history(api_key, chat_msg.session_id, "assistant", reply)
    
    # Log interaction
    log_interaction(chat_msg.session_id, chat_msg.message, is_scam=(scam_confidence > 50), confidence=scam_confidence)
    
    # 5. Return Response
    return AgentResponse(
        reply=reply,
        scam_confidence=scam_confidence,
        risk_tags=risk_tags,
        extracted_intel=extracted_intel_data
    )

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

def _extract_suspicious_keywords(text: str) -> List[str]:
    text_lower = text.lower()
    matches = []
    for keywords in KEYWORDS.values():
        for kw in keywords:
            if kw in text_lower:
                matches.append(kw)
    return list(set(matches))

async def send_guvi_callback(
    session_id: str,
    extracted_data: ExtractedIntel,
    msg_count: int,
    scam_detected: bool,
    suspicious_keywords: List[str],
    agent_notes: str
):
    payload = {
        "sessionId": session_id,
        "scamDetected": scam_detected,
        "totalMessagesExchanged": msg_count,
        "extractedIntelligence": {
            "bankAccounts": extracted_data.bank_accounts,
            "upiIds": extracted_data.upi_ids,
            "phishingLinks": extracted_data.urls,
            "phoneNumbers": extracted_data.phone_numbers,
            "suspiciousKeywords": suspicious_keywords
        },
        "agentNotes": agent_notes
    }
    try:
        async with httpx.AsyncClient() as client:
            await client.post(GUVI_CALLBACK_URL, json=payload, timeout=10.0)
    except Exception:
        # Callback failures should never block or crash the API.
        return

async def get_hackathon_api_key(x_api_key: Optional[str] = Header(None, alias="x-api-key")):
    if not x_api_key:
        raise HTTPException(status_code=401, detail="Missing x-api-key header")
    expected = os.getenv("HACKATHON_API_KEY")
    if not expected:
        raise HTTPException(status_code=401, detail="Server not configured with HACKATHON_API_KEY")
    if x_api_key != expected:
        raise HTTPException(status_code=401, detail="Invalid x-api-key header")
    return x_api_key

@app.post("/api/chat", response_model=HackathonChatResponse)
@app.post("/api/hackathon/chat", response_model=HackathonChatResponse)
async def chat_hackathon(
    request: HackathonChatRequest,
    background_tasks: BackgroundTasks,
    api_key: str = Depends(get_hackathon_api_key)
):
    # Determine persona and optional LLM overrides from metadata
    persona = "elderly"
    llm_url = None
    llm_model = None
    if isinstance(request.metadata, dict):
        persona = request.metadata.get("persona", persona)
        llm_url = request.metadata.get("llmUrl") or request.metadata.get("llm_url")
        llm_model = request.metadata.get("llmModel") or request.metadata.get("llm_model")

    session = SessionData(
        session_id=request.sessionId,
        history=_build_history(request.conversationHistory),
        persona=persona,
        created_at=time.time(),
    )

    extracted_intel_data = extract_intelligence(request.message.text)
    scam_confidence, risk_tags = detect_scam_heuristics(request.message.text, extracted_intel_data)

    agent = HoneyPotAgent(
        api_key=api_key,
        llm_url=llm_url,
        llm_model=llm_model
    )
    reply = await agent.generate_response(request.message.text, session, history_override=session.history)

    msg_count = len(request.conversationHistory) + 1
    scam_detected = scam_confidence > 50
    suspicious_keywords = _extract_suspicious_keywords(request.message.text)
    agent_notes = (
        f"Scam detected with confidence {scam_confidence}. "
        f"Keywords: {', '.join(suspicious_keywords) or 'none'}."
    )

    if scam_detected and msg_count >= GUVI_TURN_THRESHOLD:
        background_tasks.add_task(
            send_guvi_callback,
            request.sessionId,
            extracted_intel_data,
            msg_count,
            scam_detected,
            suspicious_keywords,
            agent_notes,
        )

    return HackathonChatResponse(status="success", reply=reply)
