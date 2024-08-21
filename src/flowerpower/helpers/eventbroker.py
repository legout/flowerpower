from sqlalchemy.engine import Engine

ALL_EVENT_BROKERS = [
    "sqlalchemy",
    "asyncpg",
    "psycopg3",
    "postgresql",
    "mqtt",
    "redis",
    "local",
    "memory",
]


class EventBroker:
    def __init__(
        self,
        type: str,
        uri: str | None = None,
        sqla_engine: Engine | None = None,
        host: str = "localhost",
        port: int = 1883,
        username: str | None = None,
        password: str | None = None,
    ):
        self.type = type
        self.uri = uri
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self._sqla_engine = sqla_engine

        if type not in ALL_EVENT_BROKERS:
            raise ValueError(
                f"Invalid event broker type: {type}. Valid event broker types are: {ALL_EVENT_BROKERS}"
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
        from apscheduler.eventbrokers.mqtt import MQTTEventBroker

        self._event_broker = MQTTEventBroker(
            self.host, self.port, topic="flowerpower/scheduler"
        )
        if (self.username is not None) and (self.password is not None):
            self._event_broker._client.username_pw_set(
                self.username,
                self.password,
            )

    def _setup_redis_event_broker(self):
        from apscheduler.eventbrokers.redis import RedisEventBroker

        if self.uri is None:
            self.uri = f"redis://{self.host}:{self.port}"
        self._event_broker = RedisEventBroker(self.uri)

    def _setup_local_event_broker(self):
        from apscheduler.eventbrokers.local import LocalEventBroker

        self._event_broker = LocalEventBroker()

    def setup(self):
        if self.type in ["sqlalchemy", "asyncpg", "psycopg3", "postgresql"]:
            self._setup_asyncpg_event_broker()
        elif self.type == "mqtt":
            self._setup_mqtt_event_broker()
        elif self.type == "redis":
            self._setup_redis_event_broker()
        else:
            self._setup_local_event_broker()

    def get(self):
        return self._event_broker


def setup_event_broker(
    type: str,
    uri: str | None = None,
    sqla_engine: Engine | None = None,
    host: str = "localhost",
    port: int = 1883,
    username: str | None = None,
    password: str | None = None,
):
    eb = EventBroker(
        type=type,
        uri=uri,
        sqla_engine=sqla_engine,
        host=host,
        port=port,
        username=username,
        password=password,
    )
    eb.setup()
    return eb.get()
