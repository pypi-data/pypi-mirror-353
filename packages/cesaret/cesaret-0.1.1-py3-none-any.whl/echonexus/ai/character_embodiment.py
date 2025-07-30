from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class CharacterEmbodiment:
    """Simple container for character traits and state evolution."""

    name: str
    traits: Dict[str, Any]
    logs: List[Dict[str, Any]] = field(default_factory=list)

    def update_state(self, new_state: Dict[str, Any]) -> None:
        self.traits.update(new_state)
        self.logs.append({"action": "update_state", "state": new_state})

    def integrate_feedback(self, feedback: Dict[str, Any]) -> None:
        for key, value in feedback.items():
            self.traits[key] = value
        self.logs.append({"action": "integrate_feedback", "feedback": feedback})

    def get_logs(self) -> List[Dict[str, Any]]:
        return self.logs
