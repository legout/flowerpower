from sqlalchemy.engine import Engine

ALL_EVENT_BROKERS = [
    "asyncpg",
    "psycopg3",
    "mqtt",
    "redis",
    "local",
    "memory",
]


class EventBroker:
    def __init__(
        self,
        type: str,
        url: str | None,
        sqla_engine: Engine | None = None,
        host: str = "localhost",
        port: int = 1883,
        username: str | None = None,
        password: str | None = None,
    ):
        self.type = type
        self.url = url
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.sqla_engine = sqla_engine

        if type not in ALL_EVENT_BROKERS:
            raise ValueError(
                f"Invalid event broker type: {type}. Valid event broker types are: {ALL_EVENT_BROKERS}"
            )

    def _setup_asyncpg_event_broker(self):
        from apscheduler.eventbrokers.asyncpg import AsyncpgEventBroker

        if self._sqla_engine is None:
            self._event_broker = AsyncpgEventBroker.from_dsn(dsn=self.url)
        else:
            self._event_broker = AsyncpgEventBroker.from_async_sqla_engine(
                engine=self.sqla_engine
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

        if self.url is None:
            self.url = "redis://{self.host}:{self.port}"
        self._event_broker = RedisEventBroker(self.url)

    def _setup_local_event_broker(self):
        from apscheduler.eventbrokers.local import LocalEventBroker

        self._event_broker = LocalEventBroker()

    def setup(self):
        if self.type == "asyncpg" or self.type == "psycopg3":
            self._setup_asyncpg_event_broker()
        elif self.type == "mqtt":
            self._setup_mqtt_event_broker()
        elif self.type == "redis":
            self._setup_redis_event_broker()
        else:
            self._setup_local_event_broker()

    def get(self):
        return self._event_broker


def get_event_broker(
    type: str,
    url: str | None = None,
    sqla_engine: Engine | None = None,
    host: str = "localhost",
    port: int = 1883,
    username: str | None = None,
    password: str | None = None,
):
    eb = EventBroker(
        type=type,
        url=url,
        sqla_engine=sqla_engine,
        host=host,
        port=port,
        username=username,
        password=password,
    )
    eb.setup()
    return eb.get()