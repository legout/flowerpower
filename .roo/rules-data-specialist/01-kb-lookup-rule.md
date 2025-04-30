+++
id = "data-specialist-kb-lookup"
title = "KB Lookup Rule for data-specialist"
context_type = "rules"
scope = "Mode-specific knowledge base guidance"
target_audience = ["data-specialist"]
target_mode_slug = "data-specialist"
kb_directory = ".ruru/modes/data-specialist/kb/"
granularity = "rule"
status = "active"
last_updated = "2025-04-19" # Assuming today's date
# version = "1.0"
# related_context = []
tags = ["kb", "knowledge-base", "data-specialist", "rules"]
# relevance = "High"
+++

# Knowledge Base (KB) Lookup Rule

**Objective:** To ensure you effectively leverage your dedicated Knowledge Base (KB) for consistent, accurate, and context-aware responses and actions.

**Rule:**

1.  **Consult KB First:** Before attempting any task, generating complex responses, or making decisions based on your core programming, **ALWAYS** first consult the contents of your dedicated Knowledge Base directory: `.ruru/modes/data-specialist/kb/`.
2.  **Prioritize KB:** Information, guidelines, procedures, or examples found within your KB take precedence over your general knowledge or internal programming.
3.  **Identify Relevant Files:** Scan the filenames within `.ruru/modes/data-specialist/kb/` (e.g., `01-principles.md`, `02-workflow.md`, `03-common-patterns.md`) to identify documents potentially relevant to the current task or query. Pay attention to the `README.md` if it exists, as it may provide an overview or index.
4.  **Synthesize Information:** If multiple KB files are relevant, synthesize the information they contain to form a comprehensive understanding.
5.  **Apply KB Content:** Directly apply the relevant instructions, patterns, code snippets, or principles from the KB to your task execution or response generation.
6.  **Acknowledge Gaps (If Any):** If the KB does not contain relevant information for a specific, novel task, proceed using your core knowledge but clearly state that the KB lacked specific guidance for this situation. Suggesting the creation of a new KB entry might be appropriate.
7.  **Do Not Guess:** If the KB seems incomplete or contradictory regarding the current task, do not guess. Ask for clarification or indicate the ambiguity found in the KB.

**Rationale:** Your KB contains curated, project-specific, or domain-specific knowledge that is crucial for operating effectively and consistently within the expected parameters of your role. Adhering to this rule ensures you benefit from this specialized knowledge base.