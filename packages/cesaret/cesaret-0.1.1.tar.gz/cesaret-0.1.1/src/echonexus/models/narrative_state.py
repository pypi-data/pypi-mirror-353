from dataclasses import dataclass, field
from typing import Any, Dict, List


class StateTransitionError(ValueError):
    """Raised when an invalid state transition is attempted."""


@dataclass(init=False)
class NarrativeState:
    """Represents the state of a narrative entry."""

    entry_id: str = ""
    current_state: str = "DRAFT"
    metadata: Dict[str, Any] = field(default_factory=dict)
    history: List[Dict[str, Any]] = field(default_factory=list)

    DRAFT = "DRAFT"
    REVIEW = "REVIEW"
    FINALIZATION = "FINALIZATION"
    VALID_STATES = {DRAFT, REVIEW, FINALIZATION}

    def __init__(self, entry_id: str = "", state: str = "DRAFT", metadata: Dict[str, Any] | None = None) -> None:
        self.entry_id = entry_id
        if state not in self.VALID_STATES:
            raise StateTransitionError(f"Unknown state {state}")
        self.current_state = state
        self.metadata = metadata or {}
        self.history: List[Dict[str, Any]] = []

    def transition_to_draft(self) -> None:
        self._transition(self.DRAFT)

    def transition_to_review(self) -> None:
        if self.current_state != self.DRAFT:
            raise StateTransitionError(
                f"Invalid transition from {self.current_state} to REVIEW"
            )
        self._transition(self.REVIEW)

    def transition_to_finalization(self) -> None:
        if self.current_state not in {self.DRAFT, self.REVIEW}:
            raise StateTransitionError(
                f"Invalid transition from {self.current_state} to FINALIZATION"
            )
        self._transition(self.FINALIZATION)

    def _transition(self, new_state: str) -> None:
        if new_state not in self.VALID_STATES:
            raise StateTransitionError(f"Unknown state {new_state}")
        self.history.append({"state": self.current_state, "metadata": self.metadata.copy()})
        self.current_state = new_state

    def get_state_info(self) -> Dict[str, Any]:
        return {
            "entry_id": self.entry_id,
            "state": self.current_state,
            "metadata": self.metadata,
            "history": self.history,
        }
