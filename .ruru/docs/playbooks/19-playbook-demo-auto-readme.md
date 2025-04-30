+++
# --- Metadata ---
id = "PLAYBOOK-DEMO-AUTO-README-V1"
title = "Capability Playbook: Automated README Generation from Code"
status = "draft" # Start as draft until tested
created_date = "2025-04-24"
updated_date = "2025-04-24"
version = "1.0"
tags = ["playbook", "documentation", "capability-demo", "readme", "code-analysis", "documentation-generation", "technical-writing", "epic", "feature", "task"]
related_docs = [
    ".ruru/docs/standards/project-management-strategy-v1.md",
    ".ruru/planning/project-structure/00-epic-feature-task-plan.md",
    ".ruru/modes/agent-context-discovery/agent-context-discovery.mode.md",
    ".ruru/modes/util-senior-dev/util-senior-dev.mode.md", # For deeper code analysis
    ".ruru/modes/util-writer/util-writer.mode.md"
]
objective = "Guide the process of analyzing a specified codebase directory using AI agents (`agent-context-discovery`, `util-senior-dev`) and then delegating to `util-writer` to generate a comprehensive draft README.md file."
scope = "Covers identifying the target directory, analyzing project structure/dependencies/purpose, generating standard README sections (Installation, Usage, etc.), and saving the draft."
target_audience = ["Users", "Developers", "AI Modes"]
# --- Document Specific Fields ---
example_project_type = "Existing Codebase without a README or with an outdated one"
target_directory_placeholder = "[path/to/codebase]"
output_readme_path_placeholder = "[path/to/codebase]/README.md"
+++

# Capability Playbook: Automated README Generation from Code

This playbook demonstrates how Roo Commander can analyze an existing codebase and utilize specialist modes to automatically generate a draft `README.md` file, significantly speeding up documentation efforts.

**Scenario:** You have a codebase located at `[target_directory_placeholder]` that needs a comprehensive README file outlining its purpose, setup, and usage.

## Phase 1: Target Definition & Analysis Setup

1.  **Define the README Generation Goal (Epic/Feature):**
    *   **Goal:** Automatically generate a draft README for the specified codebase.
    *   **Action:** Create a Feature (e.g., `.ruru/features/FEAT-220-generate-readme-for-[project-name].md`).
    *   **Content:** Define `objective` (e.g., "Analyze the codebase at `[target_directory_placeholder]` and generate a draft `README.md` including key sections."), specify `[target_directory_placeholder]`. Set `status` to "Planned".

2.  **Confirm Target & Existing README Check (Coordinator Task):**
    *   **Goal:** Verify the target directory and check if a README already exists.
    *   **Inputs:** `[target_directory_placeholder]` from Feature.
    *   **Tool:** `list_files`, `ask_followup_question`
    *   **Procedure:**
        1.  Use `<list_files><path>[target_directory_placeholder]</path></list_files>` to confirm the directory exists. Handle errors if not found.
        2.  Check if `README.md` (case-insensitive) exists within the listed files.
        3.  **If README exists:** Use `<ask_followup_question>`: "A `README.md` already exists in `[target_directory_placeholder]`. Do you want to overwrite it with a newly generated draft, or cancel?" Options: "Overwrite existing README", "Cancel generation". Handle cancellation.
        4.  **If README doesn't exist or user confirms overwrite:** Proceed to Phase 2.
    *   **Outputs:** Confirmation to proceed.

## Phase 2: Codebase Analysis

1.  **Analyze Project Structure & Dependencies (Feature/Tasks):**
    *   **Goal:** Understand the project's language, package manager, key files, dependencies, and basic structure.
    *   **Action:** Define as a Feature (`FEAT-221-analyze-codebase-structure.md`). Decompose into Tasks.
    *   **Tasks (Examples - Delegate to `agent-context-discovery`):**
        *   "List all files recursively within `[target_directory_placeholder]`." (Use `list_files`, store result).
        *   "Analyze the file list and identify the primary programming language(s), package manager (npm, yarn, pnpm, pip, cargo, etc.), main configuration files (`package.json`, `pyproject.toml`, `Cargo.toml`, etc.), and likely source code directories (e.g., `src`, `lib`, `app`)." (Provide file list as input).
        *   "Read the primary configuration file (e.g., `package.json`) identified in the previous step." (`read_file`).
        *   "Analyze the configuration file content: extract project name, description (if any), dependencies, and key scripts (e.g., `build`, `start`, `test`)." (Provide file content as input).
    *   **Process:** Use MDTM workflow. Each task provides input for the next. Store structured analysis results (language, package manager, dependencies, scripts, etc.) – potentially as JSON within the final analysis task's result or notes.

2.  **Analyze Core Purpose & Usage (Feature/Tasks):**
    *   **Goal:** Understand *what* the code does and *how* it's typically run or used. This is harder and may require more sophisticated analysis.
    *   **Action:** Define as a Feature (`FEAT-222-analyze-codebase-purpose.md`). Decompose into Tasks.
    *   **Tasks (Examples - Delegate to `util-senior-dev` or `agent-context-discovery`):**
        *   "Identify main entry point file(s) based on analysis from FEAT-221 (e.g., `src/index.ts`, `main.py`, `app.js`)."
        *   "Read the content of the main entry point file(s)." (`read_file`).
        *   "Analyze the entry point code and top-level comments/docstrings to determine the primary purpose or function of the codebase." (Provide code content).
        *   *(Optional - More Advanced)* "Identify key public functions/classes/APIs exported by the main modules and summarize their purpose based on code and comments." (May require multiple `read_file` calls and more context).
    *   **Output:** Store a concise summary of the project's likely purpose and basic usage patterns (derived from `start` scripts or entry point analysis).

## Phase 3: README Generation

1.  **Generate README Draft (Task):**
    *   **Goal:** Synthesize the analysis findings into a structured README.md file.
    *   **Action:** Define as the primary Task under the main Feature (`FEAT-220`). Delegate to `util-writer`.
    *   **Inputs:** Structured analysis results from Phase 2 (Project Structure, Dependencies, Scripts, Purpose Summary, Key Functions/APIs if identified). `[target_directory_placeholder]`.
    *   **Tool:** `new_task` (delegating to `util-writer`), `write_to_file` (likely performed by `util-writer`)
    *   **Procedure:**
        1.  Generate Task ID (`TASK-WRITE-...`). Log delegation.
        2.  Formulate message for `util-writer`:
            ```xml
            <new_task>
              <mode>util-writer</mode>
              <message>
              ✍️ Generate README.md Task:
              Target Directory: `[target_directory_placeholder]`
              Output File: `[output_readme_path_placeholder]` <!-- e.g., [target_directory_placeholder]/README.md -->

              Analysis Findings:
              - Project Name: [Extracted Name]
              - Language(s): [Detected Language(s)]
              - Package Manager: [Detected Manager]
              - Key Dependencies: [List of dependencies]
              - Key Scripts: { build: "...", start: "...", test: "..." }
              - Core Purpose Summary: [Summary from analysis]
              - Key Functions/APIs (Optional): [Summary if available]

              Instructions: Generate a comprehensive draft `README.md` file for the project at `[output_readme_path_placeholder]`. Include the following standard sections, populating them based *only* on the provided Analysis Findings:
              1.  **Title:** Use Project Name.
              2.  **Description:** Use Core Purpose Summary, potentially elaborating slightly.
              3.  **Installation:** Provide clear steps using the detected Package Manager and install script (e.g., `npm install`). Include prerequisites like Node.js/Python version if inferable.
              4.  **Usage:** Explain how to run the project using the detected `start` or main execution script. Provide a basic example if possible.
              5.  **Building:** (If applicable) Explain how to build using the `build` script.
              6.  **Testing:** (If applicable) Explain how to run tests using the `test` script.
              7.  **(Optional) Key Features/API:** Briefly list key functions/APIs identified in analysis.
              8.  **Contributing:** Add placeholder text (e.g., "Contributions are welcome! Please follow standard procedures.").
              9.  **License:** Add placeholder text (e.g., "Specify license here" or use project name from `package.json` if license field present).

              Ensure output is well-formatted Markdown. Use the `write_to_file` tool to save the result.
              Your Task ID: [Generated TASK-WRITE-... ID].
              Coordinator Task ID: [Coordinator's Task ID].
              </message>
            </new_task>
            ```
        3.  Await `attempt_completion`.
    *   **Outputs:** Draft `README.md` file created at `[output_readme_path_placeholder]`.
    *   **Error Handling:** Handle `new_task` failure or failure reported by `util-writer`.

## Phase 4: Review & Finalization

1.  **Manual Review (User Task):**
    *   **Goal:** Check the generated README for accuracy, completeness, and clarity.
    *   **Action:** Instruct user: "I've generated a draft README.md in `[target_directory_placeholder]`. Please review it carefully. The AI analysis provides a good starting point, but may require manual additions or corrections, especially regarding specific usage examples or detailed feature descriptions."

2.  **Gather Feedback & Optional Refinement (Coordinator Task):**
    *   **Goal:** Incorporate user feedback for minor corrections.
    *   **Tool:** `ask_followup_question`, `apply_diff` (via delegation if needed)
    *   **Procedure:**
        1.  Ask: "Does the generated README need any immediate corrections or additions?"
        2.  If user provides specific, small changes: Delegate to `util-writer` or `prime-coordinator` using `apply_diff` to update `[output_readme_path_placeholder]`.
        3.  If major changes needed: Inform the user that significant edits are best done manually or as separate, more specific tasks.

3.  **Complete Feature:**
    *   **Action:** Mark the `FEAT-220-generate-readme-for-[project-name].md` as "Done".

## Key Considerations for Automated README Generation:

*   **Analysis Accuracy:** The quality of the README depends heavily on the accuracy of the code analysis in Phase 2. Complex projects or non-standard structures might confuse the analysis agents.
*   **Context Limits:** Analyzing *entire* large codebases is usually infeasible due to context limits. The process relies on analyzing key files (`package.json`, entry points) effectively.
*   **"Draft" Status:** Emphasize to the user that the output is a *draft*. It's a starting point, not a replacement for human understanding and detailed documentation writing.
*   **Usage Examples:** AI might struggle to generate *meaningful* usage examples without deeper semantic understanding or running the code. Placeholders or very basic examples are more realistic.
*   **Overwrite Confirmation:** Ensure the user confirms overwriting an existing README (Phase 1).

This playbook uses analysis and writing agents to automate a significant portion of README creation, providing a valuable starting point for project documentation.