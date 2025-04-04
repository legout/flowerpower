# Configuration models for APScheduler triggers and run settings have been removed.
# Scheduling is now configured by passing 'trigger_type' and 'trigger_args'
# directly to the PipelineManager.schedule() or Pipeline.schedule() methods.
#
# Example trigger_args:
# - trigger_type='cron': {'cron_string': '0 * * * *', ...}
# - trigger_type='interval': {'seconds': 3600, 'repeat': 5, ...}
# - trigger_type='date'/'at': {'scheduled_time': datetime_object, ...}
#
# Refer to the rq-scheduler documentation and the schedule() method docstrings
# for available arguments for each trigger type.

# Placeholder class (optional, could be removed entirely if not referenced elsewhere)
# from ..base import BaseConfig
# class PipelineScheduleConfig(BaseConfig):
#    pass
