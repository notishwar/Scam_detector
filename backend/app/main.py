import time
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .models import ChatMessage, AgentResponse, ExtractedIntel
from .auth import get_api_key
from .sessions import get_session, update_session_history
from .extractor import extract_intelligence
from .detector import detect_scam_heuristics
from .agent import HoneyPotAgent
from .logger import log_interaction, log_intel

app = FastAPI(title="Agentic Honey-Pot API")

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
