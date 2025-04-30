+++
# --- Basic Metadata ---
id = ""               # << WORKFLOW-SCOPE-NNN >>
title = ""            # << Human-readable title of the Workflow/SOP >>
status = "draft"      # << draft, active, deprecated, under-review >>
created_date = ""     # << YYYY-MM-DD >>
updated_date = ""     # << YYYY-MM-DD >>
version = "1.0"       # << Workflow document version >>
tags = ["workflow", "sop"] # << Keywords >>

# --- Ownership & Context ---
owner = "Roo Commander" # Or relevant Lead Agent
related_docs = []     # << Paths/URLs to essential specs, guides, PAL doc >>
related_templates = [] # << Paths to data templates used/produced >>

# --- Workflow Specific Fields ---
objective = "" # << REQUIRED: Goal of this workflow >>
scope = ""     # << REQUIRED: Applicability and boundaries >>
roles = []     # << REQUIRED: List agent roles involved >>
trigger = ""   # << How is this workflow typically initiated? >>
success_criteria = [] # << Measurable conditions for successful completion >>
failure_criteria = [] # << Conditions indicating workflow failure >>

# --- Integration ---
acqa_applicable = true # Does the ACQA process apply to steps in this workflow?
pal_validated = false # Has this workflow been validated using PAL?
validation_notes = "" # Link to PAL validation records/notes

# --- AI Interaction Hints (Optional) ---
# context_type = "workflow_definition"
+++

# << WORKFLOW_TITLE >>

## 1. Objective 🎯
*   << REQUIRED: Goal >>

## 2. Scope ↔️
*   << REQUIRED: Applicability / Boundaries >>

## 3. Roles & Responsibilities 👤
*   << REQUIRED: List roles from TOML and detail responsibilities *within this workflow* >>

## 4. Preconditions🚦
*   What state/data/artifacts must exist before starting this workflow?
*   What context must the initiating agent (usually Coordinator) possess?

## 5. Reference Documents & Tools 📚🛠️
*   List essential specifications, guides, rules (`.roo/rules/`).
*   List key tools expected to be used (`read_file`, `apply_diff`, `new_task`, specific MCP tools, etc.).

## 6. Workflow Steps 🪜

*   Provide step-by-step details. Clearly distinguish between Coordinator actions and Delegated tasks. Use sub-numbering for clarity within steps.
*   **Example Structure for Steps:**

    *   **Step X: [Action Name] (Coordinator Task)**
        *   **Description:** What the Coordinator does in this step (e.g., analyze inputs, verify paths, prepare context).
        *   **Inputs:** Data/files needed by the Coordinator.
        *   **Procedure:** Coordinator's actions (e.g., use `list_files`, `read_file`).
        *   **Outputs:** Information gathered or state prepared for the next step/delegation.
        *   **Error Handling:** How the Coordinator handles errors in this step.
        *   **Decision Point:** If [condition], go to Step Y, else go to Step Z.

    *   **Step Y: [Action Name] (Coordinator delegates to [Delegate Role])**
        *   **Description:** The overall goal of the delegated task.
        *   **Tool:** `new_task`
        *   **Inputs Provided by Coordinator:** List the specific data, file paths, template content, context summaries, or specifications the Coordinator MUST provide to the delegate.
        *   **Instructions for Delegate:** Provide the clear, actionable instructions for the delegate agent, including:
            *   Specific actions to perform.
            *   Tools the delegate should use (`read_file`, `write_to_file`, `apply_diff`, etc.).
            *   References to relevant specs/rules.
            *   Expected format/structure of the output.
            *   Requirement to report completion (and potentially Confidence Score per ACQA).
        *   **Expected Output from Delegate:** What the Coordinator expects back (e.g., confirmation, created file paths, analysis summary, list of errors).
        *   **Coordinator Action (Post-Delegation):** What the Coordinator does upon receiving the delegate's response (e.g., Wait for confirmation, Handle errors reported by delegate, Analyze delegate output, Update Coordinator state, Proceed to next step).
        *   **Validation/QA:** Does ACQA apply to the delegate's output? If so, reference ACQA process execution here.
        *   **Error Handling:** How the Coordinator handles failure of the delegated task.

*   **Actual Workflow Steps:**

    *   **Step 1: [Action Name] (Responsible Role)**
    *   **Description:** Brief explanation of the step's purpose.
    *   **Inputs:** Specific data/files needed.
    *   **Context:** Critical context required (esp. for delegation).
    *   **Procedure:** Detailed actions, including tool usage. **Note:** For complex procedures within a step, consider defining them in a separate document in the `.ruru/processes/` directory and referencing that document here (e.g., "Execute ACQA Process as defined in `.ruru/processes/acqa-process.md`").
    *   **Outputs:** Expected artifacts/state changes.
    *   **Validation/QA:** How is this step's output checked? Does ACQA apply? Refer to specific QA steps if applicable.
    *   **Error Handling:** Specific actions if this step fails (e.g., retry, log error, escalate to Coordinator, invoke Adaptive Failure Resolution).
    *   **Decision Point:** If [condition], go to Step Y, else go to Step Z.

## 7. Postconditions ✅
*   What state/data/artifacts should exist after successful completion?
*   What constitutes successful completion (referencing `success_criteria`)?

## 8. Error Handling & Escalation (Overall) ⚠️
*   General error handling principles for the workflow.
*   Overall escalation path if steps fail repeatedly or unexpected situations arise.
*   Reference the Adaptive Failure Resolution process (`.ruru/processes/afr-process.md`).

## 9. PAL Validation Record 🧪
*   Date Validated:
*   Method: (e.g., Conceptual Review, Simulation)
*   Test Case(s):
*   Findings/Refinements:

## 10. Revision History 📜
*   v1.0 (YYYY-MM-DD): Initial draft.