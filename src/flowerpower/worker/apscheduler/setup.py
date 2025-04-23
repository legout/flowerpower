from dataclasses import dataclass, field

from apscheduler.datastores.base import BaseDataStore
from apscheduler.eventbrokers.base import BaseEventBroker
from loguru import logger
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from ...utils.logging import setup_logging
from ..base import BaseBackend

setup_logging()


@dataclass  # (slots=True)
class APSDataStore(BaseBackend):
    """Data store for APScheduler."""

    schema: str | None = "flowerpower"

    def __post_init__(self):
        if self.type is None:
            self.type = "memory"
        super().__post_init__()

        if (
            not self.type.is_memory_type
            and not self.type.is_mongodb_type
            and not self.type.is_sqla_type
        ):
            raise ValueError(
                f"Invalid backend type: {self.type}. Valid types: {
                    [
                        self.type.POSTGRESQL,
                        self.type.MYSQL,
                        self.type.SQLITE,
                        self.type.MONGODB,
                        self.type.MEMORY,
                    ]
                }"
            )
        if self.type.is_sqlite_type and self.schema is not None:
            logger.warning(
                "SQLite does not support schema. When using SQLite, the schema will be ignored.",
                "When you need to use schemas, you can use several SQLite databases, ",
                "one for each schema. Or use PostgreSQL or MySQL.",
            )

    async def _setup_db(self) -> None:
        sqla_engine = create_async_engine(self.uri)

        try:
            await self._create_schema(sqla_engine)
        except Exception:
            await self._create_database_and_schema(sqla_engine)

    async def _create_schema(self, engine: AsyncEngine) -> None:
        if not self.schema:
            return

        async with engine.begin() as conn:
            await conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {self.schema}"))
            await conn.commit()

    async def _create_database_and_schema(self, engine: AsyncEngine) -> None:
        database_name = self.uri.split("/")[-1].split("?")[0]
        temp_uri = self.uri.replace(f"/{database_name}", "/template1")
        temp_engine = create_async_engine(temp_uri)

        async with temp_engine.begin() as conn:
            await conn.execute(text("COMMIT"))
            try:
                await conn.execute(text(f"CREATE DATABASE {database_name}"))
            finally:
                await conn.execute(text("COMMIT"))

        if self.schema:
            await self._create_schema(engine)

    def setup_db(self) -> None:
        from anyio.from_thread import start_blocking_portal

        with start_blocking_portal() as portal:
            portal.call(self._setup_db)

    def _setup_sqlalchemy(self) -> None:
        from apscheduler.datastores.sqlalchemy import SQLAlchemyDataStore

        if not self.type.is_sqlite_type:
            self.setup_db()
        self._sqla_engine = create_async_engine(self.uri)
        self._client = SQLAlchemyDataStore(self._sqla_engine, schema=self.schema)

    def _setup_mongodb(self) -> None:
        from apscheduler.datastores.mongodb import MongoDBDataStore

        self._client = MongoDBDataStore(self.uri, database=self.schema)

    def _setup_memory(self) -> None:
        from apscheduler.datastores.memory import MemoryDataStore

        self._client = MemoryDataStore()

    def setup(self) -> None:
        if self.type.is_sqla_type:
            self._setup_sqlalchemy()
        elif self.type.is_mongodb_type:
            self._setup_mongodb()
        else:
            self._setup_memory()

    @property
    def client(self) -> BaseDataStore:
        if self._client is None:
            self.setup()
        return self._client

    @property
    def sqla_engine(self) -> AsyncEngine | None:
        if self._sqla_engine is None:
            self.setup()
        return self._sqla_engine


@dataclass  # (slots=True)
class APSEventBroker(BaseBackend):
    """Data store for APScheduler."""

    def __post_init__(self):
        if self.type is None:
            self.type = "memory"
        super().__post_init__()

        if (
            not self.type.is_redis_type
            and not self.type.is_memory_type
            and not self.type.is_mongodb_type
            and not self.type.is_sqla_type
        ):
            raise ValueError(
                f"Invalid backend type: {self.type}. Valid types: {
                    [
                        self.type.POSTGRESQL,
                        self.type.MQTT,
                        self.type.REDIS,
                        self.type.MEMORY,
                    ]
                }"
            )

    # @classmethod
    # def from_dict(cls, d: dict[str, any]) -> "APSEventBroker":
    #    return cls(**d)

    def _setup_asyncpg_event_broker(self):
        from apscheduler.eventbrokers.asyncpg import AsyncpgEventBroker

        if self._sqla_engine is None:
            self._client = AsyncpgEventBroker.from_dsn(dsn=self.uri)
        else:
            self._client = AsyncpgEventBroker.from_async_sqla_engine(
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

        self._client = MQTTEventBroker(
            host=hostname, port=port, ssl=use_ssl, topic="flowerpower/worker"
        )
        if (self.username is not None) and (self.password is not None):
            self._client._client.username_pw_set(
                username,
                password,
            )

    def _setup_redis_event_broker(self):
        from apscheduler.eventbrokers.redis import RedisEventBroker

        self._client = RedisEventBroker(self.uri)

    def _setup_local_event_broker(self):
        from apscheduler.eventbrokers.local import LocalEventBroker

        self._client = LocalEventBroker()

    def setup(self):
        if self.type.is_sqla_type:
            self._setup_asyncpg_event_broker()
        elif self.type.is_mqtt_type:
            self._setup_mqtt_event_broker()
        elif self.type.is_redis_type:
            self._setup_redis_event_broker()
        else:
            self._setup_local_event_broker()

    @property
    def client(self) -> BaseEventBroker:
        if self._client is None:
            self.setup()
        return self._client

    @property
    def sqla_engine(self) -> AsyncEngine | None:
        if self._sqla_engine is None:
            self.setup()
        return self._sqla_engine

    @classmethod
    def from_ds_sqla(cls, sqla_engine: AsyncEngine) -> "APSEventBroker":
        if sqla_engine.url.drivername != "postgresql+asyncpg":
            raise ValueError(
                f"sqla_engine must be a PostgreSQL engine ('postgresql+asyncpg://'), got '{sqla_engine.url.drivername}'"
            )
        return cls(
            type="postgresql",
            _sqla_engine=sqla_engine,
        )


@dataclass(slots=True)
class APSBackend:
    data_store: APSDataStore | dict | None = field(default_factory=APSDataStore)
    event_broker: APSEventBroker | dict | None = field(default_factory=APSEventBroker)

    def __post_init__(self):
        if self.data_store is not None:
            if isinstance(self.data_store, dict):
                self.data_store = APSDataStore.from_dict(self.data_store)
            self.data_store.setup()
        if self.event_broker is not None:
            if isinstance(self.event_broker, dict):
                if "from_ds_sqla" in self.event_broker:
                    self.event_broker = APSEventBroker.from_ds_sqla(
                        self.data_store.sqla_engine
                    )
                else:
                    self.event_broker = APSEventBroker.from_dict(self.event_broker)
            self.event_broker.setup()
