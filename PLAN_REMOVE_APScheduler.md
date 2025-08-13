# Plan: Remove APScheduler from FlowerPower

This document outlines the steps to completely remove APScheduler as a job queue backend from the FlowerPower library, leaving only RQ as the supported backend.

## Phase 1: Code Removal and Modification

This phase focuses on identifying and removing or modifying code directly related to APScheduler.

### 1. `pyproject.toml`

*   Remove `apscheduler` from the `[project.optional-dependencies]` section.
*   Ensure no other direct references to `apscheduler` remain.

### 2. `src/flowerpower/__init__.py`

*   Remove `APSManager` and `APSBackend` from the `__all__` list.
*   Remove any `apscheduler` related `import` statements.

### 3. `src/flowerpower/cfg/__init__.py`

*   Review the `Config` class and its methods (`load`, `save`, `init_config`) to ensure no `apscheduler`-specific logic or imports are present.

### 4. `src/flowerpower/cfg/project/job_queue.py`

*   Delete the `APSDataStoreConfig`, `APSEventBrokerConfig`, and `APSBackendConfig` classes.
*   Modify the `JobQueueConfig` class:
    *   In the `__post_init__` method, remove the `elif self.type == "apscheduler":` block and its contents.
    *   Update the `raise ValueError` message to reflect that only `rq` is a valid type.
*   Remove all `import` statements related to `APSDataStoreConfig`, `APSEventBrokerConfig`, and `APSBackendConfig`.

### 5. `src/flowerpower/cli/__init__.py`

*   Modify the `if importlib.util.find_spec("apscheduler") or importlib.util.find_spec("rq"):` condition to only check for `rq`.
*   Update the `init` command's `job_queue_type` `typer.Option` help text to remove "apscheduler" as a valid option.

### 6. `src/flowerpower/cli/job_queue.py`

*   Remove the `start_scheduler` command entirely, as it's specific to RQ.
*   For `start_worker`, `cancel_job`, `delete_job`, `pause_schedule`, `resume_schedule`, `show_jobs`, `show_schedules`, `show_job_ids`, and `show_schedule_ids` commands:
    *   Remove any `if worker.cfg.backend.type != "apscheduler":` checks and their associated `logger.info` messages.
    *   Remove any `if worker.cfg.backend.type == "apscheduler":` blocks and their contents.
*   Remove all `import` statements related to `apscheduler` (e.g., `APSManager`, `APSBackend`).

### 7. `src/flowerpower/job_queue/__init__.py`

*   Remove the conditional imports for `APSBackend` and `APSManager`.
*   Modify the `JobQueueBackend` class's `__new__` method:
    *   Remove the `elif job_queue_type == "apscheduler":` block.
    *   Update the `raise ValueError` message to indicate only `rq` is a valid type.
*   Modify the `JobQueueManager` class's `__new__` method:
    *   Remove the `elif type == "apscheduler":` block.
    *   Update the `raise ImportError` message to indicate only `rq` is a valid type.
*   Remove `APSManager` and `APSBackend` from the `__all__` list.

### 8. `src/flowerpower/job_queue/apscheduler/` directory

*   **Delete this entire directory and all its contents.**

### 9. `src/flowerpower/job_queue/base.py`

*   In the `BackendType` enum, remove the `POSTGRESQL`, `MYSQL`, `SQLITE`, `MONGODB` members if they are *only* used by APScheduler. If they are generic database types that might be used by other backends (e.g., for I/O plugins), keep them but ensure their `properties` do not contain `apscheduler`-specific attributes.
*   Review the `gen_uri` method for any `apscheduler`-specific URI generation logic and remove it.

### 10. `src/flowerpower/pipeline/job_queue.py`

*   In the `PipelineJobQueue` class's `job_queue` property:
    *   Remove the `elif self._job_queue_type == "apscheduler":` warning message.
*   Review the `run_job`, `add_job`, and `schedule` methods for any `apscheduler`-specific parameters or logic (e.g., `job_executor` specific to APScheduler, or `APScheduler` specific `kwargs` being passed). Ensure they are either removed or generalized.

### 11. `src/flowerpower/settings/job_queue.py`

*   Remove all variables prefixed with `APS_` (e.g., `APS_BACKEND_DS`, `APS_CLEANUP_INTERVAL`, `APS_NUM_WORKERS`).

### 12. `src/flowerpower/settings/backend.py`

*   Review the `BACKEND_PROPERTIES` dictionary. Remove entries for `postgresql`, `mysql`, `sqlite`, and `mongodb` if they were exclusively defined for APScheduler. If they are generic database backends used elsewhere (e.g., by I/O plugins), keep them but ensure no `apscheduler`-specific properties remain.

### 13. `src/flowerpower/utils/monkey.py`

*   Remove the `patch_pickle` function and its call.
*   Remove the entire `if importlib.util.find_spec("apscheduler"):` block and its contents, including `job_to_dict`, `task_to_dict`, `schedule_to_dict`, and their assignments to `Job.to_dict`, etc.

### 14. `src/flowerpower/utils/scheduler.py`

*   **Delete this entire file.** This file contains utility functions specifically for displaying APScheduler jobs and schedules.

## Phase 2: Clean up and Verification

This phase ensures the codebase is clean, functional, and adheres to project standards after the removal.

### 1. Remove Unused Imports

*   After completing all code removals and modifications, go through every modified Python file (`.py`) and remove any `import` statements that are no longer used. This includes imports for `apscheduler` itself, as well as any modules or classes that were only required by `apscheduler`-related code.

### 2. Run Tests

*   Execute the project's test suite (`pytest`) to ensure that the remaining functionality (primarily RQ) still works as expected and no regressions have been introduced.
*   If there are any tests specifically for `apscheduler`, they should be removed or commented out.

### 3. Linting and Formatting

*   Run the project's linting and formatting tools (e.g., `ruff check .` and `ruff format .`) to ensure that the code adheres to the project's style guidelines and that no new linting errors have been introduced.
