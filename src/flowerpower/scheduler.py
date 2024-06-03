import sys

from apscheduler import Scheduler

from .cfg import load_scheduler_cfg

SCHEDULER = load_scheduler_cfg()


def get_scheduler(
    conf_path: str | None = None, pipelines_path: str = "pipelines"
) -> Scheduler:
    sys.path.append(pipelines_path)
    data_store = None
    event_broker = None
    engine = None
    if "data_store" in SCHEDULER:
        if "type" in SCHEDULER.data_store:
            if SCHEDULER.data_store.type == "sqlalchemy":
                from apscheduler.datastores.sqlalchemy import \
                    SQLAlchemyDataStore
                from sqlalchemy.ext.asyncio import create_async_engine

                if "url" not in SCHEDULER.data_store:
                    raise ValueError("No URL specified for SQLAlchemy data_store")
                engine = create_async_engine(SCHEDULER.data_store.url)
                data_store = SQLAlchemyDataStore(engine_or_url=engine)

            elif SCHEDULER.data_store.type == "mongodb":
                from apscheduler.datastores.mongodb import MongoDBDataStore

                if "url" not in SCHEDULER.data_store:
                    raise ValueError("No URL specified for MongoDB data_store")
                data_store = MongoDBDataStore(SCHEDULER.data_store.url)

            else:
                from apscheduler.datastores.memory import MemoryDataStore

                data_store = MemoryDataStore()

    if "event_broker" in SCHEDULER:
        if "type" in SCHEDULER.event_broker:
            if SCHEDULER.event_broker.type == "asyncpg":
                from apscheduler.eventbrokers.asyncpg import AsyncpgEventBroker

                if engine is None:
                    from sqlalchemy.ext.asyncio import create_async_engine

                    if "url" not in SCHEDULER.event_broker:
                        raise ValueError("No URL specified for AsyncPG event broker")

                    engine = create_async_engine(SCHEDULER.event_broker.url)
                event_broker = AsyncpgEventBroker.from_async_sqla_engine(engine=engine)

            elif SCHEDULER.event_broker.type == "mqtt":
                from apscheduler.eventbrokers.mqtt import MQTTEventBroker

                if "host" not in SCHEDULER.event_broker:
                    raise ValueError("No host specified for MQTT event broker")
                if "port" not in SCHEDULER.event_broker:
                    raise ValueError("No port specified for MQTT event broker")
                event_broker = MQTTEventBroker(
                    SCHEDULER.event_broker.host, SCHEDULER.event_broker.port
                )
                if (
                    "username" in SCHEDULER.event_broker
                    and "password" in SCHEDULER.event_broker
                ):
                    event_broker._client.username_pw_set(
                        SCHEDULER.event_broker.username, SCHEDULER.event_broker.password
                    )
            elif SCHEDULER.event_broker.type == "redis":
                from apscheduler.eventbrokers.redis import RedisEventBroker

                if "host" not in SCHEDULER.event_broker:
                    raise ValueError("No host specified for Redis event broker")
                if "port" not in SCHEDULER.event_broker:
                    raise ValueError("No port specified for Redis event broker")
                event_broker = RedisEventBroker(
                    SCHEDULER.event_broker.host, SCHEDULER.event_broker.port
                )
            else:
                from apscheduler.eventbrokers.local import LocalEventBroker

                event_broker = LocalEventBroker()

    scheduler = Scheduler(data_store=data_store, event_broker=event_broker)

    return scheduler


def start_scheduler(
    conf_path: str | None = None,
    pipelines_path: str = "pipelines",
    background: bool = True,
):
    # sys.path.append(pipelines_path)
    scheduler = get_scheduler(conf_path=conf_path, pipelines_path=pipelines_path)
    if background:
        scheduler.start_in_background()
    else:
        scheduler.run_until_stopped()
    return scheduler


def remove_all_schedules(
    conf_path: str | None = None, pipelines_path: str = "pipelines"
):
    scheduler = get_scheduler(conf_path=conf_path)
    for sched in scheduler.get_schedules():
        scheduler.remove_schedule(sched.id)

    return scheduler


def add_schedule(
    conf_path: str | None = None, pipelines_path: str = "pipelines", **kwargs
):
    scheduler = get_scheduler(conf_path=conf_path, pipelines_path=pipelines_path)
    scheduler.add_schedule(**kwargs)
    return scheduler


def add_job(conf_path: str | None = None, pipelines_path: str = "pipelines", **kwargs):
    scheduler = get_scheduler(conf_path=conf_path, pipelines_path=pipelines_path)
    scheduler.add_job(**kwargs)
    return scheduler
