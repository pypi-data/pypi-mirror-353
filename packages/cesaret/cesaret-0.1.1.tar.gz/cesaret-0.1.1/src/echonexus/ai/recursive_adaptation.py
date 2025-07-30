from typing import Dict
import logging
from ..models.narrative_state import NarrativeState, StateTransitionError


class RecursiveAdaptation:
    """Basic feedback processor updating the narrative state."""

    def process_feedback(self, state: NarrativeState, feedback: Dict[str, str]) -> None:
        if state.current_state == NarrativeState.FINALIZATION:
            raise StateTransitionError("Cannot process feedback in FINALIZATION state")

        text = feedback.get("feedback") or feedback.get("suggestion", "")
        text = text.strip()
        if text:
            key_phrase = text.lower().replace("add more ", "").replace("add a ", "").replace("add ", "").rstrip('.')
            state.metadata.setdefault("feedback", []).append(key_phrase)

        logging.warning("Feedback processed: %s", text)

        if state.current_state == NarrativeState.DRAFT:
            state.transition_to_review()

    def validate_coherence(self, state: NarrativeState) -> bool:
        if state.current_state == NarrativeState.REVIEW:
            return True
        return bool(state.metadata)

    def integrate_feedback(self, state: NarrativeState, feedback: Dict[str, str]) -> None:
        self.process_feedback(state, feedback)
