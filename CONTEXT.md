# FlowerPower Context

FlowerPower is a configuration-driven framework for building and executing Hamilton data pipelines. This glossary pins down project-specific language used when discussing pipeline configuration and execution.

## Language

**RunConfig**:
The complete set of execution settings for one pipeline run.
_Avoid_: resolved run context, config state, runtime config soup


**Project Facade**:
The stable entry point for coordinating a FlowerPower project's pipeline catalog, configuration, execution, visualization, creation, and transfer workflows.
_Avoid_: god manager, orchestration grab-bag, project context soup