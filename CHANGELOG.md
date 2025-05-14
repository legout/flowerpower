# Changelog

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







