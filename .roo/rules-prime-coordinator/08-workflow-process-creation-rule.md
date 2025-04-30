+++
id = "PRIME-RULE-DOC-CREATION-SIMPLE-V1"
title = "Prime Coordinator: Rule - Workflow & Process Creation Trigger"
context_type = "rules"
scope = "Triggering creation of new Workflow or Process (SOP) documents"
target_audience = ["prime"]
granularity = "guideline"
status = "active"
last_updated = "2025-04-22"
tags = ["rules", "workflow", "process", "sop", "creation", "documentation", "prime"]
related_context = [
    "01-operational-principles.md",
    # Pointing to Commander's KB for the detailed procedure
    ".ruru/modes/roo-commander/kb/08-workflow-process-creation-rule.md",
    ".ruru/templates/workflows/00_workflow_boilerplate.md",
    ".ruru/templates/toml-md/15_sop.md",
    ".ruru/workflows/",
    ".ruru/processes/"
    ]
template_schema_doc = ".ruru/templates/toml-md/16_ai_rule.README.md"
relevance = "Medium: Standardizes creation of reusable procedures"
+++

# Rule: Workflow & Process Creation Trigger

1.  **Identify Need:** If a user requests the creation of a new standard Workflow (`.ruru/workflows/`) or Process/SOP (`.ruru/processes/`), or if analysis suggests one is needed.
2.  **Procedure:** Consult the detailed procedure documented in the **Roo Commander Knowledge Base**: **`.ruru/modes/roo-commander/kb/08-workflow-process-creation-rule.md`**. This KB document outlines the steps for selecting templates, drafting, optional review (using `util-second-opinion`), validation (PAL), final storage, and index file updates (delegated to `prime-txt`).