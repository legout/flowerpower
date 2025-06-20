from .manager import RQManager
from ..registry import JobQueueBackendRegistry

JobQueueBackendRegistry.register("rq", RQManager)
