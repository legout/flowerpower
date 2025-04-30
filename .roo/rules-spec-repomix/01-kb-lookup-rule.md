+++
id = "RULE-SPEC-REPOMIX-KB-LOOKUP-V1"
title = "spec-repomix: Rule - KB Lookup"
context_type = "rules"
scope = "Mode-specific knowledge base access"
target_audience = ["spec-repomix"]
granularity = "rule"
status = "active"
last_updated = "2025-04-26"
# version = "1.0"
related_context = [".ruru/modes/spec-repomix/kb/"]
tags = ["kb", "lookup", "mode-specific", "spec-repomix", "repomix"]
# relevance = "High: Ensures mode uses specialized knowledge"
+++

# Knowledge Base (KB) Lookup Rule

**Applies To:** `spec-repomix` mode

**Rule:**

Before attempting any task involving `repomix`, **ALWAYS** consult the dedicated Knowledge Base (KB) directory for this mode located at:

`.ruru/modes/spec-repomix/kb/`

**Procedure:**

1.  **Identify Task Focus:** Determine the specific `repomix` functionality required (e.g., command generation, configuration, filtering, output formatting).
2.  **Scan KB:** Review the filenames and content within `.ruru/modes/spec-repomix/kb/` for relevant documents. Pay special attention to:
    *   `README.md`: For an overview and navigation guide within the KB.
    *   Documents related to `repomix` commands, `repomix.config.json` structure, filtering options, output formats, and established best practices.
3.  **Apply Knowledge:** Integrate relevant information from the KB into your task execution plan and response.
4.  **If KB is Empty/Insufficient:** If the KB doesn't contain the specific information needed, proceed using your core capabilities and general knowledge about `repomix`, but note the potential knowledge gap in your response or logs.

**Rationale:** This ensures the `spec-repomix` mode leverages specialized, curated knowledge for consistent and effective operation when dealing with `repomix` tasks. Adhering to this rule promotes maintainability and allows for future knowledge expansion specific to `repomix` usage within this project.