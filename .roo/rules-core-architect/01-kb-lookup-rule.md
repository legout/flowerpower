+++
id = "KB-LOOKUP-CORE-ARCHITECT"
title = "KB Lookup Rule: Technical Architect"
context_type = "rules"
scope = "Knowledge Base Lookup Configuration" # Added a reasonable scope
target_audience = ["core-architect"] # Added target audience
granularity = "ruleset"
status = "active"
last_updated = "2025-04-18" # Updated date
# version = ""
# related_context = []
tags = ["kb-lookup", "core-architect", "rules"] # Added relevant tags
# relevance = ""
target_mode_slug = "core-architect"
kb_directory = ".ruru/modes/core-architect/kb"
+++

# Knowledge Base Lookup Rule

This rule defines how the `core-architect` mode should access its dedicated Knowledge Base (KB) located in the specified `kb_directory`.

**Purpose:** To ensure the mode consistently retrieves relevant architectural principles, patterns, best practices, and project-specific context stored within its KB.

**Mechanism:** When the `core-architect` mode needs to consult its knowledge base (e.g., before making a design decision, evaluating options, or providing guidance), it should perform a lookup within the `.ruru/modes/core-architect/kb` directory. The lookup mechanism might involve:

1.  **Semantic Search:** Searching the content of files within the KB directory based on the current task or query.
2.  **Keyword Search:** Searching for specific keywords or concepts.
3.  **File Retrieval:** Accessing specific, known files (e.g., `01-design-principles.md`, `05-technology-stack.md`) if their relevance is clear.

**Expected Behavior:**

*   The mode should prioritize information found within its designated KB.
*   The lookup should be triggered automatically or explicitly when architectural knowledge is required.
*   The results of the lookup should inform the mode's subsequent actions and responses.

*(Note: The specific implementation of the lookup mechanism depends on the underlying system capabilities.)*