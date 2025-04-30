+++
# --- Basic Metadata ---
id = "WF-BUILD-ROOMODES-001"
title = "Workflow: Update .roomodes using build_roomodes.js"
status = "active"
created_date = "2025-04-19"
updated_date = "2025-04-19"
version = "1.0"
tags = ["workflow", "sop", "modes", "build", "script", "node", "roomodes"]

# --- Ownership & Context ---
owner = "Roo Commander"
related_docs = [
  "build_roomodes.js",
  ".roomodes"
]
related_templates = [] # No specific data templates used/produced by the workflow itself

# --- Workflow Specific Fields ---
objective = "To regenerate the `.roomodes` file accurately based on the current mode definitions found in the `.ruru/modes/` directory using the `build_roomodes.js` script."
scope = "Applies whenever modes are added, removed, or have their core definition (slug, name, system_prompt) changed in their respective `.mode.md` files."
roles = ["Coordinator (Roo Commander)", "Executor (Terminal via `execute_command`)"]
trigger = "Manual initiation by the Coordinator after mode changes or when `.roomodes` is suspected to be out of sync."
success_criteria = [
  "The `build_roomodes.js` script executes successfully (exit code 0).",
  "The `.roomodes` file is updated with the latest mode information.",
  "The script output confirms the number of modes processed."
]
failure_criteria = [
  "The `build_roomodes.js` script fails to execute (non-zero exit code).",
  "The script reports errors during execution (e.g., file not found, parsing errors).",
  "The `.roomodes` file is not updated or contains incorrect data."
]

# --- Integration ---
acqa_applicable = false # This workflow executes a script, ACQA doesn't directly apply
pal_validated = true # Simple workflow, validated conceptually
validation_notes = "Workflow involves running a single script and checking output."

# --- AI Interaction Hints (Optional) ---
# context_type = "workflow_definition"
+++

# Workflow: Update .roomodes using build_roomodes.js

## 1. Objective 🎯
*   To regenerate the `.roomodes` file accurately based on the current mode definitions found in the `.ruru/modes/` directory using the `build_roomodes.js` script. This ensures the system has an up-to-date list of available custom modes.

## 2. Scope ↔️
*   Applies whenever modes are added, removed, or have their core definition (`id`, `name`, `system_prompt`) changed in their respective `.mode.md` files within the `.ruru/modes/` directory structure.

## 3. Roles & Responsibilities 👤
*   **Coordinator (Roo Commander):** Initiates the workflow, executes the script via `execute_command`, and verifies the outcome.
*   **Executor (Terminal):** Runs the Node.js script.

## 4. Preconditions🚦
*   The `build_roomodes.js` script must exist in the project root.
*   Node.js must be installed and accessible in the execution environment.
*   If the script relies on external libraries (like `@ltd/j-toml`), they should ideally be installed (`npm install`).

## 5. Reference Documents & Tools 📚🛠️
*   `build_roomodes.js`: The script to be executed.
*   `.ruru/modes/`: The directory containing the mode definitions.
*   `.roomodes`: The target output file.
*   `execute_command`: The tool used to run the script.
*   `read_file`: (Optional) Tool used by Coordinator to verify `.roomodes` content after execution.

## 6. Workflow Steps 🪜

*   **Step 1: Initiate Workflow (Coordinator Task)**
    *   **Description:** The Coordinator identifies the need to update `.roomodes` (e.g., after mode changes).
    *   **Inputs:** Knowledge of recent mode changes or suspicion of stale `.roomodes`.
    *   **Procedure:** Prepare to execute the build script.
    *   **Outputs:** Decision to run the script.

*   **Step 2: Execute Build Script (Coordinator delegates to Executor via `execute_command`)**
    *   **Description:** Run the Node.js script to scan modes and generate the `.roomodes` file.
    *   **Tool:** `execute_command`
    *   **Inputs Provided by Coordinator:** The command `node build_roomodes.js`.
    *   **Instructions for Executor:** Execute the provided Node.js command.
    *   **Expected Output from Executor:** Terminal output from the script, including success or error messages, and the exit code.
    *   **Coordinator Action (Post-Execution):** Review the script's output and exit code.
    *   **Validation/QA:** Check if the script reported success and the expected number of modes processed.
    *   **Error Handling:** If the exit code is non-zero or the output indicates errors, analyze the error messages. Potential issues include missing Node.js, missing script file, file system permission errors, or errors within the script logic (e.g., parsing failures not caught gracefully). Report failure to the user or attempt troubleshooting (e.g., checking script content, checking file permissions).

*   **Step 3: Verify Output (Optional - Coordinator Task)**
    *   **Description:** The Coordinator can optionally read the updated `.roomodes` file to confirm its content looks correct and includes the expected modes.
    *   **Inputs:** Path to `.roomodes`.
    *   **Procedure:** Use `read_file` on `.roomodes`. Analyze the JSON structure and content.
    *   **Outputs:** Confirmation of correct file generation.
    *   **Error Handling:** If the file content is incorrect, report the discrepancy. Consider re-running the script or debugging `build_roomodes.js`.

## 7. Postconditions ✅
*   The `.roomodes` file accurately reflects the `slug`, `name`, and `roleDefinition` of all valid modes found in the `.ruru/modes` directory.
*   The script execution completed successfully (exit code 0).

## 8. Error Handling & Escalation (Overall) ⚠️
*   If the script fails repeatedly, review the script logic (`build_roomodes.js`) for bugs.
*   Check Node.js installation and necessary permissions.
*   If TOML parsing errors occur frequently despite having a library installed, investigate the format of the `.mode.md` files causing issues.
*   Escalate to the user if the issue cannot be resolved.

## 9. PAL Validation Record 🧪
*   Date Validated: 2025-04-19
*   Method: Conceptual Review & Successful Execution.
*   Test Case(s): Execution after creating the script and installing the dependency.
*   Findings/Refinements: Workflow is straightforward. Added check for Node.js as a precondition.

## 10. Revision History 📜
*   v1.0 (2025-04-19): Initial draft based on the creation and execution of `build_roomodes.js`.