from apscheduler import Scheduler
from apscheduler.datastores.sqlalchemy import SQLAlchemyDataStore
from apscheduler.eventbrokers.redis import RedisEventBroker
from apscheduler.eventbrokers.asyncpg import AsyncpgEventBroker


class SM(Scheduler):
    def __init__(self, name, ds_uri, eb_uri):
        self.name = name
        self._data_store = SQLAlchemyDataStore(engine_or_url=ds_uri)
        if "redis" in eb_uri:
            self._event_broker = RedisEventBroker(eb_uri)
        else:
            self._event_broker = AsyncpgEventBroker.from_async_sqla_engine(
                self._data_store._engine
            )
        
        super().__init__(
            identity=self.name,
            data_store=self._data_store,
            event_broker=self._event_broker,
            #job_executors=self._job_executors,
        )


class TestJob:
    
    def __init__(self, name):
        self.name = name

    def run(self, *args, **kwargs):
        print(self.name, args, kwargs)

    def add_job(self, *args, **kwargs):
        with SM(
            name="test",
            #ds_uri="sqlite+aiosqlite:///test.db",
            ds_uri="postgresql+asyncpg://edge:edge@localhost:5432/flowerpower", 
            eb_uri="redis://localhost:6379",
        ) as sched:
            sched.add_job(self.run, args=args, kwargs=kwargs)
