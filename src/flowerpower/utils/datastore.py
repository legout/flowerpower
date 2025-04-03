ALL_DATA_STORES = [
    "sqlalchemy",
    "asyncpg",
    "psycopg2",
    "postgresql",
    "sqlite",
    "sqlite3",
    "mysql",
    "mongodb",
    "local",
    "memory",
]


class DataStore:
    def __init__(
        self,
        type: str | None = None,
        engine_or_uri: str | None = None,
        schema: str | None = "flowerpower",
        username: str | None = None,
        password: str | None = None,
        ssl: bool = False,
        **kwargs,
    ):
        self.type = type or "memory"
        self.engine_or_uri = engine_or_uri
        self.sqla_engine = None
        self.schema = schema
        self.username = username
        self.password = password
        self.ssl = ssl
        self._kwargs = kwargs

        if self.type not in ALL_DATA_STORES:
            raise ValueError(
                f"Invalid data store type: {type}. Valid data store types are: {ALL_DATA_STORES}"
            )
        if (
            type
            in [
                "sqlalchemy",
                "postgresql",
                "asyncpg",
                "psycopg2",
                "sqlite",
                "sqlite3",
                "mysql",
                "mongodb",
            ]
            and not engine_or_uri
        ):
            raise ValueError(f"Data store type {type} requires an engine or uri")

    def _gen_uri(self):
        import urllib.parse

        if self.password and "@" not in self.engine_or_uri:
            if not self.username:
                raise ValueError(
                    "Data store type `sqlalchemy` requires a username when a password is provided"
                )
            password = urllib.parse.quote(self.password)
            self.engine_or_uri = self.engine_or_uri.replace(
                "://", f"://{self.username}:{password}@"
            )
        if self.ssl and "?ssl" not in self.engine_or_uri:
            self.engine_or_uri = self.engine_or_uri + "?ssl=allow"

        # asyncio.run(self.setup_db())
        # self.setup_db()

    def _setup_sqlalchemy(self):
        from apscheduler.datastores.sqlalchemy import SQLAlchemyDataStore
        from sqlalchemy.ext.asyncio import create_async_engine

        self._gen_uri()
        self.setup_db()
        self.sqla_engine = create_async_engine(self.engine_or_uri)
        self._data_store = SQLAlchemyDataStore(self.sqla_engine, schema=self.schema)

    def _setup_mongodb(self, uri: str):
        from apscheduler.datastores.mongodb import MongoDBDataStore

        self._data_store = MongoDBDataStore(self.engine_or_uri, database=self.schema)

    def _setup_memory(self):
        from apscheduler.datastores.memory import MemoryDataStore

        self._data_store = MemoryDataStore()

    def setup(
        self,
    ):
        if self.type in [
            "sqlalchemy",
            "sqlite",
            "postgresql",
            "asyncpg",
            "psychopg2",
            "sqlite3",
            "mysql",
        ]:
            self._setup_sqlalchemy()
        elif self.type == "mongodb":
            self._setup_mongodb()
        else:
            self._setup_memory()

    def get(self) -> tuple:
        return self._data_store, self.sqla_engine

    async def _setup_db(self):
        from sqlalchemy import text
        from sqlalchemy.ext.asyncio import create_async_engine

        self._gen_uri()
        sqla_engine = create_async_engine(self.engine_or_uri)
        try:
            async with sqla_engine.begin() as conn:
                if self.schema:
                    await conn.execute(
                        text(f"CREATE SCHEMA IF NOT EXISTS {self.schema}")
                    )
                    await conn.commit()
        except Exception as e:
            _ = e
            database_name = self.engine_or_uri.split("/")[-1].split("?")[0]
            temp_engine = create_async_engine(
                self.engine_or_uri.replace(f"/{database_name}", "/template1")
            )
            async with temp_engine.begin() as conn:
                await conn.execute(text("COMMIT"))
                try:
                    await conn.execute(text(f"CREATE DATABASE {database_name}"))
                # await conn.commit()
                except Exception as e:
                    _ = e
                    pass
                finally:
                    await conn.execute(text("COMMIT"))
            if self.schema:
                async with sqla_engine.begin() as conn:
                    await conn.execute(
                        text(f"CREATE SCHEMA IF NOT EXISTS {self.schema}")
                    )
                    await conn.commit()

    def setup_db(self):
        from anyio.from_thread import start_blocking_portal

        with start_blocking_portal() as portal:
            portal.call(self._setup_db)


def setup_data_store(
    type: str,
    engine_or_uri: str,
    schema: str | None = "flowerpower",
    username: str | None = None,
    password: str | None = None,
    ssl: bool = False,
    **kwargs,
) -> tuple:

    # ds = DataStore(
    #    type=type,
    #    engine_or_uri=engine_or_uri,
    #    schema=schema,
    #    username=username,
    #    password=password,
    #    ssl=ssl,
    #    **kwargs,
    # )
    # ds.setup_db()
    ds2 = DataStore(
        type=type,
        engine_or_uri=engine_or_uri,
        schema=schema,
        username=username,
        password=password,
        ssl=ssl,
        **kwargs,
    )
    ds2.setup()
    return ds2.get()
