+++
id = "KB-LOOKUP-DESIGN-ANTD"
title = "KB Lookup Rule: design-antd"
context_type = "rules"
scope = "Mode-specific knowledge base access"
target_audience = ["design-antd"]
granularity = "rule"
status = "active"
last_updated = "2025-04-20" # Using today's date
# version = ""
# related_context = []
tags = ["kb-lookup", "design-antd", "knowledge-base", "design", "ui-library", "antd", "react", "frontend"]
# relevance = ""
target_mode_slug = "design-antd"
kb_directory = ".ruru/modes/design-antd/kb/"
+++

# Knowledge Base (KB) Lookup Rule

**Applies To:** `{{target_mode_slug}}` mode

**Rule:**

Before attempting a task, **ALWAYS** consult the dedicated Knowledge Base (KB) directory for this mode located at:

`{{kb_directory}}`

**Procedure:**

1.  **Identify Keywords:** Determine the key concepts, tools, or procedures relevant to the current task.
2.  **Scan KB:** Review the filenames and content within the `{{kb_directory}}` for relevant documents (e.g., principles, workflows, examples, best practices, common issues). Pay special attention to `README.md` if it exists.
3.  **Apply Knowledge:** Integrate relevant information from the KB into your task execution plan and response.
4.  **If KB is Empty/Insufficient:** If the KB doesn't contain relevant information, proceed using your core capabilities and general knowledge, but note the potential knowledge gap.

**Rationale:** This ensures the mode leverages specialized, curated knowledge for consistent and effective operation, even if the KB is currently sparse or empty. Adhering to this rule promotes maintainability and allows for future knowledge expansion.