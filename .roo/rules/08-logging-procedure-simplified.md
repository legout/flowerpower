+++
id = "RULE-LOGGING-PROCEDURE-SIMPLE-V1"
title = "Standard: Logging Requirement"
context_type = "rules"
scope = "Requirement to log significant events and decisions"
target_audience = ["all"] # Especially Coordinators and Leads
granularity = "guideline"
status = "active"
last_updated = "2025-04-22"
tags = ["rules", "logging", "auditing", "traceability", "mdtm"]
related_context = [
    ".roo/rules/04-mdtm-workflow-initiation.md",
    ".ruru/modes/roo-commander/kb/12-logging-procedures.md" # Link to detailed KB
    ]
template_schema_doc = ".ruru/templates/toml-md/16_ai_rule.README.md"
relevance = "High: Essential for traceability and state management"
+++

# Standard: Logging Requirement

**Objective:** Ensure a traceable record of actions, decisions, and task progress.

**Rule:**

1.  **Log Events:** You **MUST** log significant events relevant to your task execution (e.g., decisions made, tasks delegated, errors encountered, steps completed, coordination actions).
2.  **Designated Location:** Log entries should typically be added to your assigned MDTM task file (`.ruru/tasks/TASK-...`), your coordination log file, or other designated artifact locations (e.g., ADRs in `.ruru/decisions/`).
3.  **Tooling Details:** For detailed guidance on *which tools* (`write_to_file`, `append_to_file`, `insert_content`, `apply_diff`) to use for specific logging scenarios and locations, consult the Roo Commander Knowledge Base document: **`.ruru/modes/roo-commander/kb/12-logging-procedures.md`**.