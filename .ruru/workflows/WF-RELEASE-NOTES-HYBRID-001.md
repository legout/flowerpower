+++
# --- Basic Metadata ---
id = "WF-RELEASE-NOTES-HYBRID-001"
title = "Workflow: Generate Release Notes (Hybrid Approach)"
description = "Generates release notes as a local Markdown file, with an optional step to push to GitHub Releases via MCP."
version = "0.1.0"
status = "draft" # Options: draft, active, deprecated, inactive
created_date = "2025-04-25" # Use current date
last_updated = "2025-04-25" # Use current date
authors = ["prime-coordinator"]
tags = ["workflow", "release-notes", "changelog", "git", "github", "mcp", "automation", "hybrid"]

# --- Workflow Configuration ---
# target_audience = ["roo-commander", "lead-devops", "manager-project"] # Who typically runs this
# trigger = ["manual", "workflow_step"] # How is it typically started?
# complexity = "medium" # low, medium, high
# estimated_duration = "5-15 minutes" # Rough estimate

# --- Related Context ---
related_context = [
    ".ruru/planning/github-deeper-integration/PLAN-RELEASE-NOTES-WHITEPAPER.md",
    ".ruru/planning/github-deeper-integration/PLAN-RELEASE-NOTES-MCP-WORKFLOW.md",
    ".ruru/planning/github-deeper-integration/PLAN-RELEASE-NOTES-LOCAL-WORKFLOW.md",
    ".ruru/planning/github-deeper-integration/PLAN-RELEASE-NOTES-SOURCE-OF-TRUTH.md",
    ".ruru/planning/github-deeper-integration/PLAN-RELEASE-NOTES-TRIGGERS.md",
    ".roo/rules/07-git-commit-standard-simplified.md",
    ".ruru/templates/toml-md/NN_release_notes.md" # Assumes template exists
]

# --- Input Parameters ---
[parameters]
target_tag = { type = "string", description = "The Git tag for the current release (e.g., v1.2.0).", required = true }
previous_tag = { type = "string", description = "The Git tag for the previous release to compare against. If omitted, uses the latest tag before target_tag.", required = false }
output_dir = { type = "string", description = "Directory to save the local release notes file.", default = ".ruru/docs/release-notes/" }
push_to_github = { type = "boolean", description = "Attempt to create/update GitHub Release via MCP.", default = false }
github_owner = { type = "string", description = "GitHub repository owner (required if push_to_github is true).", required = false }
github_repo = { type = "string", description = "GitHub repository name (required if push_to_github is true).", required = false }
mark_as_draft = { type = "boolean", description = "Mark the GitHub Release as a draft.", default = true }
mark_as_prerelease = { type = "boolean", description = "Mark the GitHub Release as a pre-release.", default = false }

# --- Workflow Steps ---
# Use Markdown checklist format. Prefix steps requiring specific modes or tools.
# Use 📣 to indicate steps that should report progress back to the coordinator/user.
# Use ❓ to indicate decision points or optional steps.
# Use ❗ for critical failure points.
+++

# Workflow: Generate Release Notes (Hybrid Approach)

This workflow generates release notes by analyzing Git history between two tags, creates a local Markdown file, and optionally attempts to push the notes to a GitHub Release using the GitHub MCP server. It follows the Hybrid approach (Option C) and the recommended Hybrid Source of Truth.

## Checklist

-   [ ] **1. Initialization & Input Validation:**
    -   [ ] 📣 Verify required parameters (`target_tag`).
    *   [ ] Determine `previous_tag`: If not provided, delegate to `dev-git` or GitHub MCP (`get_latest_tag`?) to find the latest tag before `target_tag`. Store result.
    *   [ ] ❗ If `push_to_github` is true, verify `github_owner` and `github_repo` are provided. Fail if not.
    *   [ ] ❗ Verify the existence and connectivity of the GitHub MCP server if `push_to_github` is true. Fail if not available.

-   [ ] **2. Query Git History:**
    *   [ ] Delegate to `dev-git`: Execute `git log --pretty=format:"%H ||| %s ||| %b%n---COMMIT-END---%n" <previous_tag>..<target_tag>`. Use clear delimiters like `|||` and `---COMMIT-END---` for easier parsing.
    *   [ ] ❗ Store the raw `git log` output. Handle potential errors from `dev-git` (e.g., invalid tags).

-   [ ] **3. Parse & Filter Commits:**
    *   [ ] Process the raw `git log` output line by line or commit by commit.
    *   [ ] For each commit:
        *   [ ] Parse hash, subject, and body using the delimiters.
        *   [ ] Identify Conventional Commit type (`feat`, `fix`, `perf`, `refactor`, `chore`, `docs`, `test`, etc.) from the subject. Skip commits without a recognized type or merge commits (unless configured otherwise).
        *   [ ] Extract scope (if present).
        *   [ ] Extract `Refs: TASK-...` from the footer. Store Task ID(s).
    *   [ ] Store the filtered and parsed commit data, grouped by type (e.g., `features: [{subject, hash, taskId}, ...]`, `fixes: [...]`).

-   [ ] **4. Summarize Changes (Hybrid Source of Truth):**
    *   [ ] Initialize Markdown sections for each commit type (Features, Bug Fixes, etc.).
    *   [ ] For each parsed commit in each group:
        *   [ ] ❓ **(Enhancement):** If a `taskId` exists:
            *   [ ] Delegate to `agent-context-resolver` or `prime-txt` to read the corresponding MDTM task file (`.ruru/tasks/.../TASK-....md`).
            *   [ ] Extract the task `title` from the TOML frontmatter. Use this title if available.
            *   [ ] *Alternative/Simpler:* Just use the commit subject line.
        *   [ ] Format the entry (e.g., `- Scope: Title/Subject (Commit Hash, Refs: TASK-ID)` or similar). Add to the appropriate Markdown section string.
    *   [ ] Combine the formatted sections into a single `release_notes_body` Markdown string.

-   [ ] **5. Generate Local Release Notes File:**
    *   [ ] Define output filename: `{{output_dir}}/{{target_tag}}.md`.
    *   [ ] Prepare TOML frontmatter for the local file using a template (e.g., `NN_release_notes.md`), including version, date, related tags, etc.
    *   [ ] Combine TOML and the `release_notes_body`.
    *   [ ] Delegate to `prime-txt`: Use `write_to_file` to create the local file at the defined path with the combined content.
    *   [ ] ❗ Handle potential file writing errors.
    *   [ ] 📣 Report success and the path to the created local file.

-   [ ] **6. ❓ Optional: Push to GitHub Release (via MCP):**
    *   [ ] **IF `push_to_github` is true:**
        *   [ ] 📣 Indicate attempt to push to GitHub.
        *   [ ] Delegate to GitHub MCP server (`create_release` or `update_release` - need logic to check if release/tag already exists):
            *   Provide `owner`, `repo`, `target_tag`.
            *   Provide `release_notes_body` as the body.
            *   Set release `name` (e.g., "Version {{target_tag}}").
            *   Set `draft = {{mark_as_draft}}`, `prerelease = {{mark_as_prerelease}}`.
        *   [ ] ❗ Handle potential errors from the MCP server (authentication, API errors, tag already exists, etc.).
        *   [ ] 📣 Report success (with link to draft release) or failure of the GitHub push attempt.
    *   [ ] **ELSE:**
        *   [ ] 📣 Skip GitHub push as requested.

-   [ ] **7. Final Report:**
    *   [ ] 📣 Report overall completion, summarizing which steps were successful (local file creation, optional GitHub push).