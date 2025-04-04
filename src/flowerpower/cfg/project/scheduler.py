# src/flowerpower/cfg/project/scheduler.py
from typing import Any, Dict, Literal, Optional

from pydantic import BaseModel, Field, root_validator, ValidationError

from ..base import BaseConfig


class APSchedulerSettings(BaseConfig):
    """Settings specific to the APScheduler backend."""
    data_store: Dict[str, Any] = Field(default_factory=dict, description="APScheduler data store configuration.")
    event_broker: Dict[str, Any] = Field(default_factory=dict, description="APScheduler event broker configuration.")
    # Add other APScheduler-specific fields if needed


class RQSettings(BaseConfig):
    """Settings specific to the RQ backend."""
    redis_url: str = "redis://localhost:6379/0"
    # Add other RQ-specific fields if needed


class DramatiqSettings(BaseConfig):
    """Settings specific to the Dramatiq backend."""
    broker_url: str = "redis://localhost:6379/0" # Placeholder, adjust as needed
    # Add other Dramatiq-specific fields if needed


class SpinachSettings(BaseConfig):
    """Settings specific to the Spinach backend."""
    broker_url: str = "redis://localhost:6379/0" # Placeholder, adjust as needed
    # Add other Spinach-specific fields if needed


class SchedulerConfig(BaseConfig):
    """Configuration for the task scheduler."""
    backend: Literal["apscheduler", "rq", "dramatiq", "spinach"] = "apscheduler"
    default_queue: str = "default"

    apscheduler: Optional[APSchedulerSettings] = Field(default_factory=APSchedulerSettings)
    rq: Optional[RQSettings] = None
    dramatiq: Optional[DramatiqSettings] = None
    spinach: Optional[SpinachSettings] = None

    @root_validator(pre=True)
    def check_backend_config_provided(cls, values):
        """Ensure that the config section for the selected backend is present."""
        backend = values.get("backend")
        backend_config = values.get(backend)

        # If the backend is explicitly set and its config is None or missing,
        # initialize it with default values. This simplifies usage as users
        # don't always need to provide an empty dict for the selected backend.
        if backend and backend_config is None:
            if backend == "apscheduler":
                values["apscheduler"] = APSchedulerSettings()
            elif backend == "rq":
                values["rq"] = RQSettings()
            elif backend == "dramatiq":
                values["dramatiq"] = DramatiqSettings()
            elif backend == "spinach":
                values["spinach"] = SpinachSettings()
            # No need for explicit validation failure here, as we provide defaults.
            # If a backend was selected for which no default factory exists,
            # Pydantic's regular validation would catch it later if accessed.

        return values