+++
id = "KB-LOOKUP-AGENT-CONTEXT-CONDENSER"
title = "KB Lookup Rule: Agent Context Condenser"
context_type = "rules"
scope = "Mode-specific rule for KB consultation"
target_audience = ["agent-context-condenser"]
granularity = "ruleset"
status = "active"
last_updated = "2025-04-18"
# version = ""
# related_context = []
tags = ["kb-lookup", "agent-context-condenser", "rule"]
# relevance = ""
target_mode_slug = "agent-context-condenser"
kb_directory = ".ruru/modes/agent-context-condenser/kb"
+++

# Rule: Consult Knowledge Base

Before proceeding with the task, review the contents of your Knowledge Base (KB) located in your mode's source directory (`.ruru/modes/agent-context-condenser/kb/`).
Assess if any documents within the KB are relevant to the current task.
If relevant documents are found, incorporate their information into your response or actions.
If no relevant documents are found, proceed with the task using your general knowledge.