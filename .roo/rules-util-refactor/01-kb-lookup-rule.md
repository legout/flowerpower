+++
id = "util-refactor-kb-lookup"
title = "KB Lookup Rule for util-refactor"
context_type = "rules"
scope = "Knowledge Base Lookup Procedure"
target_audience = ["util-refactor"]
granularity = "rule"
status = "active"
last_updated = "2025-04-19" # Using today's date
# version = "1.0"
# related_context = []
tags = ["kb", "lookup", "util-refactor", "rules"]
# relevance = "High"
target_mode_slug = "util-refactor"
kb_directory = ".modes/util-refactor/kb/"
+++

# Knowledge Base Lookup Rule

**Applies To:** `util-refactor` mode

**Rule:** Before responding to any user request or starting a task, **ALWAYS** check your dedicated Knowledge Base (KB) directory located at `.modes/util-refactor/kb/` for relevant information, guidelines, examples, or procedures.

**Procedure:**

1.  **Consult KB:** Prioritize reviewing the contents of the `.modes/util-refactor/kb/` directory.
2.  **Start with README:** Begin by reading the `README.md` file within the KB directory (if it exists) to get an overview of the available knowledge and its organization.
3.  **Apply Knowledge:** Integrate any relevant findings from the KB into your analysis, planning, and execution of the task. If the KB provides specific instructions or constraints, adhere to them strictly.
4.  **Proceed if KB is Empty/Irrelevant:** If the KB directory is empty, does not contain relevant information for the current task, or you have already consulted it thoroughly, proceed with the task based on your core instructions and the user's request.

**Rationale:** This ensures that the mode leverages specialized knowledge, best practices, and established procedures defined for its specific function, leading to more consistent, accurate, and efficient task execution. Even if the KB is currently empty, this rule establishes the standard operating procedure for future knowledge additions.