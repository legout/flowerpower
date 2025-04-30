+++
id = "design-one-shot-kb-lookup"
title = "KB Lookup Rule for design-one-shot"
context_type = "rules"
scope = "Knowledge Base Consultation"
target_audience = ["design-one-shot"]
target_mode_slug = "design-one-shot"
kb_directory = ".ruru/modes/design-one-shot/kb/"
granularity = "ruleset"
status = "active"
last_updated = "2025-04-19" # Assuming today's date
# version = ""
# related_context = []
tags = ["kb", "knowledge-base", "lookup", "design-one-shot", "rules"]
# relevance = "High relevance for mode operation"
+++

# Knowledge Base Lookup Rule

**Objective:** Ensure the AI mode consults its dedicated Knowledge Base (KB) directory for relevant information, guidelines, and examples before proceeding with tasks.

**Rule:**

1.  **Identify KB Directory:** Your dedicated Knowledge Base directory is located at: `.ruru/modes/design-one-shot/kb/`.
2.  **Consult KB First:** Before generating a response or taking significant action related to your core function, **ALWAYS** first consult the contents of your KB directory (`.ruru/modes/design-one-shot/kb/`).
3.  **Prioritize KB Content:** Information, instructions, examples, or constraints found within your KB take precedence over general knowledge or previously learned patterns.
4.  **Apply KB Learnings:** Integrate the relevant findings from the KB into your reasoning and response generation. If the KB provides specific instructions or constraints, adhere to them strictly.
5.  **Acknowledge Empty KB:** If the KB directory is empty or contains no relevant information for the current task, proceed based on your general knowledge and the user's request, but acknowledge that the KB was consulted and found empty or non-applicable in your internal thought process.