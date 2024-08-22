import importlib
import importlib.util

from hamilton.execution import executors
from loguru import logger

if importlib.util.find_spec("distributed"):
    from dask import distributed
else:
    distributed = None


if importlib.util.find_spec("ray"):
    import ray
else:
    ray = None


def get_executor(mode: str, max_tasks: int = 10, num_cpus: int = 4):
    shutdown = None

    if mode == "processpool":
        remote_executor = executors.MultiProcessingExecutor(max_tasks=max_tasks)
    elif mode == "threadpool":
        remote_executor = executors.MultiThreadingExecutor(max_tasks=max_tasks)
    elif mode == "dask":
        if distributed:
            from hamilton.plugins import h_dask

            cluster = distributed.LocalCluster()
            client = distributed.Client(cluster)
            remote_executor = h_dask.DaskExecutor(client=client)
            shutdown = cluster.close
        else:
            logger.info(
                "Dask is not installed. If you want to use Dask for distributed execution, install it using via:"
                "`pip install dask`"
                "'conda install dask'"
                "`pip install flowerpower[dask]`"
            )
            remote_executor = executors.SynchronousLocalTaskExecutor()
    elif mode == "ray":
        if ray:
            from hamilton.plugins import h_ray

            remote_executor = h_ray.RayTaskExecutor(num_cpus=num_cpus)
            shutdown = ray.shutdown
        else:
            logger.info(
                "Ray is not installed. If you want to use Ray for distributed execution, install it using via:"
                "`pip install ray`"
                "'conda install ray'"
                "`pip install flowerpower[ray]`"
            )
            remote_executor = executors.SynchronousLocalTaskExecutor()
    else:
        remote_executor = executors.SynchronousLocalTaskExecutor()
    return remote_executor, shutdown
