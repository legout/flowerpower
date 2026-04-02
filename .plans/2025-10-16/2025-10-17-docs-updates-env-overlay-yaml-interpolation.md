I will update the documentation to reflect the new configuration behavior:

- docs/docs/advanced.md: revise configuration precedence to: kwargs > FP_PIPELINE__* env > YAML (after interpolation) > FP_* globals > code defaults. Add examples for both overlays and YAML ${VAR} forms with JSON coercion and escaping.
- docs/docs/api/configuration.md: add a section describing env overlays (FP_PROJECT__/FP_PIPELINE__/FP_* shims), typed coercion, and YAML env interpolation. Note retry normalization into nested RunConfig.retry.
- docs/docs/api/cli_pipeline.md: correct the executor_cfg JSON example quoting and add a short note that environment variables can override run settings via FP_PIPELINE__RUN__*.
- docs/docs/index.md or quickstart.md: add a brief callout about YAML ${VAR} support and env override precedence.

No code changes, only Markdown edits in docs.