from dataclasses import dataclass, field

import redis

from ..base import BaseBackend

# Enums for RQ DataStore and EventBroker types
# class RQBackendType(BackendType):
#    REDIS = "redis"
#    MEMORY = "memory"


@dataclass  # (slots=True)
class RQBackend(BaseBackend):
    """RQ Backend implementation for Redis Queue (RQ) job storage and queuing.

    This class provides a Redis-based backend for RQ job storage and queue management.
    It supports both Redis and in-memory storage options for development/testing.

    Args:
        queues (str | list[str] | None): Names of queues to create. Defaults to ["default"].
        num_workers (int): Number of worker processes to use. Defaults to 1.

    Attributes:
        type (str): Backend type, either "redis" or "memory". Inherited from BaseBackend.
        uri (str): Connection URI. Inherited from BaseBackend.
        result_namespace (str): Namespace for storing job results in Redis.
        _client (redis.Redis | dict): Redis client or dict for memory storage.

    Raises:
        ValueError: If an invalid backend type is specified.

    Example:
        ```python
        # Create Redis backend with default queue
        backend = RQBackend(
            type="redis",
            uri="redis://localhost:6379/0"
        )

        # Create Redis backend with multiple queues
        backend = RQBackend(
            type="redis",
            uri="redis://localhost:6379/0",
            queues=["high", "default", "low"]
        )

        # Create in-memory backend for testing
        backend = RQBackend(type="memory", queues=["test"])
        ```
    """

    queues: str | list[str] | None = field(default_factory=lambda: ["default"])
    num_workers: int = field(default=1)

    def __post_init__(self) -> None:
        """Initialize and validate the backend configuration.

        This method is called automatically after instance creation. It:
        1. Sets default type to "redis" if not specified
        2. Calls parent class initialization
        3. Validates backend type
        4. Sets default result namespace

        Raises:
            ValueError: If an unsupported backend type is specified.
                Only "redis" and "memory" types are supported.
        """
        if self.type is None:
            self.type = "redis"
        super().__post_init__()

        if not self.type.is_memory_type and not self.type.is_redis_type:
            raise ValueError(
                f"Invalid backend type: {self.type}. Valid types: {[self.type.REDIS, self.type.MEMORY]}"
            )

        self.result_namespace = getattr(self, "result_namespace", "flowerpower:results")

    def setup(self) -> None:
        """Set up the Redis client or in-memory storage.

        This method initializes the backend storage based on the configured type.
        For Redis, it creates a Redis client with the specified connection parameters.
        For in-memory storage, it creates a simple dictionary.

        Raises:
            ValueError: If an unsupported backend type is specified.
            redis.RedisError: If Redis connection fails.

        Example:
            ```python
            backend = RQBackend(
                type="redis",
                host="localhost",
                port=6379,
                password="secret",
                database="0",
                ssl=True
            )
            backend.setup()
            ```
        """
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
                ssl_cert_reqs=None if not self.verify_ssl else "required",
                ssl_ca_certs=self.ca_file,
                ssl_certfile=self.cert_file,
                ssl_keyfile=self.key_file,
            )
        elif self.type.is_memory_type:
            # Simple in-memory dict for testing
            self._client = {}
        else:
            raise ValueError(f"Unsupported RQBackend type: {self.type}")

    @property
    def client(self) -> redis.Redis | dict:
        """Get the initialized storage client.

        This property provides access to the Redis client or in-memory dictionary,
            initializing it if needed.

        Returns:
            redis.Redis | dict: The Redis client for Redis backend,
                or dictionary for in-memory backend.

        Example:
            ```python
            backend = RQBackend(type="redis", uri="redis://localhost:6379/0")
            redis_client = backend.client  # Gets Redis client
            redis_client.set("key", "value")

            backend = RQBackend(type="memory")
            mem_dict = backend.client  # Gets dict for testing
            mem_dict["key"] = "value"
            ```
        """
        if self._client is None:
            self.setup()
        return self._client
