+++
# --- Basic Metadata ---
id = "WORKFLOW-BATCH-BUILD-002"
title = "Create Multiple Specialized Roo Commander Builds (Batch)"
status = "draft"
created_date = "2025-04-27"
updated_date = "2025-04-27"
version = "1.0"
tags = ["workflow", "build", "modes", "customization", "batch", "roo-commander"]

# --- Ownership & Context ---
owner = "Roo Commander"
related_docs = [
    ".ruru/config/build_collections.json",
    ".ruru/workflows/WF-CREATE-ROO-CMD-BUILD-001.md", # Single build workflow
    "create_build.js" # Assumed build script
    ]
related_templates = []

# --- Workflow Specific Fields ---
objective = "Automate the generation of multiple, predefined Roo Commander builds, each containing a specific subset of modes defined in `build_collections.json`."
scope = "This workflow reads collection definitions, iterates through them, generates the necessary `.roomodes` file for each, executes the build script, and reports the overall status."
roles = ["roo-commander"]
trigger = "User request to perform a batch build of predefined mode collections."
success_criteria = [
    "Build script is executed for each defined collection in `build_collections.json`.",
    "A build artifact is successfully created for each collection.",
    "The overall process completes without critical errors."
    ]
failure_criteria = [
    "Cannot read or parse `build_collections.json`.",
    "Build script (`create_build.js`) fails for one or more collections.",
    "`.roomodes` file cannot be written for a collection."
    ]

# --- Integration ---
acqa_applicable = false
pal_validated = false
validation_notes = ""

# --- AI Interaction Hints (Optional) ---
# context_type = "workflow_definition"
+++

# Create Multiple Specialized Roo Commander Builds (Batch)

## 1. Objective 🎯
*   Automate the generation of multiple, predefined Roo Commander builds, each containing a specific subset of modes defined in `.ruru/config/build_collections.json`.

## 2. Scope ↔️
*   This workflow reads collection definitions from `.ruru/config/build_collections.json`, iterates through them, generates the necessary `.roomodes` file for each collection, executes the `create_build.js` script (passing collection-specific arguments if needed), and reports the overall status.

## 3. Roles & Responsibilities 👤
*   **Roo Commander:** Orchestrates the entire batch process, reads configuration, manages the loop, generates `.roomodes` files, executes the build script via `execute_command` for each collection, monitors results, and reports the final outcome.
*   **Build Script (`create_build.js`):** Performs the actual filtering and packaging for a single build based on the `.roomodes` file and potentially other arguments (like output directory/name).

## 4. Preconditions🚦
*   The configuration file `.ruru/config/build_collections.json` exists and contains valid JSON defining the collections.
*   The build script `create_build.js` exists, is functional, and can handle being run multiple times (potentially with arguments to differentiate outputs).
*   The full set of modes is available for filtering.

## 5. Reference Documents & Tools 📚🛠️
*   Config: `.ruru/config/build_collections.json`
*   Scripts: `create_build.js`
*   Tools: `read_file`, `write_to_file`, `execute_command`, `ask_followup_question` (for error handling).

## 6. Workflow Steps 🪜

*   **Step 1: Read Build Collections Config (Roo Commander Task)**
    *   **Description:** Load the predefined mode collections.
    *   **Inputs:** File path `.ruru/config/build_collections.json`.
    *   **Procedure:** Use `read_file` to get the content of the JSON configuration. Parse the JSON content.
    *   **Outputs:** Parsed object containing the collection definitions.
    *   **Error Handling:** If `read_file` fails or JSON parsing fails, report error to the user and terminate the workflow.

*   **Step 2: Resolve Core Modes (Roo Commander Task - Optional Optimization)**
    *   **Description:** If collections reference "core", resolve the list of core modes once.
    *   **Inputs:** Parsed collection data from Step 1.
    *   **Procedure:** Check if a "core" collection exists. If yes, store its list of modes.
    *   **Outputs:** List of core mode slugs (if applicable).

*   **Step 3: Iterate Through Collections (Roo Commander Loop)**
    *   **Description:** Loop through each collection name defined in the parsed configuration (e.g., "core", "fullstack_react_supabase", "full").
    *   **For each collection:** Perform Steps 4-6.

*   **Step 4: Prepare Mode List for Collection (Roo Commander Task)**
    *   **Description:** Determine the final list of mode slugs for the current collection.
    *   **Inputs:** Current collection name, parsed collection data, resolved core modes list (from Step 2).
    *   **Procedure:**
        *   Get the list associated with the current collection name.
        *   If the list contains "core", replace "core" with the actual list of core mode slugs resolved in Step 2.
        *   Handle the special "full" collection: If the collection name is "full" and its value is `["all"]`, note this special case for Step 5/6 (the build script might handle "all" directly, or it might require generating a `.roomodes` with all known modes, or skipping `.roomodes` generation). Clarify script behavior if needed.
    *   **Outputs:** Final list of mode slugs for the current collection (or indication of "full" build).

*   **Step 5: Generate `.roomodes` File for Collection (Roo Commander Task)**
    *   **Description:** Create the `.roomodes` file specific to the current collection.
    *   **Inputs:** Final mode list for the collection (from Step 4).
    *   **Procedure:**
        *   **Unless** it's the special "full" collection handled differently by the script:
            *   Format the list of slugs into a newline-separated string.
            *   Use `write_to_file` to create/overwrite the `.roomodes` file in the workspace root.
    *   **Outputs:** `.roomodes` file updated for the current collection (or skipped).
    *   **Error Handling:** If `write_to_file` fails, log the error for this collection, report it, and potentially ask the user whether to continue with other collections.

*   **Step 6: Execute Build Script for Collection (Roo Commander delegates to `execute_command`)**
    *   **Description:** Run the `create_build.js` script for the current collection.
    *   **Tool:** `execute_command`
    *   **Inputs Provided by Coordinator:** Command to run the script. **Crucially, the script might need arguments** to specify the collection name and/or a unique output directory/filename for this collection's build artifact (e.g., `node create_build.js --collection core --output ./builds/core`). This needs clarification based on `create_build.js` capabilities.
    *   **Instructions for Delegate (`execute_command`):**
        *   Command: `node create_build.js [ARGUMENTS]` (e.g., `node create_build.js --collection <collection_name> --output ./builds/<collection_name>`).
        *   Explain: "This command executes the build script for the '<collection_name>' collection, creating a filtered build artifact."
    *   **Expected Output from Delegate:** Terminal output indicating success or failure. Exit code 0 for success.
    *   **Coordinator Action (Post-Delegation):**
        *   Wait for command completion.
        *   Record the success/failure status for this collection based on exit code and output. Log key output messages.
    *   **Error Handling:** If the command fails, log the error details for this collection. Decide whether to stop the batch or continue with the next collection (potentially ask the user).

*   **Step 7: Report Batch Outcome (Roo Commander Task)**
    *   **Description:** Inform the user about the overall result of the batch build process.
    *   **Inputs:** Success/failure status recorded for each collection in Step 6.
    *   **Procedure:** Summarize which collections were built successfully and which failed, providing error details for failures.
    *   **Outputs:** User notification via `<attempt_completion>`.

## 7. Postconditions ✅
*   Build artifacts exist for all successfully processed collections (likely in distinct output locations).
*   A summary report of the batch build success/failure is provided to the user.

## 8. Error Handling & Escalation (Overall) ⚠️
*   Failure to read/parse config is fatal for the batch.
*   Failure to write `.roomodes` for a collection should be logged, and the user potentially consulted about continuing.
*   Failure of the build script for one collection should be logged, and the user potentially consulted about continuing the batch run for other collections.

## 9. PAL Validation Record 🧪
*   Date Validated:
*   Method:
*   Test Case(s):
*   Findings/Refinements:

## 10. Revision History 📜
*   v1.0 (2025-04-27): Initial draft for batch building based on JSON config.