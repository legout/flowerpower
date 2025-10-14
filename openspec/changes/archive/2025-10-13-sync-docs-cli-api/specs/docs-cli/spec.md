## MODIFIED Requirements

### Requirement: CLI main commands reflect actual options
Documentation SHALL list accurate options, types, and defaults for top-level CLI (`flowerpower`) commands.
#### Scenario: flowerpower init
- Options documented with correct types/defaults: `--name` (str|None), `--base-dir` (str|None), `--storage-options` (str->dict|None)
- Examples reflect working invocations

#### Scenario: flowerpower ui
- Options documented with correct types/defaults: `--port` (int=8241), `--base-dir` (str, default `~/.hamilton/db`), `--no-migration` (bool=False), `--no-open` (bool=False), `--settings` (str="mini"), `--config` (str|None)
- Note dependency on `sf-hamilton[ui]` and error message if missing

### Requirement: Pipeline CLI subcommands match actual signatures
Documentation MUST mirror the real parameters and behaviors of all `flowerpower pipeline` subcommands.
#### Scenario: pipeline run
- Document options present in code: `--executor`, `--inputs`, `--final-vars`, `--config`, `--cache`, `--storage-options`, `--log-level`, `--with-adapter`, retry options; remove `--run-config` and adapter split options not in CLI

#### Scenario: pipeline new/delete
- Document `--overwrite` for `new`; `--cfg`/`--module` behavior for `delete` (if none set, both deleted)

#### Scenario: pipeline show-dag/save-dag
- Document `show-dag` `--format` with `raw` behavior
- Document `save-dag` options; add note that manager currently ignores `output_path` (inconsistency)

#### Scenario: pipeline show-pipelines
- Document current CLI option `--format`, but add note that manager implementation doesn’t accept a format arg (inconsistency)

### Requirement: API docs reflect code
Python API documentation MUST match implementation signatures, return types, behavior notes, and available attributes.
#### Scenario: FlowerPowerProject.load
- Behavior: returns `FlowerPowerProject | None` (prints/logs when missing), does not raise `FileNotFoundError`

#### Scenario: FlowerPowerProject.new
- Include `overwrite: bool=False` parameter

#### Scenario: initialize_project
- No `overwrite` parameter; mirrors `FlowerPowerProject.new()` sans overwrite

#### Scenario: create_project (alias FlowerPower)
- Behavior: loads existing project; if missing, raises `FileNotFoundError` with guidance to use `initialize_project()`; does not auto-initialize

#### Scenario: FlowerPowerProject attributes
- Remove internal attributes not present (`_base_dir`, `_fs`, `_storage_options`); document available `name` and `pipeline_manager`

#### Scenario: PipelineManager API
- Document existing methods/properties only: `run`, `load_pipeline`, `list_pipelines`, `show_pipelines()` (no format param), `pipelines` (property), `summary` (property), `add_hook`, IO and visualization methods with correct signatures
