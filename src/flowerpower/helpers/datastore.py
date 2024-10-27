ALL_DATA_STORES = [
    "sqlalchemy",
    "sqlite",
    "postgresql",
    "mysql",
    "mongodb",
    "local",
    "memory",
]


class DataStore:
    def __init__(self, type: str | None = None, engine_or_uri: str | None = None):
        self.type = type or "memory"
        self.engine_or_uri = engine_or_uri
        self.sqla_engine = None

        if self.type not in ALL_DATA_STORES:
            raise ValueError(
                f"Invalid data store type: {type}. Valid data store types are: {ALL_DATA_STORES}"
            )
        if (
            type in ["sqlalchemy", "sqlite", "postgresql", "mysql", "mongodb"]
            and not engine_or_uri
        ):
            raise ValueError(f"Data store type {type} requires an engine or uri")

    def _setup_sqlalchemy(self):
        from apscheduler.datastores.sqlalchemy import SQLAlchemyDataStore
        from sqlalchemy.ext.asyncio import create_async_engine

        self.sqla_engine = create_async_engine(self.engine_or_uri)
        self._data_store = SQLAlchemyDataStore(self.sqla_engine)

    def _setup_mongodb(self, uri: str):
        from apscheduler.datastores.mongodb import MongoDBDataStore

        self._data_store = MongoDBDataStore(self.engine_or_uri)

    def _setup_memory(self):
        from apscheduler.datastores.memory import MemoryDataStore

        self._data_store = MemoryDataStore()

    def setup(
        self,
    ):
        if self.type in ["sqlalchemy", "sqlite", "postgresql", "mysql"]:
            self._setup_sqlalchemy()
        elif self.type == "mongodb":
            self._setup_mongodb()
        else:
            self._setup_memory()

    def get(self) -> tuple:
        return self._data_store, self.sqla_engine


def setup_data_store(type: str, engine_or_uri: str) -> tuple:
    ds = DataStore(type=type, engine_or_uri=engine_or_uri)
    ds.setup()
    return ds.get()
