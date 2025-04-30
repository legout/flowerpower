+++
id = "data-mongo-kb-lookup"
title = "KB Lookup Rule for data-mongo"
context_type = "rules"
scope = "Mode-specific rule for data-mongo" # Inferred scope
target_audience = ["data-mongo"] # Inferred target
granularity = "ruleset"
status = "active"
last_updated = "2025-04-19" # Using current date
# version = ""
# related_context = []
tags = ["kb-lookup", "data-mongo", "mongodb"] # Added relevant tags
# relevance = ""
target_mode_slug = "data-mongo"
kb_directory = ".ruru/modes/data-mongo/kb/"
+++

# Knowledge Base (KB) Lookup Rule

**Objective:** Ensure you leverage the specialized knowledge contained within your designated Knowledge Base (KB) directory before proceeding with tasks.

**Rule:**

1.  **Identify KB Directory:** Your primary KB directory is located at: `.ruru/modes/data-mongo/kb/`.
2.  **Consult KB First:** Before generating responses, executing complex actions, or making significant decisions related to `data-mongo`, **ALWAYS** first consult the contents of your KB directory (`.ruru/modes/data-mongo/kb/`).
3.  **Prioritize KB:** Treat the information within your KB as the primary source of truth and guidance for your specific domain. It contains curated best practices, patterns, constraints, and examples relevant to your function.
4.  **Apply Knowledge:** Integrate the knowledge gleaned from the KB into your reasoning, planning, and execution steps. Reference specific KB documents if applicable when explaining your approach.
5.  **Proceed if KB is Empty/Irrelevant:** If the KB is empty, or if after careful review, the KB content does not apply to the current specific task, proceed using your general knowledge and the provided context, but explicitly state that the KB was consulted and found not applicable.