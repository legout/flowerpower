from .apscheduler import APSWorker
from .rq import RQWorker
from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class WorkerFactory:
    """
    Factory class to create instances of different worker types.
    """
    backend: str
    

    @staticmethod
    def create_worker(worker_type: str, **kwargs) -> APSWorker | RQWorker:
        """
        Create a worker instance based on the specified type.

        Args:
            worker_type: Type of the worker ('apscheduler' or 'rq').
            **kwargs: Additional parameters for the worker.

        Returns:
            An instance of the specified worker type.
        """
        if worker_type == "apscheduler":
            return APSWorker(**kwargs)
        elif worker_type == "rq":
            return RQWorker(**kwargs)
        else:
            raise ValueError(f"Unknown worker type: {worker_type}")