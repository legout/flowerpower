+++
id = "ROO-CMD-RULE-DOC-ADR-SIMPLE-V1"
title = "Roo Commander: Rule - Documentation & ADR Trigger (Simplified)"
context_type = "rules"
scope = "Triggering ADR creation and overseeing documentation"
target_audience = ["roo-commander"]
granularity = "guideline"
status = "active"
last_updated = "2025-04-22"
tags = ["rules", "documentation", "adr", "logging", "decision-record", "roo-commander"]
related_context = [
    "01-operational-principles.md",
    "08-logging-procedure-simplified.md", # Reference the simplified logging rule
    ".ruru/modes/roo-commander/kb/06-documentation-logging.md", # Detailed ADR creation/doc mgmt in KB
    ".ruru/templates/toml-md/07_adr.md", # ADR Template
    ".ruru/decisions/" # Standard ADR location
    ]
template_schema_doc = ".ruru/templates/toml-md/16_ai_rule.README.md"
relevance = "High: Ensures important decisions are recorded"
+++

# Rule: Documentation & ADR Trigger (Simplified)

1.  **Documentation Oversight:** Oversee project documentation location and status. Prefer delegating creation/updates of stable docs (`.ruru/docs/`) to specialists (`util-writer`, `core-architect`). Handle planning docs (`.ruru/planning/`) directly if needed, preferring `apply_diff` for modifications. Consult KB `.ruru/modes/roo-commander/kb/06-documentation-logging.md` for detailed documentation management guidance.

2.  **ADR Trigger:** An Architecture Decision Record (ADR) **MUST** be created in `.ruru/decisions/` for any **significant** architectural, technological, or strategic decision (e.g., framework choice, major pattern adoption, core tech selection).

3.  **ADR Procedure:** To create an ADR, consult the Knowledge Base document **`.ruru/modes/roo-commander/kb/06-documentation-logging.md`** for the detailed procedure. This involves using the standard template (`.ruru/templates/toml-md/07_adr.md`), writing the content, and logging the creation (Rule `08`).