from test_job import TestJob
from apscheduler import Scheduler
from apscheduler.datastores.sqlalchemy import SQLAlchemyDataStore
from apscheduler.eventbrokers.redis import RedisEventBroker

def main():
    data_store = SQLAlchemyDataStore(engine_or_url="postgresql+asyncpg://edge:edge@localhost:5432/flowerpower")
    event_broker = RedisEventBroker("redis://localhost:6379")
    with Scheduler(data_store, event_broker) as sched:
        sched.run_until_stopped()

if __name__ == "__main__":
    main()