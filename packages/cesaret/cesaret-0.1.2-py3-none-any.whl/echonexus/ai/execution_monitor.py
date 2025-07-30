from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class ExecutionMonitor:
    """Tracks narrative state transitions and verifies basic coherence."""

    state_log: List[Dict[str, Any]] = field(default_factory=list)

    def validate_coherence(self, state) -> bool:
        return state.current_state in {"DRAFT", "REVIEW", "FINALIZATION"}

    def log_state_transition(self, state) -> None:
        self.state_log.append({"state": state.current_state, "metadata": state.metadata})

    def detect_coherence_drift(self) -> bool:
        return False

    def generate_report(self) -> str:
        if not self.state_log:
            return "No state transitions logged."
        latest = self.state_log[-1]
        return f"{latest['metadata'].get('title', '')} - {latest['state']}"
