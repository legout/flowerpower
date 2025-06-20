from typing import Type, Dict, List
from .base import BaseJobQueueManager

class JobQueueBackendRegistry:
    _backends: Dict[str, Type[BaseJobQueueManager]] = {}

    @classmethod
    def register(cls, name: str, backend_class: Type[BaseJobQueueManager]):
        if name in cls._backends:
            raise ValueError(f"Backend '{name}' is already registered.")
        cls._backends[name] = backend_class

    @classmethod
    def create(cls, backend_type: str, **config) -> BaseJobQueueManager:
        if backend_type not in cls._backends:
            raise ValueError(f"Backend '{backend_type}' is not registered. Available: {list(cls._backends.keys())}")
        return cls._backends[backend_type](**config)

    @classmethod
    def list_available(cls) -> List[str]:
        return list(cls._backends.keys())