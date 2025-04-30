+++
id = "data-elasticsearch-kb-lookup"
title = "KB Lookup Rule for data-elasticsearch"
context_type = "rules"
scope = "Knowledge Base Lookup Guidance" # Standard scope for KB rules
target_audience = ["data-elasticsearch"] # Target the specific mode
granularity = "rule" # More specific than ruleset
status = "active"
last_updated = "2025-04-19" # Use today's date
# version = "1.0"
# related_context = []
tags = ["kb", "lookup", "data-elasticsearch", "rules"] # Add relevant tags
# relevance = "High" # Optional, but good practice
kb_directory = ".ruru/modes/data-elasticsearch/kb/" # Add the specific KB directory field
+++

# Knowledge Base Lookup Rule

**Objective:** Ensure the mode leverages its dedicated Knowledge Base (KB) for relevant information, best practices, and specific instructions before proceeding with tasks.

**Rule:**

1.  **Consult KB First:** Before starting any task or answering a query, **ALWAYS** check the contents of your dedicated Knowledge Base directory: `.ruru/modes/data-elasticsearch/kb/`.
2.  **Prioritize KB Content:** Information found within your KB (files like `README.md`, `01-principles.md`, `02-patterns.md`, etc.) takes precedence over general knowledge. These files contain specific guidelines, approved methods, and context relevant to your function.
3.  **Search Systematically:** Review the `README.md` first for an overview, then look for files relevant to the current task (e.g., for coding standards, check `coding-style.md`; for API usage, check `api-integration.md`).
4.  **Apply Learned Information:** Integrate the knowledge gained from the KB into your response, analysis, or task execution. Reference specific KB documents if it aids clarity.
5.  **If KB is Empty/Insufficient:** If the KB does not contain relevant information for the specific task, proceed using your general knowledge and best practices, but explicitly state that the KB was consulted and lacked specific guidance for this scenario.
6.  **Do Not Hallucinate KB Content:** Never invent or assume information is in the KB if it's not present.

**Rationale:** This ensures the mode operates according to established project standards, utilizes specialized knowledge effectively, and maintains consistency in its outputs and actions. Consulting the KB first reduces errors and aligns the mode's behavior with project-specific requirements.