from typing import Any, Dict

try:
    from redis import Redis
except Exception:  # pragma: no cover - redis not installed
    Redis = None  # type: ignore


class RedisClient:
    """Simple wrapper around redis with in-memory fallback."""

    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0) -> None:
        self.host = host
        self.port = port
        self.db = db
        self.memory_store: Dict[str, Any] = {}
        self.client = self._connect()

    def _connect(self):
        if Redis is None:
            return None
        try:
            client = Redis(host=self.host, port=self.port, db=self.db)
            client.ping()
            return client
        except Exception:
            return None

    def set_state(self, key: str, value: Any) -> None:
        if self.client:
            self.client.set(key, value)
        self.memory_store[key] = value

    def get_state(self, key: str) -> Any:
        if self.client:
            val = self.client.get(key)
            if val is not None:
                return val
        return self.memory_store.get(key)

    def delete_state(self, key: str) -> None:
        if self.client:
            self.client.delete(key)
        self.memory_store.pop(key, None)

    def exists(self, key: str) -> bool:
        if self.client:
            if self.client.exists(key):
                return True
        return key in self.memory_store

    def close(self) -> None:
        if self.client:
            self.client.close()
