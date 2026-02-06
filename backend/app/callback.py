import asyncio
import logging
import httpx

from .config import GUVI_CALLBACK_URL, GUVI_CALLBACK_RETRIES, GUVI_CALLBACK_BACKOFF_SEC
from .session_store import SessionState

logger = logging.getLogger("honeypot.callback")


async def send_guvi_callback(session: SessionState, agent_notes: str) -> None:
    if session.callback_sent:
        return

    payload = {
        "sessionId": session.session_id,
        "scamDetected": session.scam_detected,
        "totalMessagesExchanged": session.total_messages,
        "extractedIntelligence": {
            "bankAccounts": session.extracted.bank_accounts,
            "upiIds": session.extracted.upi_ids,
            "phishingLinks": session.extracted.urls,
            "phoneNumbers": session.extracted.phone_numbers,
            "suspiciousKeywords": sorted(session.suspicious_keywords),
        },
        "agentNotes": agent_notes,
    }

    for attempt in range(1, GUVI_CALLBACK_RETRIES + 1):
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(GUVI_CALLBACK_URL, json=payload, timeout=10.0)
                resp.raise_for_status()
            session.callback_sent = True
            return
        except Exception as exc:
            logger.warning("GUVI callback failed (attempt %s): %s", attempt, exc)
            if attempt < GUVI_CALLBACK_RETRIES:
                await asyncio.sleep(GUVI_CALLBACK_BACKOFF_SEC * attempt)
