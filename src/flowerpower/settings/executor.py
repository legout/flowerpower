import os

# EXECUTOR
EXECUTOR = os.getenv("FP_EXECUTOR", "threadpool")
EXECUTOR_MAX_WORKERS = int(
    os.getenv("FP_EXECUTOR_MAX_WORKERS", os.cpu_count() * 5 or 10)
)
EXECUTOR_NUM_CPUS = int(os.getenv("FP_EXECUTOR_NUM_CPUS", os.cpu_count() or 1))
