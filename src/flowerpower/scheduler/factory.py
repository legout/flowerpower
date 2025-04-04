import typing as t
import logging

from flowerpower.cfg import Config  # Assuming Config is importable from here
from .adapters.base import BaseSchedulerAdapter

logger = logging.getLogger(__name__)


def create_scheduler_adapter(config: Config) -> BaseSchedulerAdapter:
    """
    Factory function to create a scheduler adapter based on configuration.

    :param config: The application configuration object.
    :return: An instance of a BaseSchedulerAdapter subclass.
    :raises ValueError: If the configured backend is unsupported or configuration is missing.
    """
    backend = config.project.scheduler.backend
    logger.info(f"Creating scheduler adapter for backend: {backend}")

    if backend == "apscheduler":
        try:
            from .adapters.apscheduler import APSchedulerAdapter
        except ImportError:
            logger.error("APScheduler backend selected, but APSchedulerAdapter could not be imported.")
            raise ValueError("APScheduler backend requires 'apscheduler' library to be installed.")

        # Extract the specific config section for APScheduler
        # We assume the structure defined in the config models (e.g., cfg.project.SchedulerConfig)
        apscheduler_config = config.project.scheduler.apscheduler.model_dump(exclude_none=True) if config.project.scheduler.apscheduler else {}

        if not apscheduler_config:
             logger.warning("APScheduler backend selected, but no specific configuration found under 'project.scheduler.apscheduler'. Using defaults.")
             # Provide minimal default if needed, or rely on create_scheduler's defaults
             apscheduler_config = {} # Or potentially load defaults

        logger.debug(f"APScheduler configuration: {apscheduler_config}")
        return APSchedulerAdapter(config=apscheduler_config)

    elif backend == "rq":
        logger.error("RQ scheduler backend is not yet implemented.")
        raise NotImplementedError("RQ scheduler backend is not yet implemented.")
        # Placeholder for RQ implementation
        # from .adapters.rq import RQSchedulerAdapter # To be created
        # rq_config = config.project.scheduler.rq...
        # return RQSchedulerAdapter(config=rq_config)

    elif backend == "dramatiq":
        logger.error("Dramatiq scheduler backend is not yet implemented.")
        raise NotImplementedError("Dramatiq scheduler backend is not yet implemented.")
        # Placeholder for Dramatiq implementation
        # from .adapters.dramatiq import DramatiqSchedulerAdapter # To be created
        # dramatiq_config = config.project.scheduler.dramatiq...
        # return DramatiqSchedulerAdapter(config=dramatiq_config)

    elif backend == "spinach":
        logger.error("Spinach scheduler backend is not yet implemented.")
        raise NotImplementedError("Spinach scheduler backend is not yet implemented.")
        # Placeholder for Spinach implementation
        # from .adapters.spinach import SpinachSchedulerAdapter # To be created
        # spinach_config = config.project.scheduler.spinach...
        # return SpinachSchedulerAdapter(config=spinach_config)

    else:
        logger.error(f"Unsupported scheduler backend configured: {backend}")
        raise ValueError(f"Unsupported scheduler backend: {backend}")