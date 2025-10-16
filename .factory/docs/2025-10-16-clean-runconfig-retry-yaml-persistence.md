**Change ID**: update-run-config-retry-yaml

## Proposal
### Why
Legacy retry fields linger in saved run configuration YAML, creating duplicate state and confusing operators maintaining configs.

### What Changes
- Strip deprecated top-level retry fields when emitting run configuration YAML so only the nested `retry` block is persisted.
- Auto-migrate legacy configs during load by hydrating the nested retry struct from flat fields and resaving the YAML in the new format.
- Extend regression coverage to lock in the serialization and migration flow.

### Impact
- Code: `src/flowerpower/cfg/pipeline/run.py`, `src/flowerpower/cfg/pipeline/__init__.py`, `src/flowerpower/cfg/__init__.py`, `src/flowerpower/utils/config.py`, related tests under `tests/cfg` and `tests/pipeline`.
- Specs: new capability `pipeline-run-config` capturing retry persistence behaviour.

## Spec Delta: pipeline-run-config
### Capability Summary
Run configuration persistence ensures retry settings are stored once and legacy configs upgrade automatically.

## ADDED Requirements
### Requirement: Retry persistence cleanup
The system SHALL persist retry settings for pipeline execution using only the nested `retry` structure and upgrade legacy YAML on load.

#### Scenario: Save run config without deprecated fields
- **WHEN** any pipeline configuration containing retry settings is saved through FlowerPower helpers
- **THEN** the resulting YAML SHALL include the nested `retry` block with its values
- **AND** the deprecated fields `max_retries`, `retry_delay`, `jitter_factor`, and `retry_exceptions` SHALL be omitted from the YAML output

#### Scenario: Migrate legacy run config on load
- **GIVEN** a pipeline configuration YAML containing any of the deprecated retry fields without a nested `retry` block
- **WHEN** the configuration is loaded via the standard config loaders
- **THEN** the system SHALL populate the nested `retry` structure using those values
- **AND** the loader SHALL rewrite the YAML file so only the nested `retry` block remains
- **AND** the deprecated retry fields SHALL be removed from the persisted YAML

## Tasks
1. Implement serialization helpers that drop deprecated retry fields before persisting run configs and ensure nested `retry` values remain intact.
2. Detect legacy retry fields during pipeline config load, hydrate nested retry config, and rewrite the YAML without deprecated keys.
3. Propagate the migration through higher-level config load/save flows so CLI and builder paths rewrite legacy files automatically.
4. Update existing config serialization tests and add migration coverage for loading legacy YAML and verifying on-disk rewrite.
5. Validate with `uv run pytest tests/cfg/test_run_config.py tests/pipeline/test_pipeline.py` (extend to broader suites if side effects appear).
