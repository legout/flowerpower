from .config import load_scheduler_params
from apscheduler import Scheduler


def configure_scheduler(path: str | None = None) -> Scheduler:

    PARAMS = load_scheduler_params(path=path)

    data_store = None
    event_broker = None
    engine = None
    if "data_store" in PARAMS:
        if "type" in PARAMS.data_store:
            if PARAMS.data_store.type == "sqlalchemy":
                from apscheduler.datastores.sqlalchemy import SQLAlchemyDataStore
                from sqlalchemy.ext.asyncio import create_async_engine

                if "url" not in PARAMS.data_store:
                    raise ValueError("No URL specified for SQLAlchemy data_store")
                engine = create_async_engine(PARAMS.data_store.url)
                data_store = SQLAlchemyDataStore(engine_or_url=engine)

            elif PARAMS.data_store.type == "mongodb":
                from apscheduler.datastores.mongodb import MongoDBdata_store

                if "url" not in PARAMS.data_store:
                    raise ValueError("No URL specified for MongoDB data_store")
                data_store = MongoDBdata_store(PARAMS.data_store.url)

            else:
                from apscheduler.datastores.memory import Memorydata_store

                data_store = Memorydata_store()

    if "event_broker" in PARAMS:
        if "type" in PARAMS.event_broker:
            if PARAMS.event_broker.type == "asyncpg":
                from apscheduler.eventbrokers.asyncpg import AsyncpgEventBroker

                if engine is None:
                    from sqlalchemy.ext.asyncio import create_async_engine

                    if "url" not in PARAMS.event_broker:
                        raise ValueError("No URL specified for AsyncPG event broker")

                    engine = create_async_engine(PARAMS.event_broker.url)
                event_broker = AsyncpgEventBroker.from_async_sqla_engine(engine=engine)

            elif PARAMS.event_broker.type == "mqtt":
                from apscheduler.eventbrokers.mqtt import MQTTEventBroker

                if "host" not in PARAMS.event_broker:
                    raise ValueError("No host specified for MQTT event broker")
                if "port" not in PARAMS.event_broker:
                    raise ValueError("No port specified for MQTT event broker")
                event_broker = MQTTEventBroker(
                    PARAMS.event_broker.host, PARAMS.event_broker.port
                )
                if (
                    "username" in PARAMS.event_broker
                    and "password" in PARAMS.event_broker
                ):
                    event_broker._client.username_pw_set(
                        PARAMS.event_broker.username, PARAMS.event_broker.password
                    )
            elif PARAMS.event_broker.type == "redis":
                from apscheduler.eventbrokers.redis import RedisEventBroker

                if "host" not in PARAMS.event_broker:
                    raise ValueError("No host specified for Redis event broker")
                if "port" not in PARAMS.event_broker:
                    raise ValueError("No port specified for Redis event broker")
                event_broker = RedisEventBroker(
                    PARAMS.event_broker.host, PARAMS.event_broker.port
                )
            else:
                from apscheduler.eventbrokers.local import LocalEventBroker

                event_broker = LocalEventBroker()

    scheduler = Scheduler(data_store=data_store, event_broker=event_broker)

    return scheduler

