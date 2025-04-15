# Active Context

## Current Focus

*   [2025-04-10 21:14:00] - Implementing a unified interface for RQ, Huey, and APScheduler.

## Recent Changes

*   [2025-04-10 21:14:00] - Designed the unified interface, created the core files and configuration classes.
*   [2025-04-14 22:49:46] - Refactored and optimized `src/flowerpower/worker/__init__.py` and `src/flowerpower/worker/base.py` for clarity, robustness, and security.
*   [2025-04-14 16:38:42] - Implemented Huey trigger classes (`HueyCronTrigger`, `HueyIntervalTrigger`, `HueyDateTrigger`) in `src/flowerpower/worker/huey/trigger.py` and updated `__init__.py`.

## Open Questions/Issues

*   [2025-04-10 21:14:00] - The APScheduler library is not installed, and there are errors in the RQ and Huey adapters.