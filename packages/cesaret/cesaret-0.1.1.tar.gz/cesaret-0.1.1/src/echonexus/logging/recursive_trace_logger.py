from typing import Any, Dict, List
from datetime import datetime


class RecursiveTraceLogger:
    """Lightweight in-memory logger for narrative events."""

    def __init__(self) -> None:
        self.history: List[Dict[str, Any]] = []

    def log_event(self, event: Dict[str, Any]) -> None:
        if "timestamp" not in event:
            event["timestamp"] = datetime.utcnow().isoformat() + "Z"
        self.history.append(event)

    def retrieve_history(self) -> List[Dict[str, Any]]:
        return list(self.history)
