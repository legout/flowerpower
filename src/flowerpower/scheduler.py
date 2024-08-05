import sys
import importlib.util

if importlib.util.find_spec("apscheduler"):
    from apscheduler import Scheduler, current_scheduler
else:
    raise ImportError(
        "APScheduler is not installed. Please install it using `pip install"
        "'apscheduler>4.0.0a1'`, 'conda install apscheduler4' or `pip install flowerpower[scheduler]`"
    )

from .cfg import Config
import os
from loguru import logger
import uuid
from typing import Any


class SchedulerManager:
    def __init__(
        self,
        name: str | None = None,
        base_path: str | None = None,
        conf_path: str | None = None,
        pipelines_path: str = None,
    ):
        self.name = name

        if base_path is None:
            base_path = os.getcwd()

        self._base_path = base_path
        self._conf_path = os.path.join(base_path, "conf") or conf_path
        self._pipelines_path = os.path.join(base_path, "pipelines") or pipelines_path

        cfg = Config(path=self._conf_path)

        self._scheduler_params = cfg.scheduler
        self.data_store = None
        self.event_broker = None
        self._sqla_engine = None
        self.scheduler = None

        sys.path.append(self._pipelines_path)

    def setup_data_store(self):
        if "data_store" in self._scheduler_params:
            if "type" in self._scheduler_params.data_store:
                if self._scheduler_params.data_store.type == "sqlalchemy":
                    self._setup_sqlalchemy_data_store()
                elif self._scheduler_params.data_store.type == "mongodb":
                    self._setup_mongodb_data_store()
                else:
                    self._setup_memory_data_store()

    def _setup_sqlalchemy_data_store(self):
        from apscheduler.datastores.sqlalchemy import SQLAlchemyDataStore
        from sqlalchemy.ext.asyncio import create_async_engine

        if "url" not in self._scheduler_params.data_store:
            raise ValueError("No URL specified for SQLAlchemy data_store")
        self._sqla_engine = create_async_engine(self._scheduler_params.data_store.url)
        self.data_store = SQLAlchemyDataStore(engine_or_url=self._sqla_engine)

    def _setup_mongodb_data_store(self):
        from apscheduler.datastores.mongodb import MongoDBDataStore

        if "url" not in self._scheduler_params.data_store:
            raise ValueError("No URL specified for MongoDB data_store")
        self.data_store = MongoDBDataStore(self._scheduler_params.data_store.url)

    def _setup_memory_data_store(self):
        from apscheduler.datastores.memory import MemoryDataStore

        self.data_store = MemoryDataStore()

    def setup_event_broker(self):
        if "event_broker" in self._scheduler_params:
            if "type" in self._scheduler_params.event_broker:
                if self._scheduler_params.event_broker.type == "asyncpg":
                    self._setup_asyncpg_event_broker()
                elif self._scheduler_params.event_broker.type == "mqtt":
                    self._setup_mqtt_event_broker()
                elif self._scheduler_params.event_broker.type == "redis":
                    self._setup_redis_event_broker()
                else:
                    self._setup_local_event_broker()

    def _setup_asyncpg_event_broker(self):
        from apscheduler.eventbrokers.asyncpg import AsyncpgEventBroker

        if self._sqla_engine is None:
            if "url" not in self._scheduler_params.event_broker:
                raise ValueError("No URL specified for AsyncPG event broker")
            self.event_broker = AsyncpgEventBroker.from_dsn(
                dsn=self._scheduler_params.event_broker.url
            )
        else:
            self.event_broker = AsyncpgEventBroker.from_async_sqla_engine(
                engine=self._sqla_engine
            )

    def _setup_mqtt_event_broker(self):
        from apscheduler.eventbrokers.mqtt import MQTTEventBroker

        host = self._scheduler_params.event_broker.get("host", "localhost")
        port = self._scheduler_params.event_broker.get("port", 1883)
        self.event_broker = MQTTEventBroker(host, port, topic="flowerpower/scheduler")
        if (
            "username" in self._scheduler_params.event_broker
            and "password" in self._scheduler_params.event_broker
        ):
            self.event_broker._client.username_pw_set(
                self._scheduler_params.event_broker.username,
                self._scheduler_params.event_broker.password,
            )

    def _setup_redis_event_broker(self):
        from apscheduler.eventbrokers.redis import RedisEventBroker

        if "host" in self._scheduler_params.event_broker:
            port = self._scheduler_params.event_broker.get("port", 6379)
            self._scheduler_params.event_broker.url = (
                f"redis://{self._scheduler_params.event_broker.host}:{port}"
            )
        url = self._scheduler_params.event_broker.get("url", "redis://localhost:6379")
        self.event_broker = RedisEventBroker(url)

    def _setup_local_event_broker(self):
        from apscheduler.eventbrokers.local import LocalEventBroker

        self.event_broker = LocalEventBroker()

    def init_scheduler(self, **kwargs) -> Scheduler:
        self.setup_data_store()
        self.setup_event_broker()
        self.scheduler = Scheduler(
            data_store=self.data_store,
            event_broker=self.event_broker,
            identity=self.name,
            logger=logger,
            **kwargs,
        )
        # return self.scheduler

    def start_scheduler(self, background: bool = False, *args, **kwargs):
        if not self.scheduler:
            self.init_scheduler(*args, **kwargs)
        if background:
            self.scheduler.start_in_background()
        else:
            self.scheduler.run_until_stopped()
        # return self.scheduler

    def get_current_scheduler(self):
        if not self.scheduler:
            self.scheduler = current_scheduler.get()

    def stop_scheduler(self):
        if not self.scheduler:
            self.get_current_scheduler()
        self.scheduler.stop()

    def remove_all_schedules(self):
        if not self.scheduler:
            self.init_scheduler()
        for sched in self.scheduler.get_schedules():
            self.scheduler.remove_schedule(sched.id)
        # return self.scheduler

    def add_schedule(self, *args, **kwargs) -> uuid.UUID:
        if not self.scheduler:
            self.init_scheduler()
        return self.scheduler.add_schedule(*args, **kwargs)
        # return self.scheduler

    def add_job(self, *args, **kwargs) -> uuid.UUID:
        if not self.scheduler:
            self.init_scheduler()
        return self.scheduler.add_job(*args, **kwargs)

    def run_job(self, *args, **kwargs) -> Any:
        if not self.scheduler:
            self.init_scheduler()
        return self.scheduler.run_job(*args, **kwargs)
        # return self.scheduler


# Wrapper functions for backward compatibility
def get_scheduler(
    name: str | None = None,
    path: str | None = None,
    conf_path: str | None = None,
    pipelines_path: str = None,
    *args,
    **kwargs,
) -> Scheduler:
    manager = SchedulerManager(name, path, conf_path, pipelines_path)
    manager.init_scheduler(*args, **kwargs)
    return manager.scheduler


def start_scheduler(
    name: str | None = None,
    path: str | None = None,
    conf_path: str | None = None,
    pipelines_path: str = None,
    background: bool = False,
    *args,
    **kwargs,
) -> Scheduler:
    manager = SchedulerManager(name, path, conf_path, pipelines_path)
    manager.start_scheduler(background, *args, **kwargs)
    return manager.scheduler


def get_current_scheduler() -> Scheduler | None:
    return SchedulerManager.get_current_scheduler()


# def stop_scheduler():
#    SchedulerManager.stop_scheduler()


def remove_all_schedules(
    name: str | None = None,
    path: str | None = None,
    conf_path: str | None = None,
    pipelines_path: str = None,
):
    manager = SchedulerManager(name, path, conf_path, pipelines_path)
    return manager.remove_all_schedules()


def add_schedule(
    name: str | None = None,
    path: str | None = None,
    conf_path: str | None = None,
    pipelines_path: str = None,
    *args,
    **kwargs,
) -> uuid.UUID:
    manager = SchedulerManager(name, path, conf_path, pipelines_path)
    return manager.add_schedule(*args, **kwargs)


def add_job(
    name: str | None = None,
    path: str | None = None,
    conf_path: str | None = None,
    pipelines_path: str = None,
    *args,
    **kwargs,
) -> uuid.UUID:
    manager = SchedulerManager(name, path, conf_path, pipelines_path)
    return manager.add_job(*args, **kwargs)


def run_job(
    name: str | None = None,
    path: str | None = None,
    conf_path: str | None = None,
    pipelines_path: str = None,
    *args,
    **kwargs,
) -> Any:
    manager = SchedulerManager(name, path, conf_path, pipelines_path)
    return manager.run_job(*args, **kwargs)
