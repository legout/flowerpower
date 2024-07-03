# from apscheduler import (
#     Event,
#     JobAcquired,
#     JobAdded,
#     JobRemoved,
#     JobDeserializationFailed,
#     ScheduleAdded,
#     ScheduleDeserializationFailed,
#     ScheduleRemoved,
#     SchedulerStopped,
#     SchedulerStarted,
#     ScheduleUpdated,
#     TaskAdded,
#     TaskRemoved,
#     TaskUpdated,
# )
# from loguru import logger

# def job_added(event: Event):
#     logger.info(event.timestamp)
#     logger.info(event.job_id)
#     logger.info(event.task_id)
#     logger.info(event.schedule_id)
