+++
id = "DEV-PYTHON-KB-LOOKUP-V1"
title = "dev-python: KB Lookup Rule"
context_type = "rules"
scope = "Mode-specific knowledge base access for dev-python"
target_audience = ["dev-python"]
granularity = "rule"
status = "active"
last_updated = "2025-04-25" # Using today's date
# version = "1.0"
related_context = [
    ".ruru/modes/dev-python/kb/",
    ".ruru/modes/dev-python/kb/README.md" # If it exists
    ]
tags = ["kb", "lookup", "mode-specific", "dev-python", "rules", "python"]
template_schema_doc = ".ruru/templates/toml-md/16_ai_rule.README.md"
relevance = "High: Ensures use of curated Python knowledge"
+++

# Knowledge Base (KB) Lookup Rule for `dev-python`

**Applies To:** `dev-python` mode

**Rule:**

Before attempting any Python-related task (code generation, analysis, refactoring, debugging, providing advice), **ALWAYS** consult the dedicated Knowledge Base (KB) directory for this mode located at:

`.ruru/modes/dev-python/kb/`

**Procedure:**

1.  **Identify Keywords:** Determine the key Python concepts, libraries, frameworks, tools, or project-specific requirements relevant to the current task.
2.  **Scan KB:** Review the filenames and content within the `.ruru/modes/dev-python/kb/` directory for relevant documents. Pay special attention to:
    *   `README.md` (if it exists) for an overview.
    *   Files covering Python 3 best practices, standard library usage, common patterns (e.g., virtual environments, error handling, testing).
    *   Documentation on specific libraries or frameworks mentioned in the task (e.g., `requests`, `pandas`, `numpy`, `Flask`, `Django`, `FastAPI`).
    *   Project-specific coding standards or architectural guidelines related to Python.
3.  **Apply Knowledge:** Integrate relevant information from the KB into your task execution plan, code generation, and responses. Prioritize KB information over general knowledge when available.
4.  **If KB is Empty/Insufficient:** If the KB doesn't contain relevant information for the specific task, proceed using your core Python expertise and general best practices, but note the potential knowledge gap in your internal reasoning or logs if appropriate.

**Rationale:** This ensures the `dev-python` mode leverages specialized, curated knowledge for consistent, high-quality, and contextually appropriate Python development, adhering to established project standards and best practices.