from .registry import JobQueueBackendRegistry

# Import RQ backend for auto-registration
from .rq import RQManager  # noqa: F401
