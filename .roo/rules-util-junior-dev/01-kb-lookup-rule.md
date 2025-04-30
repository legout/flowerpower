+++
id = "util-junior-dev-kb-lookup"
title = "KB Lookup Rule for util-junior-dev"
context_type = "rules"
scope = "Mode-specific knowledge base access"
target_audience = ["util-junior-dev"]
granularity = "rule"
status = "active"
last_updated = "2025-04-19" # Using date from environment_details
# version = "1.0"
# related_context = []
tags = ["kb", "knowledge-base", "lookup", "util-junior-dev"]
# relevance = "High"
target_mode_slug = "util-junior-dev"
kb_directory = ".modes/util-junior-dev/kb/"
+++

# Knowledge Base Lookup Rule

**Objective:** Ensure the `util-junior-dev` mode leverages its dedicated Knowledge Base (KB) for relevant information, guidelines, and best practices before proceeding with tasks.

**Rule:**

1.  **Consult KB First:** Before starting any significant task or answering complex questions, **ALWAYS** consult the contents of your dedicated Knowledge Base directory: `.modes/util-junior-dev/kb/`.
2.  **Identify Relevant Documents:** Look for documents within the KB that relate to the current task (e.g., coding standards, common patterns, debugging tips, tool usage). The `README.md` file in the KB directory may provide an overview of available documents.
3.  **Apply Knowledge:** Integrate the information and guidelines found in the KB into your analysis, planning, and execution.
4.  **If KB is Empty/Insufficient:** If the KB directory is empty or does not contain relevant information for the specific task, proceed using your general knowledge and capabilities, but note the potential knowledge gap.