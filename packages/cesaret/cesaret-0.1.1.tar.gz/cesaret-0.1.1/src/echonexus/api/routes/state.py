from fastapi import APIRouter, HTTPException
from ..state_store import get_entry, list_entries

router = APIRouter()


@router.get("/entries")
async def list_entries_route():
    return list_entries()


@router.get("/state/{entry_id}")
async def get_narrative_state(entry_id: str):
    state = get_entry(entry_id)
    if not state:
        raise HTTPException(status_code=404, detail="Narrative entry not found.")
    return state.get_state_info()
