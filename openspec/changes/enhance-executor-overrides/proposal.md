# Change Proposal: Enhance executor overrides and CLI support

Change-ID: enhance-executor-overrides

## Summary
Enable full control over pipeline executors from Python and CLI, including selecting a synchronous executor and overriding parameters (max_workers, num_cpus). Add predictable merge semantics so runtime overrides take precedence over YAML defaults.

## Motivation
- Users need to choose synchronous execution to run nodes sequentially.
- CLI lacked a way to pass executor parameters.
- Merge behavior occasionally ignored user overrides when equal to defaults.

## Scope
- Pipeline merging logic for ExecutorConfig.
- CLI: new options for executor configuration.
- Minimal unit tests for override helper.

## Out of Scope
- Changes to ExecutorFactory logic.
- Broader adapter/config refactors.

## Risks
- Merge precedence change may affect edge cases; mitigated by preserving YAML for omitted fields and only preferring explicitly provided values.
