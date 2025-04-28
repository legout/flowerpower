from typing import Any, Dict

from ..base import BaseTrigger


class RQTrigger(BaseTrigger):
    """
    RQTrigger adapts trigger logic for the RQ worker backend.

    Inherits from BaseTrigger and provides a trigger instance
    in dictionary format suitable for RQ scheduling.
    """

    def __init__(self, trigger_type: str):
        super().__init__(trigger_type)

    def get_trigger_instance(self, **kwargs) -> Dict[str, Any]:
        """
        Get trigger parameters for RQ Scheduler.

        Args:
            **kwargs: Keyword arguments for the trigger

        Returns:
            Dict[str, Any]: A dictionary with trigger configuration
        """
        # RQ doesn't have specific trigger classes like APScheduler.
        # Instead, we'll return a dictionary with parameters that can
        # be used by RQSchedulerBackend to schedule jobs appropriately.

        result = {"type": self.trigger_type, **kwargs}

        # For cron triggers, handle crontab string specifically
        if self.trigger_type == "cron" and "crontab" in kwargs:
            result["crontab"] = kwargs["crontab"]

        return result
