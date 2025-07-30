from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from ..state_store import get_entry, create_entry
from ...models.narrative_state import NarrativeState
from ...ai.recursive_adaptation import RecursiveAdaptation

router = APIRouter()

adapter = RecursiveAdaptation()


class Feedback(BaseModel):
    feedback: str


@router.post("/feedback/{entry_id}")
async def submit_feedback(entry_id: str, payload: dict = Body(...)):
    if "feedback" not in payload:
        raise HTTPException(
            status_code=422,
            detail=[{"loc": ["body", "feedback"], "msg": "field required", "type": "value_error.missing"}],
        )
    feedback = Feedback(**payload)
    state = get_entry(entry_id)
    if not state:
        state = create_entry(entry_id)

    adapter.process_feedback(state, {"feedback": feedback.feedback})
    return {"message": "Feedback processed successfully."}
