# Change Proposal: Group RunConfig retry fields into RetryConfig

- change-id: refactor-run-retry-config
- owner: cfg/pipeline
- status: proposal

## Overview
Group the retry-related settings on RunConfig into a dedicated RetryConfig struct and replace the four top-level fields with a single retry field. Preserve behavior and provide a backward-compatible deprecation path for existing users (YAML, CLI, and builders).

## Motivation
- Cohesion: keep all retry concerns together and easier to extend later.
- Clarity: reduce top-level RunConfig surface area.
- Compatibility: allow phased migration without breaking existing configs and code.

## Affected Areas
- src/flowerpower/cfg/pipeline/run.py (new RetryConfig, RunConfig changes)
- src/flowerpower/pipeline/pipeline.py (reads retry config)
- src/flowerpower/cfg/pipeline/builder.py, src/flowerpower/utils/config.py (builders and serialization)
- src/flowerpower/cli/pipeline.py (flags mapping)
- tests/* (cfg, pipeline, cli)

---

## Spec Deltas (changes/refactor-run-retry-config/specs/run-config/spec.md)

### ADDED Requirements

- Requirement: The system MUST define RetryConfig as a msgspec model to hold retry settings.
  - Fields: max_retries:int=3, retry_delay:float=1.0, jitter_factor:float|None=0.1, retry_exceptions:list[str|type]=["Exception"].
  - Methods: __post_init__ MUST convert retry_exceptions strings to classes (same logic as current RunConfig).
  - Scenario: Given retry: {max_retries:2,retry_delay:0.5,jitter_factor:0.2,retry_exceptions:["ValueError"]} in YAML, when loaded, runtime sees retry.retry_exceptions == [ValueError].

- Requirement: RunConfig MUST expose a retry: RetryConfig field with default RetryConfig().
  - Scenario: Given no retry provided, RunConfig.retry defaults to values (3,1.0,0.1,[Exception]).

- Requirement: YAML/Dict configs MAY specify a nested retry object.
  - Scenario: Given run: { retry: { max_retries: 5 } }, RunConfig.retry.max_retries == 5.

- Requirement: Builder API MUST allow setting nested retry values.
  - Scenario: RunConfigBuilder.with_retry_config(max_retries=5) sets config.retry.max_retries == 5.

### MODIFIED Requirements

- Requirement: The execution layer MUST read retry settings from RunConfig.retry with fallback for deprecated top-level fields during transition.
  - Scenario: Pipeline.run uses run_config.retry.max_retries, etc.; if retry is None but top-level deprecated fields present, it MUST derive RetryConfig from them.

- Requirement: RunConfig.__post_init__ MUST map deprecated top-level fields into retry when retry is missing, and issue DeprecationWarning.
  - Precedence: explicit retry takes precedence over top-level fields; if both present, top-level are ignored and a warning is emitted.
  - Scenario: Given max_retries:2 and retry:{max_retries:4}, effective retry.max_retries == 4 and a warning is raised.

### REMOVED Requirements (planned)

- Requirement: The top-level fields max_retries, retry_delay, jitter_factor, retry_exceptions on RunConfig are removed from the public API in a future release after deprecation.
  - Scenario (post-removal): Accessing run_config.max_retries raises AttributeError; YAML with those keys fails validation unless a migration flag is enabled.

---

## Design (changes/refactor-run-retry-config/design.md)

- Structure:
  - New struct co-located in run.py:
    ```python
    class RetryConfig(BaseConfig):
        max_retries: int = msgspec.field(default=3)
        retry_delay: float = msgspec.field(default=1.0)
        jitter_factor: float | None = msgspec.field(default=0.1)
        retry_exceptions: list[str | type[BaseException]] = msgspec.field(default_factory=lambda: ["Exception"])  # converted in __post_init__

        def __post_init__(self):
            if isinstance(self.retry_exceptions, list):
                self.retry_exceptions = _convert_exception_strings(self.retry_exceptions)
    ```
  - RunConfig changes:
    ```python
    class RunConfig(BaseConfig):
        # ... existing fields ...
        retry: RetryConfig = msgspec.field(default_factory=RetryConfig)
        # [DEPRECATED] remove top-level retry fields; accept during transition
        def __post_init__(self):
            # existing conversions ...
            # map deprecated fields -> retry when retry not provided
            deprecated_present = any(k in self.__dict__ for k in ("max_retries","retry_delay","jitter_factor","retry_exceptions"))
            if deprecated_present and not getattr(self, "retry", None):
                self.retry = RetryConfig(
                    max_retries=getattr(self, "max_retries", 3),
                    retry_delay=getattr(self, "retry_delay", 1.0),
                    jitter_factor=getattr(self, "jitter_factor", 0.1),
                    retry_exceptions=getattr(self, "retry_exceptions", ["Exception"]),
                )
                warnings.warn("RunConfig top-level retry fields are deprecated; use run.retry.*", DeprecationWarning)
            elif deprecated_present and getattr(self, "retry", None):
                warnings.warn("Ignoring deprecated RunConfig top-level retry fields because retry is set", DeprecationWarning)
    ```
  - Exception conversion helpers are kept as-is and reused by RetryConfig.
- CLI: keep existing flags (max_retries, retry_delay, jitter_factor, retry_exceptions) for now; they populate RunConfig.retry. A future follow-up may add a single --retry (JSON) option.
- Builders: forwarder methods (with_max_retries, with_retry_delay, with_jitter_factor, with_retry_exceptions) set nested retry fields. Add with_retry(self, retry: RetryConfig|dict) for convenience.
- Validation: existing non-negative checks move to the nested RetryConfig or use run.retry in builder validation.

---

## Migration & Compatibility
- Accept both shapes during deprecation window; prefer nested retry when both provided.
- Emit DeprecationWarning whenever deprecated fields are used.
- YAML/serialization: utils/config should list 'retry' as allowed and omit deprecated keys when writing.

---

## Tasks (changes/refactor-run-retry-config/tasks.md)
1. Implement RetryConfig in run.py; move exception conversion to it (unit tests).
2. Update RunConfig: add retry field; implement __post_init__ mapping and deprecation warnings.
3. Replace internal uses in pipeline/pipeline.py to consume run_config.retry.* with fallback helper for BC.
4. Update cfg/pipeline/builder.py validations to use retry; modify setters to write into retry.*.
5. Update utils/config.py keys and RunConfigBuilder.with_retry_config/with_max_retries/etc to target retry.*.
6. CLI: map flags into RunConfig.retry; ensure help text indicates deprecation of top-level fields.
7. Update tests:
   - tests/cfg/test_run_config.py (new nested cases + BC tests)
   - tests/pipeline/* (read from retry)
   - tests/cli/* (flags still work)
8. Validate: ruff, mypy, pytest; ensure no warnings except intentional deprecations.

---

## Validation
- Unit: pytest -q ensures no behavior regression; new tests confirm nested config path.
- Type-check: uv run mypy src/flowerpower
- Lint: uv run ruff check

## Out of Scope
- Removing CLI flags; changes to retry algorithm/timing.

If this spec looks good, I’ll implement it and update tests accordingly.