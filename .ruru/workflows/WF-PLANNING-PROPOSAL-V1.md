+++
# --- Basic Metadata ---
id = "WF-PLANNING-PROPOSAL-V1"
title = "Workflow: Planning Proposal Creation"
status = "draft"      # << draft, active, deprecated, under-review >>
created_date = "2025-04-27"     # << YYYY-MM-DD >>
updated_date = "2025-04-27"     # << YYYY-MM-DD >>
version = "1.0"       # << Workflow document version >>
tags = ["workflow", "planning", "proposal", "documentation", "refinement"] # << Keywords >>

# --- Ownership & Context ---
owner = "prime-coordinator" # Or relevant Lead Agent
related_docs = [".roo/rules/01-standard-toml-md-format.md"]     # << Paths/URLs to essential specs, guides, PAL doc >>
related_templates = [] # << Paths to data templates used/produced >>

# --- Workflow Specific Fields ---
objective = "To define a structured process for capturing, refining, and documenting planning proposals based on user input." # << REQUIRED: Goal of this workflow >>
scope = "Applies to the creation of planning proposals initiated by a user, involving input capture, interactive refinement, whitepaper generation, and implementation document creation within the .ruru/planning/ directory structure."     # << REQUIRED: Applicability and boundaries >>
roles = ["prime-coordinator", "ask", "core-architect", "technical-writer", "project-manager"]     # << REQUIRED: List agent roles involved >>
trigger = "User request to initiate a planning proposal, providing initial text, files, or both."   # << How is this workflow typically initiated? >>
success_criteria = [
    "Proposal directory created at `.ruru/planning/[ProposalName]/`.",
    "Initial user input saved within the `input/` subdirectory.",
    "Proposal idea refined through interactive questioning.",
    "Refinement notes/summary saved.",
    "Detailed whitepaper (`[ProposalName]_Whitepaper.md`) generated and saved.",
    "Associated implementation documents (e.g., `Implementation_Plan.md`, `Concerns_Analysis.md`) generated and saved."
    ] # << Measurable conditions for successful completion >>
failure_criteria = [
    "Inability to create required directories or save initial files.",
    "User abandons or is unresponsive during the refinement process.",
    "Failure to generate the required whitepaper or implementation documents.",
    "Generated documents do not accurately reflect the refined proposal."
    ] # << Conditions indicating workflow failure >>

# --- Integration ---
acqa_applicable = false # Does the ACQA process apply to steps in this workflow?
pal_validated = false # Has this workflow been validated using PAL?
validation_notes = "" # Link to PAL validation records/notes

# --- AI Interaction Hints (Optional) ---
context_type = "workflow_definition"
+++

# Workflow: Planning Proposal Creation

## 1. Objective 🎯
*   To define a structured process for capturing, refining, and documenting planning proposals based on user input.

## 2. Scope ↔️
*   Applies to the creation of planning proposals initiated by a user, involving input capture, interactive refinement, whitepaper generation, and implementation document creation within the `.ruru/planning/` directory structure.

## 3. Roles & Responsibilities 👤
*   **`prime-coordinator`**: Initiates the workflow, manages file/directory creation, orchestrates delegation to specialist modes, ensures all steps are completed.
*   **`ask` / `core-architect`**: Interactively refines the proposal idea with the user, clarifies requirements, identifies potential issues or improvements.
*   **`technical-writer`**: Generates the formal whitepaper based on the refined proposal details.
*   **`project-manager` / `core-architect`**: Generates implementation-focused documents (plans, concerns, etc.) based on the refined proposal.

## 4. Preconditions🚦
*   User provides an initial request to create a planning proposal.
*   User provides initial input in the form of text, file paths, or both.
*   `prime-coordinator` has the necessary context about the user's request.

## 5. Reference Documents & Tools 📚🛠️
*   Rules: `.roo/rules/01-standard-toml-md-format.md`
*   Tools: `write_to_file`, `ask_followup_question`, `new_task`, `read_file`, `list_files` (potentially for verifying input file paths).

## 6. Workflow Steps 🪜

*   **Step 1: Initiation & Input Capture (Coordinator Task)**
    *   **Description:** Receive the user's request and initial input. Determine a suitable, filesystem-safe name for the proposal (`[ProposalName]`). Create the necessary directory structure and save the initial input.
    *   **Inputs:** User request, initial text/file paths.
    *   **Procedure:**
        1.  Analyze the user input to derive a concise `[ProposalName]` (e.g., "Feature_UserAuth", "Refactor_DatabaseSchema"). Sanitize the name for filesystem compatibility.
        2.  Define the base path: `proposal_base_path = ".ruru/planning/[ProposalName]"`
        3.  Define the input path: `input_path = proposal_base_path + "/input"`
        4.  Use `write_to_file` (or potentially `execute_command` with `mkdir -p`) to ensure `input_path` exists. *Confirmation required before write.*
        5.  If text input is provided, save it to a file like `input_path/initial_request.md` using `write_to_file`. *Confirmation required.*
        6.  If file paths are provided:
            *   *(Optional)* Verify file existence using `list_files` or `read_file` on the provided paths.
            *   Copy the input files into the `input_path` directory. This might require coordination with the user or using file system tools if direct copying isn't possible via standard tools (consider `execute_command` with `cp` if necessary and OS-aware).
    *   **Outputs:** Created directory structure `.ruru/planning/[ProposalName]/input/`, saved initial input files.
    *   **Error Handling:** If directory creation fails, report error. If input files cannot be accessed/copied, inform the user and potentially ask for clarification or alternative input methods.

*   **Step 2: Proposal Refinement (Coordinator delegates to `ask` or `core-architect`)**
    *   **Description:** Interactively refine the initial proposal idea with the user to clarify goals, scope, requirements, and potential challenges.
    *   **Tool:** `new_task`
    *   **Inputs Provided by Coordinator:**
        *   Path to the proposal directory: `proposal_base_path`.
        *   Path to the input files/text: `input_path`.
        *   Summary of the initial proposal idea.
    *   **Instructions for Delegate (`ask` / `core-architect`):**
        *   "Review the initial proposal input located at `[input_path]`."
        *   "Engage the user in a dialogue using `ask_followup_question` to refine the proposal. Focus on clarifying: goals, scope, key features/requirements, potential challenges, success metrics, non-goals."
        *   "Summarize the refined proposal, including key decisions and clarifications."
        *   "Save the summary and key discussion points to a file named `Refinement_Notes.md` within the `[proposal_base_path]` directory using `write_to_file`." *Confirmation required before write.*
        *   "Report completion, providing the path to the `Refinement_Notes.md` file."
    *   **Expected Output from Delegate:** Confirmation of completion, path to `Refinement_Notes.md`.
    *   **Coordinator Action (Post-Delegation):** Await confirmation. Verify the `Refinement_Notes.md` file exists. Log completion of refinement. Proceed to Step 3.
    *   **Error Handling:** If the delegate fails or the user is unresponsive, log the issue and potentially pause the workflow, informing the user.

*   **Step 3: Whitepaper Generation (Coordinator delegates to `technical-writer`)**
    *   **Description:** Generate a formal whitepaper summarizing the refined proposal.
    *   **Tool:** `new_task`
    *   **Inputs Provided by Coordinator:**
        *   Path to the proposal directory: `proposal_base_path`.
        *   Path to the `Refinement_Notes.md` file.
        *   Path to the initial input files (`input_path`) for context.
        *   Proposal Name (`[ProposalName]`).
    *   **Instructions for Delegate (`technical-writer`):**
        *   "Read the `Refinement_Notes.md` and initial input files located within `[proposal_base_path]`."
        *   "Generate a comprehensive whitepaper document summarizing the refined proposal. Structure it logically (e.g., Introduction, Problem Statement, Proposed Solution, Scope, Key Features, Potential Benefits, Conclusion)."
        *   "Save the whitepaper as `[proposal_base_path]/[ProposalName]_Whitepaper.md` using `write_to_file`." *Confirmation required before write.*
        *   "Ensure the content adheres to standard documentation practices and uses TOML+MD format if appropriate (though likely just Markdown body needed here unless a specific template is required)."
        *   "Report completion, providing the path to the whitepaper file."
    *   **Expected Output from Delegate:** Confirmation of completion, path to `[ProposalName]_Whitepaper.md`.
    *   **Coordinator Action (Post-Delegation):** Await confirmation. Verify the whitepaper file exists. Log completion. Proceed to Step 4.
    *   **Error Handling:** If the delegate fails, log the error, potentially retry or assign to a different writer/mode.

*   **Step 4: Implementation Document Generation (Coordinator delegates to `project-manager` or `core-architect`)**
    *   **Description:** Generate documents related to the practical implementation of the proposal.
    *   **Tool:** `new_task`
    *   **Inputs Provided by Coordinator:**
        *   Path to the proposal directory: `proposal_base_path`.
        *   Path to the `Refinement_Notes.md` file.
        *   Path to the `[ProposalName]_Whitepaper.md` file.
    *   **Instructions for Delegate (`project-manager` / `core-architect`):**
        *   "Review the refined proposal details in `Refinement_Notes.md` and `[ProposalName]_Whitepaper.md` located at `[proposal_base_path]`."
        *   "Generate relevant implementation documents. Examples include:"
            *   `Implementation_Plan.md`: High-level steps, potential phases, resource considerations.
            *   `Concerns_Analysis.md`: Potential risks, challenges, open questions, mitigation ideas.
            *   `Improvements_Suggestions.md`: Ideas for future enhancements beyond the core proposal.
        *   "Create these documents as separate Markdown files within the `[proposal_base_path]` directory using `write_to_file`." *Confirmation required before each write.*
        *   "Focus on actionable insights relevant to planning and execution."
        *   "Report completion, providing the paths to all created implementation documents."
    *   **Expected Output from Delegate:** Confirmation of completion, list of paths to created implementation documents.
    *   **Coordinator Action (Post-Delegation):** Await confirmation. Verify the implementation documents exist. Log completion. Proceed to Step 5.
    *   **Error Handling:** If the delegate fails, log the error, potentially retry or assign to a different mode.

*   **Step 5: Completion (Coordinator Task)**
    *   **Description:** Verify all artifacts have been created and finalize the workflow.
    *   **Inputs:** Confirmation and file paths from previous steps.
    *   **Procedure:**
        1.  Verify the existence of:
            *   `.ruru/planning/[ProposalName]/input/` (with initial files)
            *   `.ruru/planning/[ProposalName]/Refinement_Notes.md`
            *   `.ruru/planning/[ProposalName]/[ProposalName]_Whitepaper.md`
            *   `.ruru/planning/[ProposalName]/Implementation_Plan.md` (and others created in Step 4)
        2.  Log the successful completion of the planning proposal workflow, referencing the `proposal_base_path`.
        3.  Inform the user that the planning proposal process is complete and provide the path to the main proposal directory.
    *   **Outputs:** Final confirmation to the user, logged completion status.
    *   **Error Handling:** If verification fails, attempt to re-run the relevant failed step or report the inconsistency.

## 7. Postconditions ✅
*   The directory `.ruru/planning/[ProposalName]/` exists.
*   The `input/` subdirectory contains the initial user-provided materials.
*   `Refinement_Notes.md` exists, capturing the interactive refinement process.
*   `[ProposalName]_Whitepaper.md` exists, providing a formal summary.
*   Implementation-related documents (e.g., `Implementation_Plan.md`, `Concerns_Analysis.md`) exist.
*   The workflow completion is logged.

## 8. Error Handling & Escalation (Overall) ⚠️
*   Individual steps include specific error handling.
*   If a delegated task fails repeatedly, the `prime-coordinator` should log the failure, potentially try an alternative delegate if appropriate, or escalate to the user for clarification or manual intervention.
*   Persistent file system errors should be reported clearly.
*   Reference the Adaptive Failure Resolution process (`.ruru/processes/afr-process.md`) if applicable.

## 9. PAL Validation Record 🧪
*   Date Validated: TBD
*   Method: TBD
*   Test Case(s): TBD
*   Findings/Refinements: TBD

## 10. Revision History 📜
*   v1.0 (2025-04-27): Initial draft based on user request.