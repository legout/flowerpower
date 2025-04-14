from apscheduler.eventbrokers.base import BaseEventBroker
from sqlalchemy.ext.asyncio import AsyncEngine

from ...base import BackendType, BaseBackend


class APSEventBrokerType(BackendType):
    POSTGRESQL = "postgresql"
    MEMORY = "memory"
    REDIS = "redis"
    MQTT = "mqtt"


class APSEventBroker(BaseBackend):
    """Data store for APScheduler."""

    def __post_init__(self):
        super().__post_init__(backend_type=APSEventBrokerType)

    @classmethod
    def from_dict(cls, d: dict[str, any]) -> "APSEventBroker":
        return cls(**d)

    def _validate_inputs(self) -> None:
        if self.type.value not in [ds.value for ds in APSEventBrokerType]:
            raise ValueError(
                f"Invalid data store type: {self.type}. Valid types: {[ds.value for ds in APSEventBrokerType]}"
            )

    def _setup_asyncpg_event_broker(self):
        from apscheduler.eventbrokers.asyncpg import AsyncpgEventBroker

        if self._sqla_engine is None:
            self._event_broker = AsyncpgEventBroker.from_dsn(dsn=self.uri)
        else:
            self._event_broker = AsyncpgEventBroker.from_async_sqla_engine(
                engine=self._sqla_engine
            )

    def _setup_mqtt_event_broker(self):
        import urllib.parse

        from apscheduler.eventbrokers.mqtt import MQTTEventBroker

        # Parse the URI
        parsed = urllib.parse.urlparse(self.uri)

        hostname = parsed.hostname
        port = parsed.port
        username = parsed.username
        password = parsed.password
        use_ssl = parsed.scheme == "mqtts"

        self._event_broker = MQTTEventBroker(
            host=hostname, port=port, ssl=use_ssl, topic="flowerpower/scheduler"
        )
        if (self.username is not None) and (self.password is not None):
            self._event_broker._client.username_pw_set(
                username,
                password,
            )

    def _setup_redis_event_broker(self):
        from apscheduler.eventbrokers.redis import RedisEventBroker

        self._event_broker = RedisEventBroker(self.uri)

    def _setup_local_event_broker(self):
        from apscheduler.eventbrokers.local import LocalEventBroker

        self._event_broker = LocalEventBroker()

    def setup(self):
        if self.is_sqla_type:
            self._setup_asyncpg_event_broker()
        elif self.is_mqtt_type:
            self._setup_mqtt_event_broker()
        elif self.is_redis_type:
            self._setup_redis_event_broker()
        else:
            self._setup_local_event_broker()

    @property
    def client(self) -> BaseEventBroker:
        if self._event_broker is None:
            self.setup()
        return self._event_broker

    @property
    def sqla_engine(self) -> AsyncEngine | None:
        if self._sqla_engine is None:
            self.setup()
        return self._sqla_engine
