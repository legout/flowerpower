+++
# --- Basic Metadata ---
id = "WF-CREATE-ROO-CMD-BUILD-001"
title = "Workflow: Create Roo Commander Build Archive"
status = "active"
created_date = "2025-04-20"
updated_date = "2025-04-21" # Updated date
version = "1.2" # Updated version
tags = ["workflow", "build", "release", "archive", "zip", "versioning", "git", "github", "roo-commander"] # Added git, github

# --- Ownership & Context ---
owner = "Roo Commander"
related_docs = [
  ".builds/README.md",
  ".ruru/docs/standards/roo-commander-version-naming-convention.md",
  "create_build.js" # Corrected reference to the JS script
]
related_templates = []

# --- Workflow Specific Fields ---
objective = "To stage, commit, and push changes, create a standardized, versioned zip archive of the Roo Commander configuration files, place it in the `.builds/` directory, log the build, and create a GitHub release with the artifact." # Updated objective
scope = "Applies when preparing a new distributable release of the Roo Commander configuration."
roles = [
  "Coordinator (Roo Commander)",
  "Executor (Terminal via `execute_command`)",
  "Technical Writer (Optional, for CHANGELOG)",
  "Executor (Git CLI via `execute_command`)",
  "Executor (GitHub CLI via `execute_command`)"
]
trigger = "Manual initiation by the Coordinator when a new build is required."
success_criteria = [
  "All modified files are successfully staged, committed, and pushed to the remote Git repository.", # Added Git success criteria
  "A zip archive named according to the versioning convention (e.g., `roo-commander-vX.Y.Z-Codename.zip`) is created in the `.builds/` directory.", # Corrected version format
  "The archive contains the correct set of included files/folders and excludes the specified ones.",
  "The archive contains a `README.md` with setup instructions.",
  "The archive contains an up-to-date `CHANGELOG.md`.",
  "The `.builds/README.md` log file is updated with the details of the new build.",
  "The build script executes successfully (exit code 0).",
  "A GitHub release is created with the correct tag, title, notes, and attached build artifact.",
  "The `gh release create` command executes successfully (exit code 0)."
]
failure_criteria = [
  "Git staging, commit, or push fails.", # Added Git failure criteria
  "The build script (if used) fails or produces errors.",
  "The zip archive is not created or is placed in the wrong location.",
  "The zip archive has an incorrect name.",
  "The contents of the zip archive are incorrect (missing files, includes excluded files).",
  "The `README.md` or `CHANGELOG.md` within the archive is missing or incorrect.",
  "The `.builds/README.md` log file is not updated or contains errors.",
  "The GitHub release creation fails.",
  "The build artifact upload fails."
]

# --- Integration ---
acqa_applicable = false # Workflow primarily orchestrates a build script/process
pal_validated = false # Needs validation once implemented
validation_notes = "Workflow needs implementation and testing, potentially involving creation of a build script."

# --- AI Interaction Hints (Optional) ---
# context_type = "workflow_definition"
+++

# Workflow: Create Roo Commander Build Archive

## 1. Objective 🎯
*   To ensure all relevant changes are committed and pushed to the Git repository.
*   To create a standardized, versioned zip archive (`.zip`) containing the necessary Roo Commander configuration files for distribution.
*   To ensure the archive follows the defined versioning and naming conventions.
*   To place the archive in the designated `.builds/` directory.
*   To maintain a log of created builds in `.builds/README.md`.
*   To create a corresponding release on GitHub with the build artifact attached.

## 2. Scope ↔️
*   This workflow is triggered manually when a new distributable build of the Roo Commander configuration is needed.

## 3. Roles & Responsibilities 👤
*   **Coordinator (Roo Commander):** Initiates the workflow, determines version information, prepares CHANGELOG and README, updates build log, handles Git operations (staging, commit, push), executes the build process, verifies output, and creates the GitHub release.
*   **Executor (Terminal):** Runs the Git, build script, and GitHub CLI commands provided by the Coordinator.
*   **Technical Writer (Optional):** Can be delegated the task of creating or updating the `CHANGELOG.md`.

## 4. Preconditions🚦
*   The `.builds/` directory exists.
*   The `.builds/README.md` file exists (or will be created on the first run).
*   The `.ruru/docs/standards/roo-commander-version-naming-convention.md` document exists and is up-to-date.
*   The `create_build.js` script exists and performs the archiving correctly.
*   Necessary tools (`git`, `node`, `gh` CLI) are available and configured (including Git/GitHub authentication).
*   The local Git repository is clean or has only the intended changes for the release staged.

## 5. Reference Documents & Tools 📚🛠️
*   `.builds/README.md`: Log file for build history.
*   `.ruru/docs/standards/roo-commander-version-naming-convention.md`: Defines version numbers and codenames.
*   `create_build.js`: The script automating the build process.
*   `.tmp/CHANGELOG.md`: Temporary file holding the changelog for the current build.
*   `.tmp/README.md`: Temporary file holding the distribution README for the current build.
*   `git` (Git CLI): Tool for staging, committing, and pushing changes.
*   `gh` (GitHub CLI): Tool for interacting with GitHub, specifically for creating releases.
*   `execute_command`: Tool to run the build script, `git`, and `gh` commands.
*   `read_file`: Tool to read version info, changelogs, build logs.
*   `write_to_file`: Tool to create temporary README/CHANGELOG files.
*   `append_to_file`: Tool to add entries to the build log.
*   `list_files`: Tool to verify script existence or build output.
*   `technical-writer` (Mode): Optional delegate for `CHANGELOG.md` creation/update.

## 6. Workflow Steps 🪜

*   **Step 1: Determine Build Version & Codename (Coordinator Task)**
    *   **Description:** Identify the correct version number (e.g., `v7.0.4`) and codename (e.g., `Wallaby`) for the new build.
    *   **Inputs:** `.ruru/docs/standards/roo-commander-version-naming-convention.md`, potentially `.builds/README.md` to find the last version.
    *   **Procedure:**
        1.  Read `.ruru/docs/standards/roo-commander-version-naming-convention.md` to confirm the current major version's codename.
        2.  Read `.builds/README.md` (if it exists) to determine the last build number for the current major version.
        3.  Increment the minor version number (e.g., v7.0.3 -> v7.0.4).
        4.  Construct the full version string (e.g., `v7.0.4`) and the archive filename stem (e.g., `roo-commander-v7.0.4-Wallaby`).
    *   **Outputs:** `BUILD_VERSION` (e.g., "v7.0.4"), `BUILD_CODENAME` (e.g., "Wallaby"), `ARCHIVE_NAME_STEM` (e.g., "roo-commander-v7.0.4-Wallaby").

*   **Step 2: Prepare CHANGELOG (Coordinator Task / Optional Delegation)**
    *   **Description:** Create or update a `CHANGELOG.md` file detailing changes for this specific build version.
    *   **Inputs:** `BUILD_VERSION`, knowledge of recent changes, previous `CHANGELOG.md` (if available).
    *   **Procedure:**
        *   **Option A (Manual/Coordinator):** Gather notes on changes since the last build. Format them into a new entry in `CHANGELOG.md` under the `BUILD_VERSION` heading. Use `write_to_file` to create/update a temporary changelog file (e.g., `.tmp/CHANGELOG.md`).
        *   **Option B (Delegate):** Delegate to `technical-writer` via `new_task`: "Create/Update CHANGELOG.md for build [BUILD_VERSION]. Summarize recent changes [provide details or pointers]. Save output to `.tmp/CHANGELOG.md`." Await completion.
    *   **Outputs:** A `CHANGELOG.md` file ready for inclusion in the build (e.g., located at `.tmp/CHANGELOG.md`).

*   **Step 3: Prepare Distribution README (Coordinator Task)**
    *   **Description:** Ensure the `README.md` file intended for *inside* the zip archive is ready, potentially updating version numbers.
    *   **Inputs:** Source `README.md`, `BUILD_VERSION`, `BUILD_CODENAME`.
    *   **Procedure:**
        1.  Read the source `README.md`.
        2.  Update any placeholders (like the current version number in installation instructions). Use `search_and_replace` if needed on the source `README.md` first.
        3.  Use `write_to_file` to save the finalized content to a temporary location (e.g., `.tmp/README.md`).
    *   **Outputs:** A `README.md` file ready for inclusion in the build (e.g., located at `.tmp/README.md`).

*   **Step 4: Update Build Log (Coordinator Task)**
    *   **Description:** Add an entry for the newly created build to the `.builds/README.md` log file.
    *   **Inputs:** `BUILD_VERSION`, `BUILD_CODENAME`, Current Date, `ARCHIVE_NAME_STEM`.
    *   **Procedure:**
        1.  Get the current date (e.g., YYYY-MM-DD).
        2.  Format the log entry (e.g., `- **${BUILD_VERSION} (${BUILD_CODENAME})** - ${YYYY-MM-DD} - File: \`${ARCHIVE_NAME_STEM}.zip\``).
        3.  Use `append_to_file` to add the new entry to `.builds/README.md`. If the file doesn't exist, use `write_to_file` to create it with a header and the first entry.
    *   **Outputs:** Updated `.builds/README.md`.
    *   **Error Handling:** If writing/appending fails, report the error.

*   **Step 5: Stage Changes (Coordinator delegates to Executor via `execute_command`)**
    *   **Description:** Stage all modified files (including updated README, build log, etc.) for commit.
    *   **Tool:** `execute_command` (using `git`)
    *   **Inputs Provided by Coordinator:** None needed for the basic command.
    *   **Command Example:** `git add .`
    *   **Instructions for Executor:** Execute the provided `git add` command.
    *   **Expected Output from Executor:** Exit code 0.
    *   **Coordinator Action (Post-Execution):** Review output and exit code.
    *   **Validation/QA:** Check for non-zero exit code. `git status` could be run manually if needed, but generally rely on exit code.
    *   **Error Handling:** If errors occur, analyze output. Check if inside a Git repository. Report failure.

*   **Step 6: Commit Changes (Coordinator delegates to Executor via `execute_command`)**
    *   **Description:** Commit the staged changes with a standard message including the build version.
    *   **Tool:** `execute_command` (using `git`)
    *   **Inputs Provided by Coordinator:** `BUILD_VERSION` (e.g., "v7.0.4")
    *   **Command Example:** `git commit -m "Prepare release ${BUILD_VERSION}"`
    *   **Instructions for Executor:** Execute the provided `git commit` command.
    *   **Expected Output from Executor:** Output indicating files committed or "nothing to commit", exit code 0.
    *   **Coordinator Action (Post-Execution):** Review output and exit code.
    *   **Validation/QA:** Check for non-zero exit code (unless it's a "nothing to commit" scenario, which is okay).
    *   **Error Handling:** If errors occur (e.g., Git hooks fail, merge conflicts if run manually during issues), analyze output. Report failure.

*   **Step 7: Push Changes (Coordinator delegates to Executor via `execute_command`)**
    *   **Description:** Push the commit to the remote repository's main branch (assuming 'main' or 'master').
    *   **Tool:** `execute_command` (using `git`)
    *   **Inputs Provided by Coordinator:** None needed for the basic command.
    *   **Command Example:** `git push` (Assumes remote and branch are configured correctly).
    *   **Instructions for Executor:** Execute the provided `git push` command.
    *   **Expected Output from Executor:** Output indicating successful push, exit code 0.
    *   **Coordinator Action (Post-Execution):** Review output and exit code.
    *   **Validation/QA:** Check for non-zero exit code or error messages (e.g., authentication failure, non-fast-forward).
    *   **Error Handling:** If errors occur, analyze output. Check network, authentication (`gh auth status` might be relevant if using HTTPS), and whether the local branch is behind the remote. Report failure.

*   **Step 8: Execute Build Process (Coordinator delegates to Executor via `execute_command`)**
    *   **Description:** Run the automated script (`create_build.js`) to create the zip archive.
    *   **Tool:** `execute_command` (using `node`)
    *   **Inputs Provided by Coordinator:** `BUILD_VERSION`, `BUILD_CODENAME`, path to temp README (`.tmp/README.md`), path to temp CHANGELOG (`.tmp/CHANGELOG.md`).
    *   **Command Example:** `node create_build.js ${BUILD_VERSION} ${BUILD_CODENAME} .tmp/README.md .tmp/CHANGELOG.md`
    *   **Instructions for Executor:** Execute the provided `node` command.
    *   **Expected Output from Executor:** Terminal output indicating success (including archive path) or failure, exit code 0 for success.
    *   **Coordinator Action (Post-Execution):** Review output and exit code. Note the final archive path.
    *   **Validation/QA:** Check for success messages, non-zero exit code. Use `list_files` on `.builds/` to confirm the zip file exists with the correct name (e.g., `roo-commander-${BUILD_VERSION}-${BUILD_CODENAME}.zip`).
    *   **Error Handling:** If errors occur, analyze script output. Check file paths, permissions, tool availability (`node`, `zip`). Report failure or attempt troubleshooting.

*   **Step 9: Create GitHub Release (Coordinator delegates to Executor via `execute_command`)**
    *   **Description:** Create a new release on GitHub and upload the build artifact. **Important:** This step relies on the commit from Step 6 being pushed successfully in Step 7, as the tag `${BUILD_VERSION}` will be created based on the latest commit on the main branch.
    *   **Tool:** `execute_command` (using `gh` CLI)
    *   **Inputs Provided by Coordinator:**
        *   `BUILD_VERSION` (e.g., "v7.0.4")
        *   Target Repository (e.g., `jezweb/roo-commander`)
        *   Release Title (e.g., `${BUILD_VERSION} (${BUILD_CODENAME})`)
        *   Path to temporary CHANGELOG file (e.g., `.tmp/CHANGELOG.md`)
        *   Path to the build artifact zip file (e.g., `.builds/roo-commander-${BUILD_VERSION}-${BUILD_CODENAME}.zip`)
    *   **Command Example:** `gh release create ${BUILD_VERSION} --repo jezweb/roo-commander --title "${BUILD_VERSION} (${BUILD_CODENAME})" --notes-file .tmp/CHANGELOG.md .builds/roo-commander-${BUILD_VERSION}-${BUILD_CODENAME}.zip`
    *   **Instructions for Executor:** Execute the provided `gh release create` command.
    *   **Expected Output from Executor:** URL of the created release, exit code 0.
    *   **Coordinator Action (Post-Execution):** Review output and exit code.
    *   **Validation/QA:** Check for success messages (URL output), non-zero exit code. Verify the release exists on GitHub with the correct tag, title, notes, and attached asset.
    *   **Error Handling:** If the `gh` command fails, analyze output. Check authentication (`gh auth status`), repository name, tag existence, file paths, and permissions. Report failure or attempt troubleshooting.

## 7. Postconditions ✅
*   The local Git repository reflects all changes included in the build, and these changes are pushed to the remote.
*   A correctly named and structured zip archive exists in `.builds/`.
*   The `.builds/README.md` file contains an entry for the new build.
*   A corresponding release exists on GitHub with the build artifact attached, tagged at the correct commit.

## 8. Error Handling & Escalation (Overall) ⚠️
*   If Git operations fail, check repository status, authentication, network, and potential conflicts.
*   If the build script fails, debug the script.
*   If file operations fail, check permissions and paths.
*   If versioning information is inconsistent, review `.builds/README.md` and the versioning standard document.
*   If the GitHub release creation fails, check `gh` CLI authentication, command syntax, and network connectivity.
*   Escalate to the user if any step cannot be completed successfully after basic troubleshooting.

## 9. PAL Validation Record 🧪
*   Date Validated: (Pending Implementation)
*   Method:
*   Test Case(s):
*   Findings/Refinements:

## 10. Revision History 📜
*   v1.2 (2025-04-21): Inserted Git add, commit, push steps (5-7) before build (8) and release (9). Moved build log update to Step 4. Renumbered steps accordingly. Added `git` to tools list and updated descriptions/examples. Corrected build script example command and archive name format. Updated objective, preconditions, and postconditions.
*   v1.1 (2025-04-20): Added Step 6 for GitHub Release creation using `gh` CLI. Updated roles, criteria, and tools list.
*   v1.0 (2025-04-20): Initial draft incorporating versioning, build log, CHANGELOG, distribution README, and suggestion for an automated build script.