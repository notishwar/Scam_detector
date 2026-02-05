import time
from typing import Dict
from .models import SessionData

# In-memory storage: { (api_key_hash + session_id): SessionData }
sessions: Dict[str, SessionData] = {}

def get_session_key(api_key: str, session_id: str) -> str:
    # Simple composite key. In prod, hash the key.
    return f"{api_key}_{session_id}"

def get_session(api_key: str, session_id: str) -> SessionData:
    key = get_session_key(api_key, session_id)
    if key not in sessions:
        # Create new session if not exists
        sessions[key] = SessionData(
            session_id=session_id,
            persona="elderly", # Default, can be updated
            created_at=time.time(),
            history=[]
        )
    return sessions[key]

def update_session_history(api_key: str, session_id: str, role: str, content: str):
    session = get_session(api_key, session_id)
    session.history.append({"role": role, "content": content})
