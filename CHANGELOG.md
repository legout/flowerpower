# Changelog

## [0.11.6.20] - 2025-08-12

### Changes
- fixed a bug in the job queue manager and updated the CLI job queue script
- Fix formatting of base path calculation in BaseFileIO class



## [0.11.6.19] - 2025-07-16

### Changes
- Bump version to 0.11.6.19 in pyproject.toml and update version to 0.11.6.18 in uv.lock; enhance base path handling in BaseFileIO class



## [0.11.6.18] - 2025-07-16

### Changes
- Bump version to 0.11.6.18 and update condition for table length check in _read_parquet function
- Refactor string cleaning and optimize imports in PyArrow; improve readability of _clean_string_array function



## [0.11.6.17] - 2025-07-16

### Changes
- Update regex patterns and enhance string cleaning in PyArrow and Polars; optimize numeric and string array processing with null handling
- Refactor _get_column_expr and opt_dtype for improved readability by formatting function arguments



## [0.11.6.16] - 2025-07-16

### Changes
- Bump version to 0.11.6.16 and update _get_column_expr to include allow_unsigned parameter for numeric optimization
- Refactor _optimize_numeric_column to improve readability of unsigned integer check



## [0.11.6.15] - 2025-07-16

### Changes
- Enhance _optimize_numeric_column to support unsigned integer types and improve type optimization logic
- Refactor _get_optimal_int_type and _optimize_numeric_array function signatures for improved readability



## [0.11.6.14] - 2025-07-16

### Changes
- Refactor _get_optimal_int_type and _optimize_numeric_array function signatures for improved readability



## [0.11.6.14] - 2025-07-16

### Changes
- Update _get_optimal_int_type and _optimize_numeric_array functions to support unsigned integer types
- Refactor function signatures for improved readability in pyarrow.py



## [0.11.6.13] - 2025-07-15

### Changes
- Bump version to 0.11.6.13 in pyproject.toml and update timestamp handling in unify_schemas function
- Fix whitespace in _read_parquet function to improve readability



## [0.11.6.12] - 2025-07-12

### Changes
- Bump version to 0.11.6.12 in pyproject.toml and enhance _read_parquet function to handle empty tables



## [0.11.6.11] - 2025-07-12

### Changes
- Bump version to 0.11.6.11 in pyproject.toml and fix null type casting in polars.py and pyarrow.py
- Fix indentation in _read_parquet function for schema unification logic



## [0.11.6.10] - 2025-07-12

### Changes
- Bump version to 0.11.6.10 in pyproject.toml and refactor schema unification logic in _read_parquet function
- Refactor commented code for clarity in _read_parquet function



## [0.11.6.9] - 2025-07-12

### Changes
- Bump version to 0.11.6.9 in pyproject.toml and set opt_dtypes to False in BaseFileReader
- Refactor import statement formatting and improve readability in run_parallel function



## [0.11.6.8] - 2025-07-12

### Changes
- Bump version to 0.11.6.8 in pyproject.toml and enhance parallel processing with progress indicators in run_parallel function
- Refactor comments for clarity in parquet reading functions



## [0.11.6.7] - 2025-07-12

### Changes
- Refactor comments for clarity in parquet reading functions



## [0.11.6.7] - 2025-07-12

### Changes
- Bump version to 0.11.6.7 in pyproject.toml and update version to 0.11.6.6 in uv.lock



## [0.11.6.6] - 2025-07-11

### Changes
- Bump version to 0.11.6.6 and update casting logic in polars and pyarrow helpers
- Refactor code for improved readability and consistency in various modules



## [0.11.6.5] - 2025-07-11

### Changes
- Refactor code for improved readability and consistency in various modules



## [0.11.6.5] - 2025-07-11

### Changes
- Refactor tests for CLI and pipeline modules
- Bump version to 0.11.6.5 in pyproject.toml and update parquet reading logic to exclude empty tables
- Refactor import formatting and improve readability in base.py



## [0.11.6.4] - 2025-07-11

### Changes
- Refactor import formatting and improve readability in base.py



## [0.11.6.4] - 2025-07-11

### Changes
- Refactor import formatting and improve readability in base.py



## [0.11.6.4] - 2025-07-11

### Changes
- Bump version to 0.11.6.4 in pyproject.toml and clean up import formatting in base.py



## [0.11.6.3] - 2025-07-11

### Changes
- Bump version to 0.11.6.3 in pyproject.toml
- Add strict mode to opt_dtype for enhanced error handling
- Add a blank line for improved readability in pyproject.toml



## [0.11.6.2] - 2025-07-11

### Changes
- Bump version to 0.11.6.2 in pyproject.toml
- Add verbose option to BaseFileReader for improved logging control
- Refactor import statements for improved organization and readability



## [0.11.6.1] - 2025-07-11

### Changes
- Refactor import statements for improved organization and readability



## [0.11.6.1] - 2025-07-11

### Changes
- Remove unused Alembic files and update version to 0.11.6.1
- Refactor code for improved readability and consistency in JSON reading functions
- Add opt_dtypes parameter to optimize DataFrame dtypes in JSON and CSV reading functions



## [0.11.6] - 2025-06-17

### Changes
- fix: clean up imports and whitespace across multiple files
- feat: Implement Adapter and Pipeline Configuration



## [0.11.6] - 2025-06-17

### Changes
- fix: clean up imports and whitespace across multiple files
- feat: Implement Adapter and Pipeline Configuration



## [0.11.6] - 2025-06-17

### Changes
- Bump version to 0.11.6 and clean up regex comments in PyArrow and Polars helpers
- Refactor and optimize PyArrow helper functions for data type conversion
- Refactor pyarrow helper functions for improved readability and consistency
- Enhance PyArrow Helper Functions and Optimize DataFrame Creation
- Refactor code structure for improved readability and maintainability



## [0.11.5.8] - 2025-06-12

### Changes
- bump: update version to 0.11.5.8 in pyproject.toml and clean up whitespace in metadata.py
- bump: update version to 0.11.5.7 in uv.lock and fix lazy loading in BaseFileReader and metadata handling in get_dataframe_metadata



## [0.11.5.7] - 2025-06-11

### Changes
- bump: update version to 0.11.5.7 in pyproject.toml and comment out unused parameters in DeltaTableWriter
- bump: update version to 0.11.5.6 in uv.lock and comment out unused parameters in DeltaTableWriter



## [0.11.5.6] - 2025-06-11

### Changes
- bump: update version to 0.11.5.6 in pyproject.toml refactor: format get_dataframe_metadata call for better readability in DeltaTableWriter
- refactor: replace _raw_path with _base_path in DeltaTableReader and DeltaTableWriter



## [0.11.5.5] - 2025-06-11

### Changes
- bump: update version to 0.11.5.5 in pyproject.toml
- fix: correct typo in with_strftime_columns method references



## [0.11.5.4] - 2025-06-11

### Changes
- bump: update version to 0.11.5.4 in pyproject.toml
- fix: correct base path extraction in get_filesystem function



## [0.11.5.3] - 2025-06-11

### Changes
- bump: update version to 0.11.5.3 in pyproject.toml
- fix: improve comment formatting in BaseFileIO
- refactor: simplify filesystem initialization in BaseFileIO



## [0.11.5.2] - 2025-06-11

### Changes
- bump: update version to 0.11.5.2 in pyproject.toml
- fix: improve formatting and readability in get_filesystem and BaseFileIO
- fix: update filesystem handling in get_filesystem and improve base path retrieval in BaseFileIO bump: version to 0.11.5.1 in uv.lock



## [0.11.5.1] - 2025-06-11

### Changes
- bump: update version to 0.11.5.1 in pyproject.toml
- fix: improve formatting of DirFileSystem initialization for better readability
- fix: update filesystem handling and version to 0.11.5, adjust dependencies



## [0.11.5] - 2025-06-10

### Changes
- bump: update version to 0.11.5 in pyproject.toml
- fix: improve readability by restructuring conditional expressions and organizing imports
- fix: enhance protocol handling and storage options in filesystem integration



## [0.11.4] - 2025-06-06

### Changes
- bump: update version to 0.11.4 in pyproject.toml
- fix: clean up whitespace in iter_pyarrow_table method in BaseFileReader
- fix: remove batch_size parameter from iterators in BaseFileReader and set default value



## [0.11.3] - 2025-06-06

### Changes
- bump: update version to 0.11.3 in pyproject.toml
- fix: handle TypeError in _opt_dtype function when casting to Float32
- fix: handle TypeError when casting to Float32 in _opt_dtype function
- refactor: remove unused msgspec import from multiple saver modules



## [0.11.2] - 2025-06-06

### Changes
- bump: update version to 0.11.2 in pyproject.toml
- refactor: comment out unused import from collections.abc in misc.py
- refactor: remove unused msgspec imports across various modules
- refactor: clean up imports in datetime and sql modules
- refactor: move timestamp_from_string function to datetime module and clean up sql.py



## [0.11.1] - 2025-06-06

### Changes
- bump: update version to 0.11.1
- refactor: standardize comments for attrs definition across loader and saver modules
- Refactor data loader and saver classes to use msgspec for field definitions



## [0.11.0] - 2025-06-05

### Changes
- bump: update version to 0.11.0
- feat: refactor codebase to use attrs for data classes and improve structure
- refactor: Update import statements for consistency and clarity



## [0.10.9.1] - 2025-06-05

### Changes
- feat: refactor codebase to use attrs for data classes and improve structure
- refactor: Update import statements for consistency and clarity



## [0.10.9.1] - 2025-06-05

### Changes
- feat: refactor codebase to use attrs for data classes and improve structure
- refactor: Update import statements for consistency and clarity



## [0.10.9.1] - 2025-06-04

### Changes
- bump: Update version to 0.10.9.1 in pyproject.toml
- refactor: Improve code formatting and readability in APScheduler manager and setup modules
- refactor: Enhance job queue backend setup and logging configuration
- refactor: Rename job queue backend variable for clarity



## [0.10.9] - 2025-06-03

### Changes
- bump: Update version to 0.10.9 in pyproject.toml
- refactor: Improve code formatting and readability in job queue and settings modules
- - Refactor code structure for improved readability and maintainability - Changed job queue default config handling



## [0.10.8.1] - 2025-06-03

### Changes
- bump: Update version to 0.10.8.1 in pyproject.toml
- refactor: Improve code formatting and readability across multiple files
- Refactor code structure for improved readability and maintainability
- chore: Bump version to 0.10.8 in pyproject.toml
- refactor: Organize imports and improve code formatting across multiple modules
- Refactor code structure for improved readability and maintainability
- refactor: Clean up imports and improve code formatting across multiple modules
- feat: Add callback support for successful and failed pipeline runs in MqttManager
- feat: Enhance job management with callback support and improved error handling
- chore: Update version to 0.10.7.4; fix incorrect attribute reference for filesystem mapper in job queue and pipeline manager
- chore: Update version to 0.10.7.3; fix incorrect attribute reference for filesystem mapper in job queue and pipeline manager
- chore: Update version to 0.10.7.2; refactor filesystem sync handling in pipeline classes
- chore: Update version to 0.10.7.1; replace posixpath.makedirs with os.makedirs for cache directory creation
- chore: Update version to 0.10.7 and add CACHE_DIR setting; refactor filesystem handling in job queue and pipeline manager
- Refactor code structure for improved readability and maintainability
- chore: Update version to 0.10.6.4 and adjust dependencies in pyproject.toml
- refactor: Clean up import statements and ensure consistent formatting in basic_mqtt.py
- Add basic MQTT pipeline configuration and implementation
- feat: Add comprehensive development plans and documentation for FlowerPower web application
- feat: Remove deprecated web templates and add new Test Engineer mode in configuration
- feat: Add comprehensive analysis and documentation for Flowerpower framework
- Add PyTest unit and integration tests
- feat: add comprehensive documentation for FlowerPower framework including installation, project setup, and pipeline management
- fix: update config_hook type annotation from int to str for consistency
- refactor: simplify dictionary comprehension for event broker and DataFrame creation



## [0.10.8] - 2025-05-30

### Changes
- chore: Bump version to 0.10.8 in pyproject.toml
- refactor: Organize imports and improve code formatting across multiple modules
- Refactor code structure for improved readability and maintainability
- refactor: Clean up imports and improve code formatting across multiple modules
- feat: Add callback support for successful and failed pipeline runs in MqttManager
- feat: Enhance job management with callback support and improved error handling
- chore: Update version to 0.10.7.4; fix incorrect attribute reference for filesystem mapper in job queue and pipeline manager
- chore: Update version to 0.10.7.3; fix incorrect attribute reference for filesystem mapper in job queue and pipeline manager
- chore: Update version to 0.10.7.2; refactor filesystem sync handling in pipeline classes
- chore: Update version to 0.10.7.1; replace posixpath.makedirs with os.makedirs for cache directory creation
- chore: Update version to 0.10.7 and add CACHE_DIR setting; refactor filesystem handling in job queue and pipeline manager
- Refactor code structure for improved readability and maintainability
- chore: Update version to 0.10.6.4 and adjust dependencies in pyproject.toml
- refactor: Clean up import statements and ensure consistent formatting in basic_mqtt.py
- Add basic MQTT pipeline configuration and implementation
- feat: Add comprehensive development plans and documentation for FlowerPower web application
- feat: Remove deprecated web templates and add new Test Engineer mode in configuration
- feat: Add comprehensive analysis and documentation for Flowerpower framework
- Add PyTest unit and integration tests
- feat: add comprehensive documentation for FlowerPower framework including installation, project setup, and pipeline management
- fix: update config_hook type annotation from int to str for consistency
- refactor: simplify dictionary comprehension for event broker and DataFrame creation
- bump: update version to 0.10.6.3 and refactor AwsStorageOptions initialization
- Refactor code structure for improved readability and maintainability
- refactor: reorder imports and comment out APScheduler availability check for clarity
- refactor: comment out APScheduler availability check for cleaner code
- fix: update README to clarify job queue backend configuration and environment variable usage
- feat: enhance job queue backend configuration with environment variable support
- fix: update version to 0.10.6.1 in pyproject.toml
- refactor: clean up whitespace and improve readability in job queue configuration
- feat: enhance environment variable handling in job queue configuration
- refactor: remove unused import and clean up whitespace in ProjectConfig
- - update version to 0.10.6 - refactor settings imports for consistency - new feat: job queue backend configuration via env variables
- feat: reorganize settings structure and add backend properties management
- style: improve logging message formatting and enhance readability in MqttManager



## [0.10.6.3] - 2025-05-19

### Changes
- bump: update version to 0.10.6.3 and refactor AwsStorageOptions initialization



## [0.10.6.2] - 2025-05-19

### Changes
- Refactor code structure for improved readability and maintainability
- refactor: reorder imports and comment out APScheduler availability check for clarity
- refactor: comment out APScheduler availability check for cleaner code
- fix: update README to clarify job queue backend configuration and environment variable usage
- feat: enhance job queue backend configuration with environment variable support



## [0.10.6.1] - 2025-05-19

### Changes
- fix: update version to 0.10.6.1 in pyproject.toml
- refactor: clean up whitespace and improve readability in job queue configuration
- feat: enhance environment variable handling in job queue configuration
- refactor: remove unused import and clean up whitespace in ProjectConfig



## [0.10.6] - 2025-05-19

### Changes
- - update version to 0.10.6 - refactor settings imports for consistency - new feat: job queue backend configuration via env variables
- feat: reorganize settings structure and add backend properties management
- style: improve logging message formatting and enhance readability in MqttManager
- chore: update version to 0.10.5 and enhance MQTT message logging with error handling Remove result_ttl, run_in and **kwargs from `pm.run` in `MqttManager.run_pipeline_on_message`
- style: improve code formatting for consistency and readability across multiple files
- Refactor code structure for improved readability and maintainability
- feat: update job queue backend installation instructions and enhance error handling; refactor .gitignore and add test fixtures



## [0.10.5] - 2025-05-18

### Changes
- style: improve logging message formatting and enhance readability in MqttManager



## [0.10.5] - 2025-05-18

### Changes
- chore: update version to 0.10.5 and enhance MQTT message logging with error handling Remove result_ttl, run_in and **kwargs from `pm.run` in `MqttManager.run_pipeline_on_message`
- style: improve code formatting for consistency and readability across multiple files



## [0.10.4.3] - 2025-05-18

### Changes
- Refactor code structure for improved readability and maintainability
- feat: update job queue backend installation instructions and enhance error handling; refactor .gitignore and add test fixtures
- fix: update version to 0.10.4.1 and correct argument name in pipeline manager
- fix: reorder import statements for consistency and clarity
- refactor: update executor configuration and enhance error handling in pipeline runner
- docs: enhance README with detailed execution options for pipelines
- fix: add repomix-output.md to .gitignore
- fix: update copyright holder in LICENSE file
- Refactor code structure for improved readability and maintainability; removed redundant code and optimized functions.
- Updated README.md
- docs: update README with enhanced features and installation instructions;
- fix: update API Documentation link in getting_started.md
- fix: remove outdated build status badge from README
- Added docs (AI generated. Better than expected, but needs review!)
- chore: update version to 0.10.3
- fix: clean up whitespace and improve code formatting across multiple files
- bugfixes: io methods to import and export pipelines fixed.
- Update README to include a subtitle and enhance visual presentation
- Refactor code structure for improved readability and maintainability; removed redundant code blocks and optimized function implementations.
- Add database and file writers/readers for various formats
- push test
- Refactor configuration and update Redis job queue settings
- Bump to version v0.10.2
- Refactor: Update pre-commit hook stages and clean up mqtt import statements
- refactor
- Refactor: Remove unnecessary blank lines and add deprecation warning for mqtt module
- Update version to 0.10.0, add retry configuration, and enhance job queue handling
- Update README.md
- fixing imports
- fixing imports
- Refactor job queue imports and conditionally import backends based on availability
- Bump version to v1.0.0b4
- Refactor imports and formatting across multiple modules
- Refactor imports and improve code formatting across multiple modules
- Add project configuration and update job queue management
- Bump version to v1.0.0b2
- Bump version to v1.0.0b1
- Added new README.md
- Refactor code structure for improved readability and maintainability - added a new `plugin` folder - mqtt is not a plugin (moved  `mqtt` into  `plugin`) - Added pipeline retry functionality
- feat: Add 'repomix-output.md' to .gitignore to exclude generated output files
- fix: Correct parameter name from 'worker_type' to 'job_queue_type' in PipelineRegistry
- feat: Update YAML configurations and improve CLI help documentation
- Refactor code structure and remove redundant code blocks for improved readability and maintainability
- feat: Enhance worker and scheduler cli with additional functionality and improved documentation
- feat: Enhance configuration management and CLI for FlowerPower
- updated deps
- Refactor code for improved readability and consistency
- Refactor code structure for improved readability and maintainability
- Enhance storage options management with detailed documentation and new features
- Refactor code structure for improved readability and maintainability
- feat: Add GeventWorker and ThreadWorker for concurrent job processing
- Add cron-descriptor and croniter packages; update dependencies
- Refactor PipelineManager and related components for improved logging and configuration handling
- Refactor PipelineScheduler and PipelineVisualizer for improved configuration handling
- Enhance PipelineRunner with context management and logging improvements
- refactor: Update worker configuration to use ProjectConfig and enhance logging setup
- Refactor logging setup and configuration
- refactor: Enhance pipeline and configuration structure, add new executor and adapter functionalities
- Refactor code structure for improved readability and maintainability
- refactor: Update project configuration to use PostgreSQL and enhance worker settings
- Refactor pipeline configuration and worker classes
- refactor: Enable port exposure for various services in docker-compose.yml
- Refactored docker-compose.yml and added a python-dev-worker container
- refactor: Correct JupyterCode references in nginx configuration and enhance docker-compose documentation
- refactor: Update configuration files and backend setup for improved clarity and consistency
- refactor: Simplify PipelineManager and PipelineRegistry methods for improved clarity and organization
- Refactor pipeline configuration and I/O management
- refactor: Clean up imports and update type hints across pipeline modules
- Refactor code for improved readability and consistency
- fix: Update storage_options type hint to support None in PipelineManager methods
- refactor: Update import paths for Pipeline and SchedulerManager to improve module organization
- feat: Add PipelineRunner, Scheduler, and Visualizer for enhanced pipeline management
- Refactor RQBackend job result methods
- feat: Add parameter resolution method and lazy worker instantiation in PipelineManager
- Implement code changes to enhance functionality and improve performance
- Refactor code structure for improved readability and maintainability
- feat: Remove unused example pipeline and script files; refactor worker configuration handling
- feat: Introduce APScheduler backend configuration and refactor worker classes
- Refactor: Remove TUI implementation and update worker backend type handling
- feat: Add worker example scripts and enhance backend configuration options
- feat: Refactor and optimize worker and backend code for clarity, robustness, and security
- feat: Implement Huey backend with trigger classes and worker integration
- Refactor worker and backend classes for improved structure and functionality
- feat: Enhance worker management with start/stop pool methods and refactor client usage
- chore: Update .gitignore to exclude all database files
- Implement RQ backend for FlowerPower scheduler
- feat: Implement base scheduler interface and RQ backend for FlowerPower
- Refactor APScheduler setup: move datastore and event broker implementations to separate modules
- Refactor configuration management and remove unused modules



## [0.10.4.1] - 2025-05-14

### Changes
- fix: update version to 0.10.4.1 and correct argument name in pipeline manager
- fix: reorder import statements for consistency and clarity



## [0.10.4] - 2025-05-14

### Changes
- refactor: update executor configuration and enhance error handling in pipeline runner
- docs: enhance README with detailed execution options for pipelines
- fix: add repomix-output.md to .gitignore
- fix: update copyright holder in LICENSE file
- Refactor code structure for improved readability and maintainability; removed redundant code and optimized functions.
- Updated README.md
- docs: update README with enhanced features and installation instructions;
- fix: update API Documentation link in getting_started.md
- fix: remove outdated build status badge from README
- Added docs (AI generated. Better than expected, but needs review!)
- chore: update version to 0.10.3
- fix: clean up whitespace and improve code formatting across multiple files
- bugfixes: io methods to import and export pipelines fixed.
- Update README to include a subtitle and enhance visual presentation
- Refactor code structure for improved readability and maintainability; removed redundant code blocks and optimized function implementations.
- Add database and file writers/readers for various formats
- push test
- Refactor configuration and update Redis job queue settings
- Bump to version v0.10.2
- Refactor: Update pre-commit hook stages and clean up mqtt import statements
- refactor
- Refactor: Remove unnecessary blank lines and add deprecation warning for mqtt module
- Update version to 0.10.0, add retry configuration, and enhance job queue handling
- Update README.md
- fixing imports
- fixing imports
- Refactor job queue imports and conditionally import backends based on availability
- Bump version to v1.0.0b4
- Refactor imports and formatting across multiple modules
- Refactor imports and improve code formatting across multiple modules
- Add project configuration and update job queue management
- Bump version to v1.0.0b2
- Bump version to v1.0.0b1
- Added new README.md
- Refactor code structure for improved readability and maintainability - added a new `plugin` folder - mqtt is not a plugin (moved  `mqtt` into  `plugin`) - Added pipeline retry functionality
- feat: Add 'repomix-output.md' to .gitignore to exclude generated output files
- fix: Correct parameter name from 'worker_type' to 'job_queue_type' in PipelineRegistry
- feat: Update YAML configurations and improve CLI help documentation
- Refactor code structure and remove redundant code blocks for improved readability and maintainability
- feat: Enhance worker and scheduler cli with additional functionality and improved documentation
- feat: Enhance configuration management and CLI for FlowerPower
- updated deps
- Refactor code for improved readability and consistency
- Refactor code structure for improved readability and maintainability
- Enhance storage options management with detailed documentation and new features
- Refactor code structure for improved readability and maintainability
- feat: Add GeventWorker and ThreadWorker for concurrent job processing
- Add cron-descriptor and croniter packages; update dependencies
- Refactor PipelineManager and related components for improved logging and configuration handling
- Refactor PipelineScheduler and PipelineVisualizer for improved configuration handling
- Enhance PipelineRunner with context management and logging improvements
- refactor: Update worker configuration to use ProjectConfig and enhance logging setup
- Refactor logging setup and configuration
- refactor: Enhance pipeline and configuration structure, add new executor and adapter functionalities
- Refactor code structure for improved readability and maintainability
- refactor: Update project configuration to use PostgreSQL and enhance worker settings
- Refactor pipeline configuration and worker classes
- refactor: Enable port exposure for various services in docker-compose.yml
- Refactored docker-compose.yml and added a python-dev-worker container
- refactor: Correct JupyterCode references in nginx configuration and enhance docker-compose documentation
- refactor: Update configuration files and backend setup for improved clarity and consistency
- refactor: Simplify PipelineManager and PipelineRegistry methods for improved clarity and organization
- Refactor pipeline configuration and I/O management
- refactor: Clean up imports and update type hints across pipeline modules
- Refactor code for improved readability and consistency
- fix: Update storage_options type hint to support None in PipelineManager methods
- refactor: Update import paths for Pipeline and SchedulerManager to improve module organization
- feat: Add PipelineRunner, Scheduler, and Visualizer for enhanced pipeline management
- Refactor RQBackend job result methods
- feat: Add parameter resolution method and lazy worker instantiation in PipelineManager
- Implement code changes to enhance functionality and improve performance
- Refactor code structure for improved readability and maintainability
- feat: Remove unused example pipeline and script files; refactor worker configuration handling
- feat: Introduce APScheduler backend configuration and refactor worker classes
- Refactor: Remove TUI implementation and update worker backend type handling
- feat: Add worker example scripts and enhance backend configuration options
- feat: Refactor and optimize worker and backend code for clarity, robustness, and security
- feat: Implement Huey backend with trigger classes and worker integration
- Refactor worker and backend classes for improved structure and functionality
- feat: Enhance worker management with start/stop pool methods and refactor client usage
- chore: Update .gitignore to exclude all database files
- Implement RQ backend for FlowerPower scheduler
- feat: Implement base scheduler interface and RQ backend for FlowerPower
- Refactor APScheduler setup: move datastore and event broker implementations to separate modules
- Refactor configuration management and remove unused modules



## [0.10.3] - 2025-05-02

### Changes
- chore: update version to 0.10.3
- fix: clean up whitespace and improve code formatting across multiple files
- bugfixes: io methods to import and export pipelines fixed.
- Update README to include a subtitle and enhance visual presentation
- Refactor code structure for improved readability and maintainability; removed redundant code blocks and optimized function implementations.
- Add database and file writers/readers for various formats
- push test
- Refactor configuration and update Redis job queue settings



## [0.10.2] - 2025-04-29

### Changes
- Bump to version v0.10.2
- Refactor: Update pre-commit hook stages and clean up mqtt import statements
- refactor
- Refactor: Remove unnecessary blank lines and add deprecation warning for mqtt module
- Update version to 0.10.0, add retry configuration, and enhance job queue handling
- Update README.md
- fixing imports
- fixing imports
- Refactor job queue imports and conditionally import backends based on availability



## [0.10.1] - 2025-04-29

### Changes
- Update version to 0.10.0, add retry configuration, and enhance job queue handling
- Update README.md
- fixing imports
- fixing imports
- Refactor job queue imports and conditionally import backends based on availability



## [0.10.0] - 2025-04-29

### Changes
- Update version to 0.10.0, add retry configuration, and enhance job queue handling
- Update README.md
- fixing imports
- fixing imports
- Refactor job queue imports and conditionally import backends based on availability



## [1.0.0b4] - 2025-04-29

### Changes
- Bump version to v1.0.0b4
- Refactor imports and formatting across multiple modules
- Refactor imports and improve code formatting across multiple modules



## [1.0.0b3] - 2025-04-29

### Changes
- Refactor imports and improve code formatting across multiple modules
- Add project configuration and update job queue management



## [1.0.0b2] - 2025-04-29

### Changes
- Bump version to v1.0.0b2
- Bump version to v1.0.0b1
- Added new README.md
- Refactor code structure for improved readability and maintainability - added a new `plugin` folder - mqtt is not a plugin (moved  `mqtt` into  `plugin`) - Added pipeline retry functionality
- feat: Add 'repomix-output.md' to .gitignore to exclude generated output files
- fix: Correct parameter name from 'worker_type' to 'job_queue_type' in PipelineRegistry
- feat: Update YAML configurations and improve CLI help documentation
- Refactor code structure and remove redundant code blocks for improved readability and maintainability
- feat: Enhance worker and scheduler cli with additional functionality and improved documentation
- feat: Enhance configuration management and CLI for FlowerPower
- updated deps
- Refactor code for improved readability and consistency
- Refactor code structure for improved readability and maintainability
- Enhance storage options management with detailed documentation and new features
- Refactor code structure for improved readability and maintainability
- feat: Add GeventWorker and ThreadWorker for concurrent job processing
- Add cron-descriptor and croniter packages; update dependencies
- Refactor PipelineManager and related components for improved logging and configuration handling
- Refactor PipelineScheduler and PipelineVisualizer for improved configuration handling
- Enhance PipelineRunner with context management and logging improvements
- refactor: Update worker configuration to use ProjectConfig and enhance logging setup
- Refactor logging setup and configuration
- refactor: Enhance pipeline and configuration structure, add new executor and adapter functionalities
- Refactor code structure for improved readability and maintainability
- refactor: Update project configuration to use PostgreSQL and enhance worker settings
- Refactor pipeline configuration and worker classes
- refactor: Enable port exposure for various services in docker-compose.yml
- Refactored docker-compose.yml and added a python-dev-worker container
- refactor: Correct JupyterCode references in nginx configuration and enhance docker-compose documentation
- refactor: Update configuration files and backend setup for improved clarity and consistency
- refactor: Simplify PipelineManager and PipelineRegistry methods for improved clarity and organization
- Refactor pipeline configuration and I/O management
- refactor: Clean up imports and update type hints across pipeline modules
- Refactor code for improved readability and consistency
- fix: Update storage_options type hint to support None in PipelineManager methods
- refactor: Update import paths for Pipeline and SchedulerManager to improve module organization
- feat: Add PipelineRunner, Scheduler, and Visualizer for enhanced pipeline management
- Refactor RQBackend job result methods
- feat: Add parameter resolution method and lazy worker instantiation in PipelineManager
- Implement code changes to enhance functionality and improve performance
- Refactor code structure for improved readability and maintainability
- feat: Remove unused example pipeline and script files; refactor worker configuration handling
- feat: Introduce APScheduler backend configuration and refactor worker classes
- Refactor: Remove TUI implementation and update worker backend type handling
- feat: Add worker example scripts and enhance backend configuration options
- feat: Refactor and optimize worker and backend code for clarity, robustness, and security
- feat: Implement Huey backend with trigger classes and worker integration
- Refactor worker and backend classes for improved structure and functionality
- feat: Enhance worker management with start/stop pool methods and refactor client usage
- chore: Update .gitignore to exclude all database files
- Implement RQ backend for FlowerPower scheduler
- feat: Implement base scheduler interface and RQ backend for FlowerPower
- Refactor APScheduler setup: move datastore and event broker implementations to separate modules
- Refactor configuration management and remove unused modules



## [0.9.13.1] - 2025-04-28

### Changes
- Refactor code structure for improved readability and maintainability
- Enhance storage options management with detailed documentation and new features
- Refactor code structure for improved readability and maintainability
- feat: Add GeventWorker and ThreadWorker for concurrent job processing
- Add cron-descriptor and croniter packages; update dependencies
- Refactor PipelineManager and related components for improved logging and configuration handling
- Refactor PipelineScheduler and PipelineVisualizer for improved configuration handling
- Enhance PipelineRunner with context management and logging improvements
- refactor: Update worker configuration to use ProjectConfig and enhance logging setup
- Refactor logging setup and configuration
- refactor: Enhance pipeline and configuration structure, add new executor and adapter functionalities
- Refactor code structure for improved readability and maintainability
- refactor: Update project configuration to use PostgreSQL and enhance worker settings
- Refactor pipeline configuration and worker classes
- refactor: Enable port exposure for various services in docker-compose.yml
- Refactored docker-compose.yml and added a python-dev-worker container
- refactor: Correct JupyterCode references in nginx configuration and enhance docker-compose documentation
- refactor: Update configuration files and backend setup for improved clarity and consistency
- refactor: Simplify PipelineManager and PipelineRegistry methods for improved clarity and organization
- Refactor pipeline configuration and I/O management
- refactor: Clean up imports and update type hints across pipeline modules
- Refactor code for improved readability and consistency
- fix: Update storage_options type hint to support None in PipelineManager methods
- refactor: Update import paths for Pipeline and SchedulerManager to improve module organization
- feat: Add PipelineRunner, Scheduler, and Visualizer for enhanced pipeline management
- Refactor RQBackend job result methods
- feat: Add parameter resolution method and lazy worker instantiation in PipelineManager
- Implement code changes to enhance functionality and improve performance
- Refactor code structure for improved readability and maintainability
- feat: Remove unused example pipeline and script files; refactor worker configuration handling
- feat: Introduce APScheduler backend configuration and refactor worker classes
- Refactor: Remove TUI implementation and update worker backend type handling
- feat: Add worker example scripts and enhance backend configuration options
- feat: Refactor and optimize worker and backend code for clarity, robustness, and security
- feat: Implement Huey backend with trigger classes and worker integration
- Refactor worker and backend classes for improved structure and functionality
- feat: Enhance worker management with start/stop pool methods and refactor client usage
- chore: Update .gitignore to exclude all database files
- Implement RQ backend for FlowerPower scheduler
- feat: Implement base scheduler interface and RQ backend for FlowerPower
- Refactor APScheduler setup: move datastore and event broker implementations to separate modules
- Refactor configuration management and remove unused modules



## [0.9.13.1] - 2025-04-28

### Changes
- Bump version to 0.9.13.1




## [0.9.13.0] - 2025-04-28

### Changes
- Bump version to 0.9.13.0
- name for hook function can be set by cli creation
- add config option to show/save dag to alllow to draw dag with config
- added a config hook to run-pipeline-on-message
- added option config hook to mqtt cli
- added load_hooks function to cli utils
- added method to add a hook template to the project for a specific pipeline
- added template for mqqt config hook method
- added mosquitto.db for docker
- Corrected output message in pipeline delete for deleting module
- added option to delete hooks in pipeline delete function
- adding pipeline to hooks folder when creating pipeline
- create new hook folder on init
- bugfix: mmh3 was in open-telemetry group chaned to mqtt
- moved mmh3 to mqtt group
- removed unused imports
- added a determinstic client_id creation when connecting to broker as persisten client (clean_session = false)
- added client_id_suffix to allow multiple clients to conect to a broker from same host with different endings
- self._client needs to be set before call to subscribe
- config anpassungeng für tests
- client_id and clean_session from cli overwrites given config
- added custom client_id in MQTTManager
- added clean_session, client_id and qos to cli
- added client_id
- added clean_session and qos in run_pipieline_on_message command







