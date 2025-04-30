+++
id = "ROO-CMD-RULE-KB-LOOKUP-V2" # Updated ID
title = "Roo Commander: Rule - KB Lookup Trigger"
context_type = "rules"
scope = "Mode-specific knowledge base access conditions"
target_audience = ["roo-commander"]
granularity = "procedure"
status = "active"
last_updated = "2025-04-21" # Assuming today's date
tags = ["rules", "kb-lookup", "knowledge-base", "context", "reference", "roo-commander"]
related_context = [
    ".ruru/modes/roo-commander/kb/",
    ".ruru/modes/roo-commander/kb/README.md",
    # Links to rules that might *trigger* a KB lookup
    "01-operational-principles.md",
    "03-delegation-procedure-rule.md",
    "05-error-handling-rule.md",
    "06-documentation-adr-rule.md",
    "08-workflow-process-creation-rule.md"
    ]
+++

# Rule: KB Lookup Trigger

This rule defines the specific situations when you **MUST** consult the detailed Knowledge Base (KB) located in `.ruru/modes/roo-commander/kb/`. In most common operational scenarios, the procedures defined in rules `02` through `12` should be sufficient.

**Consult the KB When:**

1.  **Explicitly Directed:** Another rule explicitly references a specific KB document for detailed steps or information (e.g., "consult KB `04-delegation-mdtm.md` for detailed steps").
2.  **Novel/Complex Procedures:** You encounter a task requiring a detailed procedure that is *not* adequately covered by the standard operational rules (`02` through `12`). Examples include:
    *   Executing the detailed steps within the MDTM workflow (delegation rule points here).
    *   Handling complex or unusual error scenarios (error handling rule points here).
    *   Following detailed safety protocols beyond basic checks (safety rule points here).
    *   Understanding the nuanced use of logging tools (`write_to_file` vs `append` vs `insert`) for specific log types (logging rule points here).
3.  **Reference Lookups:** You need to access large reference lists or detailed indices, such as:
    *   The full summary of available modes (`kb-available-modes-summary.md`).
    *   The index of standard processes (`10-standard-processes-index.md`).
    *   The index of standard workflows (`11-standard-workflows-index.md`).

**Procedure for KB Lookup:**

1.  **Identify Target Document:** Determine the specific KB document needed based on the directing rule or the nature of the complex/novel task. Use the KB README (`.ruru/modes/roo-commander/kb/README.md`) for guidance if the specific file isn't immediately known.
2.  **Use `read_file`:** Access the content of the target KB document.
3.  **Apply Information:** Integrate the detailed steps, guidelines, or reference information into your current task execution.

**Key Objective:** To ensure detailed, complex, or reference-heavy procedures are accessed from the KB when required, without cluttering the core operational rules or requiring unnecessary lookups for common actions.