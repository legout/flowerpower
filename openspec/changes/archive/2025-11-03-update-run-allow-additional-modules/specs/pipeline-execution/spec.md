## ADDED Requirements

### Requirement: Run With Additional Modules
The system SHALL support executing a pipeline while loading additional Python modules into the Hamilton driver so that DAG nodes can be composed across modules.

#### Scenario: Execute with string module names
- WHEN a user runs `pm.run("pipeline_1", additional_modules=["setup"])`
- THEN the system imports both `setup` and `pipeline_1` modules and executes the composed DAG
- AND functions in all loaded modules are available for dependency resolution

#### Scenario: Execute with module objects
- WHEN a user passes actual module objects in `additional_modules`
- THEN the system uses these module objects directly without re-importing
- AND execution succeeds identically to using string names

#### Scenario: Missing module raises helpful error
- WHEN any `additional_modules` entry cannot be imported
- THEN the system raises an ImportError that indicates the attempted name and suggests `pipelines.<name>` and `'-'→'_'` formatting

#### Scenario: Precedence order determines node override
- WHEN multiple modules define the same node name
- THEN the last module in the `.with_modules(*modules)` order SHALL take precedence (Hamilton standard behavior)

#### Scenario: Reload reloads all loaded modules
- GIVEN `reload=True` is set
- WHEN execution starts
- THEN the system reloads the main pipeline module and each additional module

#### Scenario: Works for async execution
- WHEN running with `run_async(...)` and `additional_modules` provided
- THEN the system composes the same set of modules and executes asynchronously

#### Scenario: Cross-module final_vars
- WHEN `final_vars` references nodes defined in any loaded module
- THEN the system resolves and returns those nodes successfully

