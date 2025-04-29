from apscheduler.datastores.base import BaseDataStore
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from ...base import BackendType, BaseBackend


class APSDataStoreType(BackendType):
    POSTGRESQL = "postgresql"
    SQLITE = "sqlite"
    MYSQL = "mysql"
    MONGODB = "mongodb"
    MEMORY = "memory"


class APSDataStore(BaseBackend):
    """Data store for APScheduler."""

    def __post_init__(self):
        super().__post_init__(backend_type=APSDataStoreType)
        self._validate_inputs()

    @classmethod
    def from_dict(cls, d: dict[str, any]) -> "APSDataStore":
        return cls(**d)

    def _validate_inputs(self) -> None:
        if self.type.value not in [ds.value for ds in APSDataStoreType]:
            raise ValueError(
                f"Invalid data store type: {self.type}. Valid types: {[ds.value for ds in APSDataStoreType]}"
            )

    async def _setup_db(self) -> None:
        sqla_engine = create_async_engine(self.uri)

        try:
            await self._create_schema(sqla_engine)
        except Exception:
            await self._create_database_and_schema(sqla_engine)

    async def _create_schema(self, engine: AsyncEngine) -> None:
        if not self.schema_or_queue:
            return

        async with engine.begin() as conn:
            await conn.execute(
                text(f"CREATE SCHEMA IF NOT EXISTS {self.schema_or_queue}")
            )
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

        if self.schema_or_queue:
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
        self._client = SQLAlchemyDataStore(
            self._sqla_engine, schema=self.schema_or_queue
        )

    def _setup_mongodb(self) -> None:
        from apscheduler.datastores.mongodb import MongoDBDataStore

        self._client = MongoDBDataStore(self.uri, database=self.schema_or_queue)

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
