+++
id = "design-diagramer-kb-lookup"
title = "KB Lookup Rule for design-diagramer"
context_type = "rules"
scope = "Mode-specific knowledge base access"
target_audience = ["design-diagramer"]
granularity = "ruleset"
status = "active"
last_updated = ""
# version = ""
# related_context = []
tags = ["kb", "knowledge-base", "lookup", "design-diagramer"]
# relevance = ""
target_mode_slug = "design-diagramer"
kb_directory = ".ruru/modes/design-diagramer/kb/"
+++

# Knowledge Base Lookup Rule

Before responding to a user request, **ALWAYS** check the files within your dedicated Knowledge Base (KB) directory: `.ruru/modes/design-diagramer/kb/`.

This directory contains curated information, best practices, specific instructions, and examples relevant to your function as the `design-diagramer` mode.

**Prioritize information found in your KB over your general knowledge.**

Consult the KB to:
*   Understand specific conventions or standards for diagramming (e.g., Mermaid syntax preferences, style guides).
*   Find examples of previously generated diagrams.
*   Retrieve specific instructions or constraints related to the current project or task.
*   Learn about preferred tools or techniques.

Even if the KB directory `.ruru/modes/design-diagramer/kb/` appears empty or contains only a `README.md`, **always perform the check** as part of your standard operating procedure. This ensures you incorporate any newly added knowledge specific to your role.