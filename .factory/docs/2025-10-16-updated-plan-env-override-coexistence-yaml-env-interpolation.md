## Additions to the Plan

### 1) Coexistence of FP_LOG_LEVEL and FP_PIPELINE__RUN__LOG_LEVEL
- Precedence: kwargs > FP_PIPELINE__RUN__LOG_LEVEL > YAML run.log_level > FP_LOG_LEVEL > hardcoded default.
- Rationale: namespaced pipeline overrides are more specific than global; fall back to global only if pipeline-level missing.
- Apply same pattern for other settings with both a global and namespaced variant (e.g., executor.type, retry.max_retries).
- Implementation: in apply_env_overrides(), first parse global FP_* keys into global overlay, then parse FP_PIPELINE__* and FP_PROJECT__* into precise structs, merge with specificity-aware precedence.

### 2) YAML Env Interpolation (Docker Compose–style)
- Syntax: ${VAR}, ${VAR:-default}, ${VAR-default}, ${VAR:?err}, ${VAR?err}, support escaping: $${VAR} -> literal.
- Evaluation:
  - Run before YAML → dict conversion (line-by-line) or after load via recursive traversal over strings.
  - Prefer post-load traversal: safer and enables JSON coercion.
- Type coercion:
  - If interpolated value parses as JSON (object/array/number/bool/null), use parsed type.
  - Else keep as string; add optional type hints via suffixes if ever needed (not required now).
- Security: Only environment variables; no command substitution. Provide allowlist prefix FP_/HAMILTON_* by default, but allow opt-in to any env with flag (e.g., allow_all_env=True) to avoid surprises.
- Examples:
  - run.executor: ${FP_EXECUTOR:-threadpool}
  - adapter.hamilton_tracker.api_key: ${HAMILTON_API_KEY:?Missing tracker key}
  - run.retry: ${FP_PIPELINE__RUN__RETRY:-{"max_retries":3}}

### 3) Updated Precedence Model
1. Code defaults in msgspec structs (no import-time env reads)
2. YAML load
3. YAML env interpolation expansion (applied to strings in the YAML data)
4. Env overlay with specificity-aware precedence:
   - project-wide: FP_PROJECT__*
   - pipeline: FP_PIPELINE__*
   - global shims: FP_* (apply to reasonable defaults like log level, executor.type, retry fields) when more specific keys absent
5. Runtime kwargs into RunConfig (existing merge util)

### 4) Back-Compat and Transition
- Keep FP_LOG_LEVEL working as today, but evaluated in the new overlay phase; FP_PIPELINE__RUN__LOG_LEVEL takes priority when present.
- Maintain current settings/* as adapters for legacy global envs; gradually refactor to rely on the overlay output; avoid bool(os.getenv(...)).
- Add tests: coexistence cases, interpolation variants, JSON coercion, escaping, precedence.

### 5) Minimal API/Code Changes
- utils/env.py: env parsing + coercion + overlay builder.
- utils/yaml_env.py: interpolation walker (post-load traversal) respecting Docker Compose semantics and escaping.
- Config.load(..., apply_env=True, interpolate_env=True) hooks; PipelineConfigManager to delegate to Config or call same utilities for parity.

If you confirm, I’ll implement: 1) env overlay with coexistence semantics, 2) YAML env interpolation with JSON coercion, 3) wire-in to Config.load/manager, plus tests.