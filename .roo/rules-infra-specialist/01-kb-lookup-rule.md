+++
id = "infra-specialist-kb-lookup"
title = "KB Lookup Rule for infra-specialist"
context_type = "rules"
scope = "Mode-specific knowledge base guidance"
target_audience = ["infra-specialist"]
granularity = "rule"
status = "active"
last_updated = "2025-04-19"
# version = "1.0"
# related_context = []
tags = ["kb", "knowledge-base", "infra-specialist", "rule"]
# relevance = "High"
target_mode_slug = "infra-specialist"
kb_directory = ".ruru/modes/infra-specialist/kb/"
+++

# Knowledge Base Lookup Rule

**Objective:** Ensure the `infra-specialist` mode consistently consults its dedicated Knowledge Base (KB) for relevant information, best practices, and established patterns before proceeding with tasks.

**Rule:**

1.  **Prioritize KB:** Before generating responses or taking actions, **ALWAYS** first consult the contents of your dedicated Knowledge Base directory: `.ruru/modes/infra-specialist/kb/`.
2.  **Check for Relevance:** Review the files within the KB directory (including subdirectories) to find information pertinent to the current task or query. Pay attention to file names and content structure (e.g., `01-principles.md`, `02-common-patterns.md`, `03-tool-usage.md`).
3.  **Apply Knowledge:** If relevant information is found, integrate it into your response or action plan. Adhere to the guidelines, principles, and examples provided in the KB.
4.  **Acknowledge Gaps:** If the KB does not contain relevant information for the specific task, proceed using your general knowledge and capabilities, but consider if this gap represents an opportunity to suggest adding new information to the KB later.
5.  **Continuous Learning:** Treat the KB as a living resource. As new patterns emerge or best practices are updated, expect the KB to evolve.

**Rationale:** Consulting the KB ensures consistency, adherence to project standards, leverages collective knowledge, and reduces redundant problem-solving. Even if the KB is currently sparse, establishing this lookup habit is crucial for future scalability and knowledge management.