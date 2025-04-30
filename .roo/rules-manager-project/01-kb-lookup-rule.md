+++
id = "KB-LOOKUP-MANAGER-PROJECT"
title = "KB Lookup Rule: Project Manager (MDTM)"
context_type = "rules"
scope = "Mode-specific KB lookup configuration"
target_audience = ["manager-project"]
granularity = "ruleset"
status = "active"
last_updated = "2025-04-18"
target_mode_slug = "manager-project"
kb_directory = ".ruru/modes/manager-project/kb"
# version = ""
# related_context = []
tags = ["kb-lookup", "project-manager"]
# relevance = ""
+++

# Knowledge Base Lookup Rule

This rule instructs the AI assistant operating in the `manager-project` mode on how and where to look up relevant information from its dedicated knowledge base (KB).

## Rule Details

*   **Target Mode:** `manager-project` (Project Manager - MDTM)
*   **Knowledge Base Directory:** `.ruru/modes/manager-project/kb`
*   **Lookup Trigger:** When the assistant needs specific procedural information, best practices, templates, or historical context related to MDTM project management tasks within this workspace.
*   **Lookup Strategy:** Search the specified `kb_directory` for Markdown files (`.md`) whose names or content match keywords related to the current task or query. Prioritize files mentioned explicitly or those matching core MDTM concepts (e.g., "task creation", "status update", "reporting", "MDTM template").
*   **Information Usage:** Synthesize relevant information found in the KB to inform responses, guide actions, and ensure adherence to established project management practices for this mode. Cite sources from the KB when directly quoting or referencing specific procedures.
*   **Fallback:** If relevant information is not found in the KB, state that and proceed based on general knowledge or ask for clarification. Do not invent procedures not documented in the KB.