## ADDED Requirements

### Requirement: Asynchronous Execution via Hamilton Async Driver
The system SHALL execute pipelines asynchronously using Hamilton’s async driver under `hamilton.async_driver`.

#### Scenario: Async execution succeeds with async driver
- WHEN a user calls `PipelineManager.run_async("pipeline")`
- THEN the system constructs the DAG with any provided `additional_modules`
- AND uses `hamilton.async_driver` to execute the pipeline asynchronously
- AND returns a result mapping for the requested `final_vars`

#### Scenario: Configure async via RunConfig
- WHEN a user sets `RunConfig.async_driver=True` (or omits it) and calls `run_async`
- THEN the system uses the async driver
- WHEN a user sets `RunConfig.async_driver=False`
- THEN the system DOES NOT use the async driver and raises a clear error or falls back per design (to be specified in design/implementation notes)

#### Scenario: Reload + logging parity
- GIVEN `reload=True` and `log_level="DEBUG"`
- WHEN a user calls `run_async`
- THEN the system reloads the main and additional modules before execution
- AND configures logging level for the run

#### Scenario: Helpful error on missing dependency
- WHEN `hamilton.async_driver` cannot be imported
- THEN the system raises an ImportError explaining that async execution requires a Hamilton version that provides the async driver and how to upgrade

#### Scenario: Adapters propagate to async
- WHEN a user enables adapters via `with_adapter` and/or adapter configs
- THEN the system instantiates and passes the same adapters to the async driver as in synchronous execution

