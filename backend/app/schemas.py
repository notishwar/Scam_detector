from pydantic import BaseModel, Field
from typing import List, Dict, Any


class HackathonMessage(BaseModel):
    sender: str
    text: str
    timestamp: int

    class Config:
        extra = "forbid"


class HackathonChatRequest(BaseModel):
    sessionId: str
    message: HackathonMessage
    conversationHistory: List[HackathonMessage] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        extra = "forbid"


class HackathonChatResponse(BaseModel):
    status: str
    reply: str
