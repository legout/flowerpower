+++
id = "PRIME-DEV-RULE-FORMAT-V1"
title = "Prime Config Editor: Rule - Adhere to File Formats"
context_type = "rules"
scope = "Ensuring syntax validity during edits"
target_audience = ["prime-dev"]
granularity = "guideline"
status = "active"
last_updated = "2025-04-21"
tags = ["rules", "formatting", "syntax", "toml", "markdown", "prime-dev"]
related_context = [".roo/rules/01-standard-toml-md-format.md"]
+++

# Rule: Adhere to File Formats

**Requirement:** When preparing changes for configuration files, you **MUST** ensure the modifications maintain the correct syntax for the target file type.

**Specific Attention:**

*   **`.mode.md` Files:** These files use the TOML+Markdown standard.
    *   Ensure all changes within the `+++` delimiters adhere strictly to valid **TOML** syntax (`key = "value"`, arrays `[...]`, etc.).
    *   Ensure all changes *outside* the `+++` delimiters use valid **Markdown**.
    *   Consult the workspace standard `.roo/rules/01-standard-toml-md-format.md` for detailed TOML+MD specifications if necessary.
*   **`.js` / `.ts` Files:** Maintain valid JavaScript/TypeScript syntax.
*   **`.json` Files:** Maintain valid JSON syntax.
*   **`.toml` Files:** Maintain valid TOML syntax.