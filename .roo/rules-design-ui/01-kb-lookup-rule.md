+++
id = "design-ui-kb-lookup"
title = "KB Lookup Rule for design-ui"
context_type = "rules"
scope = "Mode-specific rule" # Defines the applicability of this rule
target_audience = ["design-ui"] # Specifies which mode(s) this rule applies to
granularity = "ruleset" # Indicates this file contains a set of rules (even if just one)
status = "active" # Current status of the rule
last_updated = "2025-04-19" # Date of last modification
# version = "1.0" # Optional versioning
# related_context = [] # Optional links to related documents
tags = ["kb-lookup", "design-ui", "rules"] # Keywords for categorization and search
# relevance = "High" # Optional indicator of importance

# --- KB Lookup Specific Fields ---
target_mode_slug = "design-ui" # The mode this rule specifically targets
kb_directory = ".ruru/modes/design-ui/kb/" # The designated knowledge base directory for the target mode
+++

# Knowledge Base Consultation Rule for design-ui

**Objective:** Ensure that the `design-ui` mode leverages its dedicated knowledge base (KB) effectively before proceeding with tasks.

**Rule:**

1.  **Identify Task Context:** Before taking any action, analyze the current task and identify the key concepts, tools, patterns, or principles involved.
2.  **Consult KB:** Access and thoroughly review the contents of the designated knowledge base directory: `{{kb_directory}}`.
    *   Look for relevant files (e.g., `01-principles.md`, `02-workflow.md`, `03-component-library.md`, etc.) based on the task context.
    *   Pay close attention to established guidelines, best practices, preferred tools, common pitfalls, and specific instructions documented within the KB.
3.  **Apply Knowledge:** Integrate the information and guidance found in the KB into your planning and execution of the task.
4.  **Proceed:** Only after consulting the KB should you proceed with generating responses, writing code, or performing other actions related to the task.
5.  **If KB is Empty/Insufficient:** If the KB is empty or lacks relevant information for the current task, proceed using your general knowledge and best practices, but make a note (e.g., in thinking tags or suggesting a documentation update) that the KB could be improved for future similar tasks.