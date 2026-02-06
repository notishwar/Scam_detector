import os

HACKATHON_API_KEY = os.getenv("HACKATHON_API_KEY", "")

LLM_API_KEY = (
    os.getenv("LLM_API_KEY")
    or os.getenv("OPENROUTER_API_KEY")
    or os.getenv("OPENAI_API_KEY")
    or ""
)
LLM_API_BASE = os.getenv("LLM_API_BASE", "https://openrouter.ai/api/v1/chat/completions")
LLM_MODEL = os.getenv("LLM_MODEL", "meta-llama/llama-3.1-8b-instruct")

GUVI_CALLBACK_URL = os.getenv(
    "GUVI_CALLBACK_URL",
    "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"
)
GUVI_MIN_TURNS = int(os.getenv("GUVI_MIN_TURNS", "6"))
GUVI_MAX_TURNS = int(os.getenv("GUVI_MAX_TURNS", "10"))
GUVI_CALLBACK_RETRIES = int(os.getenv("GUVI_CALLBACK_RETRIES", "3"))
GUVI_CALLBACK_BACKOFF_SEC = float(os.getenv("GUVI_CALLBACK_BACKOFF_SEC", "1.5"))

