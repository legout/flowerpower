+++
id = "framework-frappe-kb-lookup"
title = "KB Lookup Rule for framework-frappe"
context_type = "rules"
scope = "Mode-specific knowledge base access"
target_audience = ["framework-frappe"]
granularity = "ruleset"
status = "active"
last_updated = "2025-04-19"
tags = ["kb-lookup", "framework-frappe", "rules"]
target_mode_slug = "framework-frappe"
kb_directory = ".modes/framework-frappe/kb/"
+++

# Knowledge Base (KB) Lookup Rule

**Objective:** Ensure the mode leverages its dedicated knowledge base for relevant information, best practices, and specific instructions.

**Rule:**

1.  **Consult KB First:** Before attempting a task or answering a query related to your domain (`framework-frappe`), **ALWAYS** first consult the contents of your dedicated Knowledge Base (KB) directory: `.modes/framework-frappe/kb/`.
2.  **Prioritize KB:** Information found within your KB should be considered authoritative and prioritized over general knowledge.
3.  **Search Systematically:** Review the `README.md` in the KB directory first (if it exists) for an overview. Then, examine relevant files based on their names.
4.  **Apply Knowledge:** Integrate the information, guidelines, code snippets, or procedures found in the KB into your response or task execution.
5.  **Indicate Usage (Optional but Recommended):** Briefly mention if your response is based on information from your KB (e.g., "Based on the guidelines in my KB...").
6.  **If KB is Empty/Insufficient:** If the KB does not contain relevant information for the specific task, proceed using your general knowledge and capabilities, but note the absence of specific guidance from the KB if relevant.

**Rationale:** This ensures the mode utilizes specialized, curated knowledge for its domain, leading to more accurate, consistent, and context-aware responses and actions. It allows for targeted updates and maintenance of the mode's expertise.