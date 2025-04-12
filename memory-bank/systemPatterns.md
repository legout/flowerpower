# System Patterns

*   **Configuration Management:** YAML-based configuration for projects and pipelines (`src/flowerpower/cfg/`).
*   **Backend Abstraction:** Base classes and adapter implementations for RQ, Huey, and APScheduler (`src/flowerpower/worker/`).
*   **Configuration via msgspec:** Using `msgspec.Struct` for type-safe configuration with YAML and dictionary loading (`src/flowerpower/worker/config.py`).
*   **Plugin System (Potential):** IO Loaders/Savers suggest a pattern for extensible input/output (`src/flowerpower/io/`).

## Initial Setup Notes

*   [2025-04-10 14:13:37] - Initial patterns identified based on existing file structure. Needs review and expansion.