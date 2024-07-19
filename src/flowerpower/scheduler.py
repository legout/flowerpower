import sys
import importlib.util

if importlib.util.find_spec("apscheduler"):
    # from hamilton.execution import executors
    from apscheduler import Scheduler, current_scheduler
else:
    raise ImportError(
        "APScheduler is not installed. Please install it using `pip install"
        "'apscheduler>4.0.0a1'`, 'conda install apscheduler4' or `pip install flowerpower[apscheduler]`"
    )

from .cfg import load_scheduler_cfg


def get_scheduler(
    conf_path: str | None = "conf", pipelines_path: str | None = "pipelines", **kwargs
) -> Scheduler:
    scheduler_params = load_scheduler_cfg(path=conf_path)
    pipelines_path = scheduler_params.get("path", None) or pipelines_path

    sys.path.append(pipelines_path)

    data_store = None
    event_broker = None
    engine = None

    if "data_store" in scheduler_params:
        if "type" in scheduler_params.data_store:
            if scheduler_params.data_store.type == "sqlalchemy":
                from apscheduler.datastores.sqlalchemy import SQLAlchemyDataStore
                from sqlalchemy.ext.asyncio import create_async_engine

                if "url" not in scheduler_params.data_store:
                    raise ValueError("No URL specified for SQLAlchemy data_store")
                engine = create_async_engine(scheduler_params.data_store.url)
                data_store = SQLAlchemyDataStore(engine_or_url=engine)

            elif scheduler_params.data_store.type == "mongodb":
                from apscheduler.datastores.mongodb import MongoDBDataStore

                if "url" not in scheduler_params.data_store:
                    raise ValueError("No URL specified for MongoDB data_store")
                data_store = MongoDBDataStore(scheduler_params.data_store.url)

            else:
                from apscheduler.datastores.memory import MemoryDataStore

                data_store = MemoryDataStore()

    if "event_broker" in scheduler_params:
        if "type" in scheduler_params.event_broker:
            if scheduler_params.event_broker.type == "asyncpg":
                from apscheduler.eventbrokers.asyncpg import AsyncpgEventBroker

                if engine is None:
                    if "url" not in scheduler_params.event_broker:
                        raise ValueError("No URL specified for AsyncPG event broker")

                    event_broker = AsyncpgEventBroker.from_dsn(
                        dsn=scheduler_params.event_broker.url
                    )
                else:
                    event_broker = AsyncpgEventBroker.from_async_sqla_engine(
                        engine=engine
                    )

            elif scheduler_params.event_broker.type == "mqtt":
                from apscheduler.eventbrokers.mqtt import MQTTEventBroker

                if "host" not in scheduler_params.event_broker:
                    scheduler_params.event_broker.host = "localhost"
                    # raise ValueError("No host specified for MQTT event broker")
                if "port" not in scheduler_params.event_broker:
                    scheduler_params.event_broker.port = 1883
                    # raise ValueError("No port specified for MQTT event broker")
                event_broker = MQTTEventBroker(
                    scheduler_params.event_broker.host,
                    scheduler_params.event_broker.port,
                    topic="flowerpower/scheduler",
                )
                if (
                    "username" in scheduler_params.event_broker
                    and "password" in scheduler_params.event_broker
                ):
                    event_broker._client.username_pw_set(
                        scheduler_params.event_broker.username,
                        scheduler_params.event_broker.password,
                    )
            elif scheduler_params.event_broker.type == "redis":
                from apscheduler.eventbrokers.redis import RedisEventBroker

                if "host" in scheduler_params.event_broker:
                    if "port" not in scheduler_params.event_broker:
                        scheduler_params.event_broker.port = 6379
                    scheduler_params.event_broker.url = f"redis://{scheduler_params.event_broker.host}:{scheduler_params.event_broker.port}"
                if scheduler_params.event_broker.url is None:
                    scheduler_params.event_broker.url = "redis://localhost:6379"
                event_broker = RedisEventBroker(scheduler_params.event_broker.url)
            else:
                from apscheduler.eventbrokers.local import LocalEventBroker

                event_broker = LocalEventBroker()

    scheduler = Scheduler(data_store=data_store, event_broker=event_broker, **kwargs)

    return scheduler


def start_scheduler(
    conf_path: str | None = "conf",
    pipelines_path: str = "pipelines",
    background: bool = False,
):
    # sys.path.append(pipelines_path)
    scheduler = get_scheduler(conf_path=conf_path, pipelines_path=pipelines_path)
    if background:
        scheduler.start_in_background()
    else:
        scheduler.run_until_stopped()
    return scheduler


def get_current_scheduler():
    return current_scheduler.get()


def stop_scheduler():
    scheduler = get_current_scheduler()
    scheduler.stop()


def remove_all_schedules(
    conf_path: str | None = "conf", pipelines_path: str = "pipelines"
):
    scheduler = get_scheduler(conf_path=conf_path)
    for sched in scheduler.get_schedules():
        scheduler.remove_schedule(sched.id)

    return scheduler


def add_schedule(
    conf_path: str | None = "conf", pipelines_path: str = "pipelines", **kwargs
):
    scheduler = get_scheduler(conf_path=conf_path, pipelines_path=pipelines_path)
    scheduler.add_schedule(**kwargs)
    return scheduler


def add_job(
    conf_path: str | None = "conf", pipelines_path: str = "pipelines", **kwargs
):
    scheduler = get_scheduler(conf_path=conf_path, pipelines_path=pipelines_path)
    scheduler.add_job(**kwargs)
    return scheduler
