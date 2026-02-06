import time
from dataclasses import dataclass, field
from threading import Lock
from typing import Dict, List, Set

from .models import ExtractedIntel
from .schemas import HackathonMessage


@dataclass
class SessionState:
    session_id: str
    history: List[HackathonMessage] = field(default_factory=list)
    scam_detected: bool = False
    extracted: ExtractedIntel = field(default_factory=ExtractedIntel)
    suspicious_keywords: Set[str] = field(default_factory=set)
    total_messages: int = 0
    callback_sent: bool = False
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)


_sessions: Dict[str, SessionState] = {}
_lock = Lock()


def get_session(session_id: str) -> SessionState:
    with _lock:
        session = _sessions.get(session_id)
        if session is None:
            session = SessionState(session_id=session_id)
            _sessions[session_id] = session
        return session


def update_history(session: SessionState, history: List[HackathonMessage]) -> None:
    session.history = list(history)
    session.total_messages = len(session.history)
    session.updated_at = time.time()


def merge_intel(session: SessionState, new_intel: ExtractedIntel) -> None:
    def merge_list(target: List[str], additions: List[str]) -> List[str]:
        for item in additions:
            if item not in target:
                target.append(item)
        return target

    session.extracted.upi_ids = merge_list(session.extracted.upi_ids, new_intel.upi_ids)
    session.extracted.bank_accounts = merge_list(session.extracted.bank_accounts, new_intel.bank_accounts)
    session.extracted.phone_numbers = merge_list(session.extracted.phone_numbers, new_intel.phone_numbers)
    session.extracted.urls = merge_list(session.extracted.urls, new_intel.urls)
    session.extracted.crypto_wallets = merge_list(session.extracted.crypto_wallets, new_intel.crypto_wallets)
    session.extracted.emails = merge_list(session.extracted.emails, new_intel.emails)
    session.extracted.ip_addresses = merge_list(session.extracted.ip_addresses, new_intel.ip_addresses)
    session.extracted.locations = merge_list(session.extracted.locations, new_intel.locations)
    session.extracted.addresses = merge_list(session.extracted.addresses, new_intel.addresses)
    session.extracted.geo_coordinates = merge_list(session.extracted.geo_coordinates, new_intel.geo_coordinates)


def has_intel(session: SessionState) -> bool:
    return any([
        session.extracted.upi_ids,
        session.extracted.bank_accounts,
        session.extracted.phone_numbers,
        session.extracted.urls,
        session.suspicious_keywords,
    ])
