import datetime as dt
import json
from dataclasses import dataclass, field

import redis

from ..base import BaseBackend

# Enums for RQ DataStore and EventBroker types
# class RQBackendType(BackendType):
#    REDIS = "redis"
#    MEMORY = "memory"


@dataclass  # (slots=True)
class RQBackend(BaseBackend):
    """
    RQ DataStore backend for job result storage.
    Inherits from BaseBackend and adapts Redis logic.
    """

    queues: str | list[str] | None = field(default_factory=lambda: ["default"])

    def __post_init__(self):
        if self.type is None:
            self.type = "redis"
        super().__post_init__()

        if not self.type.is_memory_type and not self.type.is_redis_type:
            raise ValueError(
                f"Invalid backend type: {self.type}. Valid types: {[self.type.REDIS, self.type.MEMORY]}"
            )

        self.result_namespace = getattr(self, "result_namespace", "flowerpower:results")

    def setup(self):
        # Use connection info from BaseBackend to create Redis client
        if self.type.is_redis_type:
            # Parse db from database or default to 0
            db = 0
            if self.database is not None:
                try:
                    db = int(self.database)
                except Exception:
                    db = 0
            self._client = redis.Redis(
                host=self.host or self.type.default_host,
                port=self.port or self.type.default_port,
                db=db,
                password=self.password,
                ssl=self.ssl,
            )
        elif self.type.is_memory_type:
            # Simple in-memory dict for testing
            self._client = {}
        else:
            raise ValueError(f"Unsupported RQBackend type: {self.type}")

    @property
    def client(self):
        if self._client is None:
            self.setup()
        return self._client

    # def store_job_result(
    #     self, job_id: str, result: object, expiration_time: dt.timedelta | None = None
    # ) -> None:
    #     """
    #     Store a job result in Redis or memory.
    #     """
    #     key = f"{self.result_namespace}:{job_id}"
    #     serialized_result = json.dumps(result) if result is not None else None

    #     if self.type.is_redis_type:
    #         self.client.set(key, serialized_result)
    #         if expiration_time:
    #             seconds = int(expiration_time.total_seconds())
    #             if seconds > 0:
    #                 self.client.expire(key, seconds)
    #     elif self.type.is_memory_type:
    #         self.client[key] = serialized_result
    #     else:
    #         raise ValueError(f"Unsupported RQBackend type: {self.type}")

    # def get_job_result(self, job_id: str) -> object:
    #     """
    #     Get a job result from Redis or memory.
    #     """
    #     key = f"{self.result_namespace}:{job_id}"
    #     if self.type.is_redis_type:
    #         result = self.client.get(key)
    #         if result:
    #             return json.loads(result)
    #         return None
    #     elif self.type.is_memory_type:
    #         result = self.client.get(key)
    #         if result:
    #             return json.loads(result)
    #         return None
    #     else:
    #         raise ValueError(f"Unsupported RQBackend type: {self.type}")
