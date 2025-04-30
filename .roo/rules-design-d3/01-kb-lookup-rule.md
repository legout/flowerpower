+++
id = "design-d3-kb-lookup"
title = "KB Lookup Rule for design-d3"
context_type = "rules"
scope = "Knowledge Base Lookup for design-d3 Mode"
target_audience = ["design-d3"]
granularity = "ruleset"
status = "active"
last_updated = "2025-04-19" # Assuming today's date
# version = ""
# related_context = []
tags = ["kb-lookup", "design-d3", "rules"]
# relevance = ""
target_mode_slug = "design-d3"
kb_directory = ".ruru/modes/design-d3/kb/"
+++

# Knowledge Base (KB) Lookup Rule

**Objective:** Ensure the `design-d3` mode consistently consults its dedicated Knowledge Base (KB) directory (`.ruru/modes/design-d3/kb/`) before proceeding with tasks or providing answers.

**Rule:**

1.  **Prioritize KB:** Before generating any response, code, or plan, **ALWAYS** first examine the contents of the `.ruru/modes/design-d3/kb/` directory.
2.  **Consult Relevant Files:** Identify and read any files within the KB directory that appear relevant to the current task or query. Pay attention to file names and the `README.md` if present.
3.  **Synthesize Information:** Integrate the information found in the KB into your thought process and final output.
4.  **Cite Sources (If Applicable):** If specific information from a KB file is used directly, briefly mention the source file (e.g., "Based on guidance in `kb/01-core-principles.md`...").
5.  **Proceed if KB is Empty/Irrelevant:** If the KB directory is empty, contains no relevant files for the current task, or you have already consulted the relevant files, proceed with the task using your general knowledge and the provided context.
6.  **Do Not Modify KB:** This rule is for *reading* the KB only. Do not add, delete, or modify files within the `.ruru/modes/design-d3/kb/` directory unless specifically instructed by a separate task.

**Rationale:** This rule ensures that the mode leverages its specialized knowledge base, promoting consistency, accuracy, and adherence to established patterns or guidelines defined for the `design-d3` mode. Even if the KB is currently empty, adhering to this lookup process establishes the correct operational pattern for the future.