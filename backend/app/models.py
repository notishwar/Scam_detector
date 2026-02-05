from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class ChatMessage(BaseModel):
    session_id: str
    message: str
    persona: str = "elderly"  # elderly, student, naive
    llm_url: Optional[str] = None
    llm_model: Optional[str] = None

class ExtractedIntel(BaseModel):
    upi_ids: List[str] = []
    bank_accounts: List[str] = []
    phone_numbers: List[str] = []
    urls: List[str] = []
    crypto_wallets: List[str] = []
    emails: List[str] = []
    ip_addresses: List[str] = []
    locations: List[str] = []
    addresses: List[str] = []
    geo_coordinates: List[str] = []

class AgentResponse(BaseModel):
    reply: str
    scam_confidence: float
    risk_tags: List[str]
    extracted_intel: ExtractedIntel

class SessionData(BaseModel):
    session_id: str
    history: List[Dict[str, str]] = []  # List of {"role": "user"|"assistant", "content": "..."}
    persona: str
    created_at: float
