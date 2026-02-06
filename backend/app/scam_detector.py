import json
from typing import List, Tuple, Optional
import httpx

from .config import LLM_API_KEY, LLM_API_BASE, LLM_MODEL
from .detector import detect_scam_heuristics, KEYWORDS
from .extractor import extract_intelligence


def extract_suspicious_keywords(text: str) -> List[str]:
    text_lower = text.lower()
    matches = []
    for keywords in KEYWORDS.values():
        for kw in keywords:
            if kw in text_lower:
                matches.append(kw)
    return list(set(matches))


async def llm_classify_scam(text: str) -> Optional[bool]:
    if not LLM_API_KEY:
        return None

    prompt = (
        "Answer only YES or NO. "
        "Is this message attempting financial fraud, phishing, impersonation, coercion, or extortion?\n"
        f"Message: {text}"
    )

    headers = {
        "Authorization": f"Bearer {LLM_API_KEY}",
        "Content-Type": "application/json"
    }
    if "openrouter.ai" in LLM_API_BASE:
        headers["HTTP-Referer"] = "http://localhost"
        headers["X-Title"] = "Honeypot Scam Classifier"

    payload = {
        "model": LLM_MODEL,
        "messages": [
            {"role": "system", "content": "You are a strict scam intent classifier."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 3,
        "temperature": 0
    }

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(LLM_API_BASE, json=payload, headers=headers, timeout=10.0)
            resp.raise_for_status()
            data = resp.json()
            content = data["choices"][0]["message"]["content"].strip().lower()
            if content.startswith("yes"):
                return True
            if content.startswith("no"):
                return False
    except Exception:
        return None
    return None


async def detect_scam_intent(text: str) -> Tuple[bool, float]:
    intel = extract_intelligence(text)
    heuristic_score, _ = detect_scam_heuristics(text, intel)
    llm_flag = await llm_classify_scam(text)

    if llm_flag is True:
        return True, max(heuristic_score, 75.0)
    if llm_flag is False:
        return heuristic_score >= 50.0, heuristic_score
    return heuristic_score >= 50.0, heuristic_score

