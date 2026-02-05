import logging
import sys

# Configure logging
logger = logging.getLogger("agentic_honeypot")
logger.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

def log_interaction(session_id: str, message: str, is_scam: bool, confidence: float):
    logger.info(f"Session: {session_id} | Msg: {message[:50]}... | Scam: {is_scam} | Confidence: {confidence}")

def log_intel(session_id: str, intel: dict):
    if any(intel.values()):
        logger.info(f"INTEL EXTRACTED - Session: {session_id} | Data: {intel}")
