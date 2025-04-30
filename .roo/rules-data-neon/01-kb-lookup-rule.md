+++
id = "data-neon-kb-lookup"
title = "KB Lookup Rule for data-neon"
context_type = "rules"
scope = "Mode-specific knowledge base guidance"
target_audience = ["data-neon"]
granularity = "ruleset"
status = "active"
last_updated = "2025-04-19" # Assuming today's date
# version = ""
# related_context = []
tags = ["kb-lookup", "knowledge-base", "data-neon"]
# relevance = ""
target_mode_slug = "data-neon"
kb_directory = ".ruru/modes/data-neon/kb/"
+++

# Knowledge Base Consultation Rule

**Objective:** Ensure you leverage the specialized knowledge contained within your designated Knowledge Base (KB) directory before proceeding with tasks.

**Rule:**

1.  **Identify Need:** Before generating a response or taking significant action, determine if the task could benefit from specific domain knowledge, best practices, examples, or constraints relevant to your function (`data-neon`).
2.  **Consult KB:** If specialized knowledge is potentially required, **you MUST first consult the contents of your designated Knowledge Base directory:** `.ruru/modes/data-neon/kb/`.
    *   Review the `README.md` file within the KB directory for an overview of its contents.
    *   Examine relevant files within the KB directory based on the task requirements.
3.  **Apply Knowledge:** Integrate any relevant information, guidelines, code snippets, or constraints found in the KB into your response generation or action plan.
4.  **Proceed:** If the KB does not contain relevant information for the specific task, proceed using your general knowledge and capabilities.
5.  **State Assumption (If KB Empty/Not Consulted):** If you determine KB consultation is unnecessary for a task, or if the KB is empty, explicitly state this assumption in your reasoning (e.g., "Consulted KB, found no specific guidance for this task," or "KB consultation deemed unnecessary for this request.").

**Rationale:** Your KB contains curated information critical to performing your role effectively, ensuring consistency, and adhering to specific project standards or domain practices related to Neon DB. Consulting it first prevents errors and improves the quality of your output.