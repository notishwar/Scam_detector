import logging
import os
from fastapi import Header, HTTPException
from typing import Optional

from .config import HACKATHON_API_KEY

logger = logging.getLogger("honeypot.auth")

async def get_api_key(x_llm_api_key: Optional[str] = Header(None, alias="x-llm-api-key")):
    api_key = (
        x_llm_api_key
        or os.getenv("LLM_API_KEY")
        or os.getenv("OPENROUTER_API_KEY")
        or os.getenv("OPENAI_API_KEY")
    )
    if not api_key:
        raise HTTPException(status_code=401, detail="Missing X-LLM-API-KEY header and no server key configured")
    return api_key


async def require_hackathon_key(x_api_key: Optional[str] = Header(None, alias="x-api-key")):
    if not x_api_key:
        logger.warning("Unauthorized request: missing x-api-key")
        raise HTTPException(status_code=401, detail="Missing x-api-key header")
    if not HACKATHON_API_KEY:
        logger.error("Server not configured with HACKATHON_API_KEY")
        raise HTTPException(status_code=401, detail="Server not configured with HACKATHON_API_KEY")
    if x_api_key != HACKATHON_API_KEY:
        logger.warning("Unauthorized request: invalid x-api-key")
        raise HTTPException(status_code=401, detail="Invalid x-api-key header")
    return x_api_key
