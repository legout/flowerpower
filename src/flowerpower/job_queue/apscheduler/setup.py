# Standard library imports
from dataclasses import dataclass, field

# Third-party imports
from apscheduler.datastores.base import BaseDataStore
from apscheduler.eventbrokers.base import BaseEventBroker
from loguru import logger
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

# Local imports
from ...utils.logging import setup_logging
from ..base import BaseBackend

setup_logging()


@dataclass  # (slots=True)
class APSDataStore(BaseBackend):
    """APScheduler data store implementation that supports multiple backend types.

    This class provides a flexible data store interface for APScheduler, supporting various
    backend storage options including SQLAlchemy-compatible databases, MongoDB, and in-memory
    storage.

    Args:
        schema (str | None): Database schema name. Defaults to "flowerpower".
            Note: Ignored for SQLite databases.

    Attributes:
        type (BackendType): Type of backend storage (inherited from BaseBackend)
        uri (str): Connection URI for the backend (inherited from BaseBackend)
        _client (BaseDataStore): The APScheduler data store instance
        _sqla_engine (AsyncEngine): SQLAlchemy async engine for SQL databases

    Raises:
        ValueError: If an invalid backend type is specified

    Example:
        ```python
        # Create PostgreSQL data store
        data_store = APSDataStore(
            type="postgresql",
            uri="postgresql+asyncpg://user:pass@localhost/db",
            schema="scheduler"
        )
        data_store.setup()

        # Create in-memory data store
        memory_store = APSDataStore(type="memory")
        memory_store.setup()

        # Create MongoDB data store
        mongo_store = APSDataStore(
            type="mongodb",
            uri="mongodb://localhost:27017",
            schema="scheduler"
        )
        mongo_store.setup()
        ```
    """

    schema: str | None = "flowerpower"

    def __post_init__(self):
        """Initialize and validate the data store configuration.

        This method is called automatically after instance creation. It:
        1. Sets default type to "memory" if not specified
        2. Calls parent class initialization
        3. Validates backend type
        4. Warns about schema limitations with SQLite

        Raises:
            ValueError: If an invalid backend type is specified
        """
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
        self.setup()

    async def _setup_db(self) -> None:
        """Initialize database and schema for SQL backends.

        Creates the database and schema if they don't exist. This is an internal async
        method called by setup_db().

        Raises:
            Exception: If database/schema creation fails
        """
        sqla_engine = create_async_engine(self.uri)

        try:
            await self._create_schema(sqla_engine)
        except Exception:
            await self._create_database_and_schema(sqla_engine)

    async def _create_schema(self, engine: AsyncEngine) -> None:
        """Create schema in existing database if it doesn't exist.

        Args:
            engine: SQLAlchemy async engine connected to the database
        """
        if not self.schema:
            return

        async with engine.begin() as conn:
            await conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {self.schema}"))
            await conn.commit()

    async def _create_database_and_schema(self, engine: AsyncEngine) -> None:
        """Create both database and schema if they don't exist.

        Creates a temporary connection to template1 to create the database,
        then creates the schema within the new database.

        Args:
            engine: SQLAlchemy async engine
        """
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
        """Initialize the database synchronously.

        This is a blocking wrapper around the async _setup_db() method.
        Uses anyio portal to run async code from synchronous context.
        """
        from anyio.from_thread import start_blocking_portal

        with start_blocking_portal() as portal:
            portal.call(self._setup_db)

    def _setup_sqlalchemy(self) -> None:
        """Initialize SQLAlchemy data store.

        Sets up SQLAlchemy engine and data store for PostgreSQL, MySQL, or SQLite.
        Creates database and schema if needed.
        """
        from apscheduler.datastores.sqlalchemy import SQLAlchemyDataStore

        if not self.type.is_sqlite_type:
            self.setup_db()
        self._sqla_engine = create_async_engine(self.uri)
        self._client = SQLAlchemyDataStore(self._sqla_engine, schema=self.schema)

    def _setup_mongodb(self) -> None:
        """Initialize MongoDB data store.

        Creates MongoDBDataStore instance using provided URI and schema (database name).
        """
        from apscheduler.datastores.mongodb import MongoDBDataStore

        self._client = MongoDBDataStore(self.uri, database=self.schema)

    def _setup_memory(self) -> None:
        """Initialize in-memory data store.

        Creates MemoryDataStore instance for temporary storage.
        """
        from apscheduler.datastores.memory import MemoryDataStore

        self._client = MemoryDataStore()

    def setup(self) -> None:
        """Initialize the appropriate data store based on backend type.

        This is the main setup method that should be called after creating the data store.
        It delegates to the appropriate setup method based on the backend type.
        """
        try:
            if self.type.is_sqla_type:
                self._setup_sqlalchemy()
            elif self.type.is_mongodb_type:
                self._setup_mongodb()
            else:
                self._setup_memory()
        except Exception as e:
            logger.info(
                f"Failed to initialize APScheduler data store for type {self.type}: {e}"
            )

            self._client = None
            self._sqla_engine = None

    @property
    def client(self) -> BaseDataStore:
        """Get the initialized data store client.

        Returns:
            BaseDataStore: The APScheduler data store instance, initializing it if needed.
        """
        if self._client is None:
            self.setup()
        return self._client

    @property
    def sqla_engine(self) -> AsyncEngine | None:
        """Get the SQLAlchemy engine.

        Returns:
            AsyncEngine | None: The async SQLAlchemy engine for SQL backends,
                None for non-SQL backends
        """
        if self._sqla_engine is None:
            self.setup()
        return self._sqla_engine


@dataclass  # (slots=True)
class APSEventBroker(BaseBackend):
    """APScheduler event broker implementation supporting multiple messaging backends.

    This class provides a flexible event broker interface for APScheduler that can use
    various messaging systems including PostgreSQL NOTIFY/LISTEN, MQTT, Redis pub/sub,
    and in-memory event handling.

    Attributes:
        type (BackendType): Type of backend messaging system (inherited from BaseBackend)
        uri (str): Connection URI for the backend (inherited from BaseBackend)
        _client (BaseEventBroker): The APScheduler event broker instance
        _sqla_engine (AsyncEngine): SQLAlchemy async engine for PostgreSQL NOTIFY/LISTEN

    Raises:
        ValueError: If an invalid backend type is specified or if SQLAlchemy engine is not PostgreSQL
            when using from_ds_sqla

    Example:
        ```python
        # Create Redis event broker
        redis_broker = APSEventBroker(
            type="redis",
            uri="redis://localhost:6379/0"
        )
        redis_broker.setup()

        # Create MQTT event broker
        mqtt_broker = APSEventBroker(
            type="mqtt",
            uri="mqtt://user:pass@localhost:1883"
        )
        mqtt_broker.setup()

        # Create PostgreSQL event broker from existing SQLAlchemy engine
        pg_broker = APSEventBroker.from_ds_sqla(pg_engine)

        # Create in-memory event broker
        memory_broker = APSEventBroker(type="memory")
        memory_broker.setup()
        ```
    """

    def __post_init__(self):
        """Initialize and validate the event broker configuration.

        This method is called automatically after instance creation. It:
        1. Sets default type to "memory" if not specified
        2. Calls parent class initialization
        3. Validates backend type compatibility

        Raises:
            ValueError: If an invalid backend type is specified or an unsupported
                combination of settings is provided (e.g., Redis without URI)
        """
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
        self.setup()

    def _setup_asyncpg_event_broker(self):
        """Initialize PostgreSQL event broker.

        Sets up AsyncpgEventBroker using either a DSN string or existing SQLAlchemy engine.
        Uses PostgreSQL's NOTIFY/LISTEN for event messaging.
        """
        from apscheduler.eventbrokers.asyncpg import AsyncpgEventBroker

        if self._sqla_engine is None:
            self._client = AsyncpgEventBroker.from_dsn(dsn=self.uri)
        else:
            self._client = AsyncpgEventBroker.from_async_sqla_engine(
                engine=self._sqla_engine
            )

    def _setup_mqtt_event_broker(self):
        """Initialize MQTT event broker.

        Parses MQTT connection URI for host, port, credentials and SSL settings.
        Sets up MQTTEventBroker for pub/sub messaging.
        """
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
        """Initialize Redis event broker.

        Creates RedisEventBroker instance using provided Redis URI.
        Uses Redis pub/sub for event messaging.
        """
        from apscheduler.eventbrokers.redis import RedisEventBroker

        self._client = RedisEventBroker(self.uri)

    def _setup_local_event_broker(self):
        """Initialize in-memory event broker.

        Creates LocalEventBroker for in-process event handling.
        """
        from apscheduler.eventbrokers.local import LocalEventBroker

        self._client = LocalEventBroker()

    def setup(self):
        """Initialize the appropriate event broker based on backend type.

        This is the main setup method that should be called after creating the event broker.
        It delegates to the appropriate setup method based on the backend type.
        """
        try:
            if self.type.is_sqla_type:
                self._setup_asyncpg_event_broker()
            elif self.type.is_mqtt_type:
                self._setup_mqtt_event_broker()
            elif self.type.is_redis_type:
                self._setup_redis_event_broker()
            else:
                self._setup_local_event_broker()
        except Exception as e:
            logger.info(
                f"Failed to initialize APScheduler event broker for type {self.type}: {e}"
            )
            self._client = None
            self._sqla_engine = None

    @property
    def client(self) -> BaseEventBroker:
        """Get the initialized event broker client.

        Returns:
            BaseEventBroker: The APScheduler event broker instance, initializing it if needed.
        """
        if self._client is None:
            self.setup()
        return self._client

    @property
    def sqla_engine(self) -> AsyncEngine | None:
        """Get the SQLAlchemy engine.

        Returns:
            AsyncEngine | None: The async SQLAlchemy engine for PostgreSQL backend,
                None for other backends
        """
        if self._sqla_engine is None:
            self.setup()
        return self._sqla_engine

    @classmethod
    def from_ds_sqla(cls, sqla_engine: AsyncEngine) -> "APSEventBroker":
        """Create event broker from existing SQLAlchemy engine.

        This factory method creates a PostgreSQL event broker that shares the
        same database connection as a data store.

        Args:
            sqla_engine: Async SQLAlchemy engine, must be PostgreSQL with asyncpg driver

        Returns:
            APSEventBroker: New event broker instance using the provided engine

        Raises:
            ValueError: If engine is not PostgreSQL with asyncpg driver

        Example:
            ```python
            # Create data store with PostgreSQL
            data_store = APSDataStore(
                type="postgresql",
                uri="postgresql+asyncpg://user:pass@localhost/db"
            )
            data_store.setup()

            # Create event broker using same connection
            event_broker = APSEventBroker.from_ds_sqla(data_store.sqla_engine)
            ```
        """
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
    """Main backend configuration class for APScheduler combining data store and event broker.

    This class serves as a container for configuring both the data store and event broker
    components of APScheduler. It handles initialization and setup of both components,
    with support for dictionary-based configuration.

    Args:
        data_store (APSDataStore | dict | None): Data store configuration, either as an
            APSDataStore instance or a configuration dictionary. Defaults to a new
            APSDataStore instance.
        event_broker (APSEventBroker | dict | None): Event broker configuration, either as
            an APSEventBroker instance or a configuration dictionary. Defaults to a new
            APSEventBroker instance.
        cleanup_interval (int): Interval in seconds for cleaning up old jobs. Defaults to 300.
        max_concurrent_jobs (int): Maximum number of jobs that can run concurrently.
        default_job_executor (str): Default job executor to use. Defaults to "threadpool".

    Example:
        ```python
        # Create backend with default memory storage
        backend = APSBackend()

        # Create backend with PostgreSQL data store and Redis event broker
        backend = APSBackend(
            data_store={
                "type": "postgresql",
                "uri": "postgresql+asyncpg://user:pass@localhost/db",
                "schema": "scheduler"
            },
            event_broker={
                "type": "redis",
                "uri": "redis://localhost:6379/0"
            }
        )

        # Create backend with PostgreSQL for both data store and event broker
        backend = APSBackend(
            data_store={
                "type": "postgresql",
                "uri": "postgresql+asyncpg://user:pass@localhost/db",
            },
            event_broker={
                "from_ds_sqla": True  # Use same PostgreSQL connection for events
            }
        )
        ```
    """

    data_store: APSDataStore | dict | None = field(default_factory=APSDataStore)
    event_broker: APSEventBroker | dict | None = field(default_factory=APSEventBroker)
    cleanup_interval: int = field(default=300)
    max_concurrent_jobs: int = field(default=10)
    default_job_executor: str = field(default="threadpool")

    def __post_init__(self):
        """Initialize and setup data store and event broker components.

        Called automatically after instance creation. This method:
        1. Converts data store dict to APSDataStore instance if needed
        2. Initializes data store
        3. Converts event broker dict to APSEventBroker instance if needed
        4. Sets up event broker using data store connection if specified
        5. Initializes event broker
        """
        if self.data_store is not None:
            if isinstance(self.data_store, dict):
                self.data_store = APSDataStore.from_dict(self.data_store)
                # self.data_store.setup()
        if self.event_broker is not None:
            if isinstance(self.event_broker, dict):
                if (
                    "from_ds_sqla" in self.event_broker
                    and self.data_store._sqla_engine is not None
                ):
                    self.event_broker = APSEventBroker.from_ds_sqla(
                        self.data_store._sqla_engine
                    )
                else:
                    self.event_broker.pop("from_ds_sqla", None)
                    self.event_broker = APSEventBroker.from_dict(self.event_broker)
                # self.event_broker.setup()

        if self.data_store._client is None or self.event_broker._client is None:
            logger.warning(
                "APSBackend is not fully initialized. Job Queue is not available."
            )
