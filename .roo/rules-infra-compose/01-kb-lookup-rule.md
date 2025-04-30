+++
id = "infra-compose-kb-lookup"
title = "KB Lookup Rule for infra-compose"
context_type = "rules"
scope = "Mode-specific knowledge base access"
target_audience = ["infra-compose"]
target_mode_slug = "infra-compose"
kb_directory = ".ruru/modes/infra-compose/kb/"
granularity = "ruleset"
status = "active"
last_updated = "2025-04-19"
# version = ""
# related_context = []
tags = ["kb", "lookup", "infra-compose", "rules"]
# relevance = ""
+++

# Knowledge Base Lookup Rule for infra-compose

**Objective:** Ensure the `infra-compose` mode leverages its dedicated Knowledge Base (KB) for relevant context, best practices, and specific instructions before executing tasks.

**Rule:**

1.  **Consult KB First:** Before starting any task, **ALWAYS** consult the contents of your dedicated Knowledge Base directory: `.ruru/modes/infra-compose/kb/`.
2.  **Identify Relevant Documents:** Look for documents within the KB that relate to the current task, keywords, or concepts involved. Pay attention to file names and content summaries (if available, e.g., in a `README.md`).
3.  **Prioritize KB Guidance:** If relevant information, instructions, patterns, or constraints are found in the KB, prioritize them in your approach.
4.  **Proceed if No Relevant KB:** If no relevant documents are found after a reasonable check, proceed with the task using your general knowledge and the provided instructions.
5.  **Continuous Improvement:** If you encounter situations or develop solutions that are not covered in the KB but would be valuable for future tasks, recommend adding them to the KB.