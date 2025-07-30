import os
from typing import Dict, List, Optional
import requests
from ..models.narrative_state import NarrativeState


STATE_STORE: Dict[str, NarrativeState] = {
    "test_entry": NarrativeState(entry_id="test_entry")
}

UPSTASH_URL = os.getenv("UPSTASH_VECTOR_REST_URL")
UPSTASH_TOKEN = os.getenv("UPSTASH_VECTOR_REST_TOKEN")
HEADERS = {"Authorization": f"Bearer {UPSTASH_TOKEN}"} if UPSTASH_TOKEN else {}

def _remote_get(entry_id: str) -> Optional[NarrativeState]:
    if not UPSTASH_URL or not UPSTASH_TOKEN:
        return None
    try:
        r = requests.get(f"{UPSTASH_URL}/vectors/{entry_id}", headers=HEADERS, timeout=5)
        if r.status_code == 200:
            return NarrativeState(**r.json())
    except Exception:
        pass
    return None

def _remote_set(state: NarrativeState) -> None:
    if not UPSTASH_URL or not UPSTASH_TOKEN:
        return
    try:
        requests.post(
            f"{UPSTASH_URL}/vectors/{state.entry_id}",
            headers=HEADERS,
            json=state.__dict__,
            timeout=5,
        )
    except Exception:
        pass

def _remote_list() -> List[str]:
    if not UPSTASH_URL or not UPSTASH_TOKEN:
        return []
    try:
        r = requests.get(f"{UPSTASH_URL}/vectors", headers=HEADERS, timeout=5)
        if r.status_code == 200:
            return r.json().get("ids", [])
    except Exception:
        pass
    return []

def get_entry(entry_id: str) -> Optional[NarrativeState]:
    state = STATE_STORE.get(entry_id)
    if state is not None:
        return state
    remote = _remote_get(entry_id)
    if remote:
        STATE_STORE[entry_id] = remote
    return remote

def create_entry(entry_id: str) -> NarrativeState:
    state = NarrativeState(entry_id=entry_id)
    STATE_STORE[entry_id] = state
    _remote_set(state)
    return state

def list_entries() -> List[str]:
    entries = list(STATE_STORE.keys())
    remote_ids = _remote_list()
    for rid in remote_ids:
        if rid not in entries:
            entries.append(rid)
    return entries
