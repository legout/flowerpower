+++
# --- Metadata ---
id = "PLAYBOOK-CLI-DEV-V1"
title = "Project Playbook: Command-Line Interface (CLI) Tool Development"
status = "published"
created_date = "2025-04-24"
updated_date = "2025-04-24"
version = "1.0"
tags = ["playbook", "documentation", "project-management", "cli", "command-line", "developer-tool", "npm", "epic", "feature", "task"]
related_docs = [
    ".ruru/docs/standards/project-management-strategy-v1.md",
    ".ruru/planning/project-structure/00-epic-feature-task-plan.md",
    ".ruru/planning/cli-build/00-cli-build-plan.md" # Reference the specific plan if building roocommander-cli
]
objective = "Provide a structured approach for planning, developing, testing, and preparing a Command-Line Interface (CLI) tool for distribution (e.g., via npm) using the Roo Commander Epic-Feature-Task hierarchy."
scope = "Covers phases from project setup and core command implementation to build processes, documentation, and release preparation."
target_audience = ["Users", "Developers", "AI Modes"]
# --- Document Specific Fields ---
example_project_type = "Node.js CLI Tool (e.g., build tool, code generator, management utility)"
+++

# Project Playbook: Command-Line Interface (CLI) Tool Development

This playbook outlines a recommended approach for managing the development of a CLI tool (like the `roocommander` CLI itself) using Roo Commander's Epic-Feature-Task hierarchy.

**Scenario:** You want to build a new CLI application, typically using Node.js/TypeScript and intended for distribution via npm.

## Phase 1: Project Setup & Core Structure

1.  **Define the CLI (Epic):**
    *   **Goal:** Establish the overall purpose and scope of the CLI tool.
    *   **Action:** Create the main Epic (e.g., `.ruru/epics/EPIC-010-build-roocommander-cli.md`).
    *   **Content:** Define the `objective` (e.g., "Create a CLI tool to manage Roo Commander workspace configurations"), `scope_description` (list intended high-level commands/features), target user, and core technologies (Node.js, TypeScript, Commander.js). Set `status` to "Planned".

2.  **Initialize Project Structure (Feature & Tasks):**
    *   **Goal:** Set up the basic Node.js project files and directories.
    *   **Action:** Define this as the first Feature (e.g., `.ruru/features/FEAT-050-cli-project-initialization.md`), linked to the Epic.
    *   **Tasks (Delegate to `roo-commander` initially, referencing `.ruru/planning/cli-build/01-cli-project-setup.md`):**
        *   Create root directory (e.g., `cli/`).
        *   Create subdirectories (`src`, `bin`, `dist`, `templates` if needed).
        *   Generate initial `package.json` (define `name`, `version`, basic `scripts`, importantly the `bin` field mapping the CLI command name to the executable script path like `"roo": "./dist/bin/roo-cli.js"`).
        *   Generate `tsconfig.json` for TypeScript compilation.
        *   Generate `.gitignore`.
    *   Update Feature status to "Done" when basic structure exists.

3.  **Implement Core CLI Framework (Feature & Tasks):**
    *   **Goal:** Set up the main executable script and argument parsing foundation.
    *   **Action:** Define as a second Feature (e.g., `.ruru/features/FEAT-051-cli-core-framework-setup.md`), linked to the Epic.
    *   **Tasks (Delegate to `util-typescript` / `util-senior-dev`, referencing `.ruru/planning/cli-build/02-cli-core-structure.md`):**
        *   Install core dependencies (`commander`, `chalk`, `inquirer`, `fs-extra` via `npm install`).
        *   Install dev dependencies (`typescript`, `@types/node`, etc. via `npm install --save-dev`).
        *   Create the main entry point script (`cli/src/bin/roo-cli.ts` or similar).
        *   Add shebang (`#!/usr/bin/env node`).
        *   Initialize `commander`: Set version, description.
        *   Add placeholder command registrations (`program.command(...).action(...)`).
        *   Add main execution line: `program.parse(process.argv)`.
    *   Update Feature status to "Done" when the basic CLI runs (even if commands do nothing yet).

## Phase 2: Command Implementation (Features & Tasks)

1.  **Define a Command (Feature):**
    *   **Goal:** Plan a specific CLI command (e.g., `init`, `install-mcp`, `validate`).
    *   **Action:** Create a Feature file for the command (e.g., `.ruru/features/FEAT-052-implement-init-command.md`), linked to the Epic.
    *   **Content:** Define `description` (what the command does), `acceptance_criteria` (how to verify it works, including arguments, options, expected output/side effects). List dependencies on other features/setup. Set `status` to "Ready for Dev".

2.  **Decompose Command into Tasks:**
    *   **Goal:** Create the granular implementation tasks for the command.
    *   **Action:** `roo-commander` or a Lead decomposes the Feature.
    *   **Process:**
        *   Follow MDTM Task Creation workflow (Rule `04`).
        *   Assign tasks to `util-typescript`, `util-senior-dev`.
        *   **Set `feature_id` and `epic_id`** in Task metadata.
        *   **Task Examples (for `init` command):**
            *   "Write `handleInitCommand` function in `cli/src/commands/init.ts`."
            *   "Implement logic to check for existing `.roo`/`.ruru` dirs using `fs-extra`."
            *   "Implement interactive overwrite confirmation using `inquirer`."
            *   "Implement file/directory copying from template dir using `fs-extra`."
            *   "Add console logging with `chalk` for success/error messages."
            *   "Register `init` command and action handler in `cli/src/bin/roo-cli.ts`."
            *   "Write basic unit test for path resolution logic (if applicable)."
        *   Delegate tasks via `new_task`. Update Feature's `related_tasks`.

3.  **Implement & Test Command Tasks:**
    *   **Goal:** Write and verify the code for the command.
    *   **Action:** Specialists execute tasks, writing TypeScript code, using `read_file`/`write_to_file` or delegating edits via `prime-coordinator`. **Testing within the `cli/` directory context is key.**
    *   **Process:**
        *   Specialists write code and update their `TASK-...md` files.
        *   Run `npm run build` in `cli/` CWD frequently via `execute_command` to catch TS errors.
        *   Perform basic manual tests by running the compiled CLI from the workspace root (e.g., `node ./cli/dist/bin/roo-cli.js init --options...` in a *separate test directory*).
        *   Write unit/integration tests where applicable.

4.  **Repeat for Other Commands:** Repeat steps 1-3 for each major command/feature of the CLI.

## Phase 3: Build, Documentation, and Release Prep

1.  **Refine Build Process (Feature):**
    *   **Goal:** Ensure the build process is robust and produces the correct output in `cli/dist/`.
    *   **Action:** Define as a Feature (`FEAT-060-cli-build-packaging.md`).
    *   **Tasks:**
        *   "Verify `tsconfig.json` `outDir` and `rootDir` are correct."
        *   "Ensure `package.json` `files` array includes `dist`, `bin`, and other necessary assets."
        *   "Add `prepublishOnly` script to `package.json` to run `npm run build` automatically before publishing." (Delegate to `util-senior-dev`).
        *   "Test the build process clean (`rm -rf dist && npm run build`)." (Coordinator task via `execute_command`).

2.  **Write CLI Documentation (Feature):**
    *   **Goal:** Create user-facing documentation (README, potentially usage examples).
    *   **Action:** Define as a Feature (`FEAT-061-cli-documentation.md`).
    *   **Tasks (Delegate to `util-writer`):**
        *   "Write `cli/README.md` covering installation (`npm install -g ...`), usage of all commands, options, and examples."
        *   "Update main project `README.md` to mention the CLI tool."

3.  **Prepare for Publishing (Feature):**
    *   **Goal:** Final checks before potentially publishing to npm.
    *   **Action:** Define as a Feature (`FEAT-062-cli-release-prep.md`).
    *   **Tasks:**
        *   "Bump version number in `cli/package.json` according to semantic versioning." (Delegate to `util-senior-dev`).
        *   "Create Git tag for the version." (Delegate to `dev-git`).
        *   "Manual Step: Log in to npm (`npm login`)." (Instruction for user).
        *   "Manual Step: Publish the package (`npm publish` from within `cli/` directory)." (Instruction for user).
        *   *(Note: Roo Commander should likely not perform the actual `npm publish` for safety).*

4.  **Update Epic Status:** Mark the main CLI Epic as "Done" or ready for release.

## Key Considerations for CLI Development:

*   **Argument Parsing:** Rely heavily on libraries like `commander` or `yargs` for robust parsing of commands, arguments, and options.
*   **User Experience:** Use libraries like `chalk` for clear, colored terminal output and `inquirer` for interactive prompts. Provide helpful error messages.
*   **Cross-Platform Issues:** Be mindful of file system paths (`path` module), line endings, and shell commands (`execute_command` needs OS check) if targeting multiple OS.
*   **Dependencies:** Keep dependencies minimal. Clearly distinguish between `dependencies` and `devDependencies` in `package.json`.
*   **Executable Permissions:** The build script in the example plan includes `chmodSync` to make the output script executable on Linux/macOS. This is important for the `bin` linking to work correctly after global install.
*   **Testing:** Unit tests for core logic and integration tests (potentially running the compiled CLI as a child process) are crucial.
*   **Error Handling:** Implement proper try/catch blocks and exit codes for different failure scenarios.

This playbook provides a detailed structure for building your CLI tool methodically using the Epic-Feature-Task system.