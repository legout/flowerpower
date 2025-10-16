1. Add prefer_executor_override helper to utils.config with precedence rules; test it.
2. Update Pipeline._get_executor to use prefer_executor_override; keep fallback.
3. Extend CLI pipeline run with --executor-cfg, --executor-max-workers, --executor-num-cpus; validate type.
4. Ensure synchronous selection works via YAML/REPL/CLI; covered by existing tests and helper test.
5. Run tests and lint.
