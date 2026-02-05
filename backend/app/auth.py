from fastapi import Header, HTTPException, Depends
from typing import Optional

async def get_api_key(x_llm_api_key: Optional[str] = Header(None)):
    if not x_llm_api_key:
        raise HTTPException(status_code=401, detail="Missing X-LLM-API-KEY header")
    return x_llm_api_key
