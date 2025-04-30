+++
id = "WF-MODE-DELETE-001"
title = "Workflow: Delete Custom Mode"
description = "Defines the steps to safely delete a custom mode, its associated rules, and update relevant configuration files."
status = "draft"
version = "0.1.0"
created_date = "2025-04-27"
last_updated = "2025-04-27"
tags = ["workflow", "mode", "delete", "configuration", "prime"]
actors = ["prime-coordinator", "prime-dev", "user"]
related_context = [".ruru/modes/", ".roo/rules-*/", ".roomodes", "build_roomodes.js", ".ruru/config/build_collections.json"]
+++

# Workflow: Delete Custom Mode

**Objective:** Safely remove a custom mode and its associated configuration from the workspace.

**Actors:**
*   `prime-coordinator`: Initiates and oversees the workflow.
*   `prime-dev`: Handles JSON file updates.
*   `user`: Provides confirmation.

**Trigger:** User selects the "Delete Modes" option within the "Mode Management" initialization choice.

**Procedure:**

1.  **Identify Mode:**
    *   `prime-coordinator` uses `<ask_followup_question>` to prompt the user for the exact `slug` of the mode to be deleted.
    *   `prime-coordinator` verifies the existence of the mode directory: `.ruru/modes/<mode-slug>/`.

2.  **Identify Associated Files/Dirs:**
    *   `prime-coordinator` identifies the primary directories/files to be removed:
        *   Mode Directory: `.ruru/modes/<mode-slug>/`
        *   Rules Directory (if exists): `.roo/rules-<mode-slug>/`
    *   `prime-coordinator` identifies files/processes requiring updates:
        *   `.roomodes` (Handled by build script)
        *   `.ruru/modes/roo-commander/kb/kb-available-modes-summary.md` (Handled by build script)
        *   `.ruru/config/build_collections.json` (Requires manual check/edit if mode is listed)

3.  **User Confirmation:**
    *   `prime-coordinator` presents the list of directories to be deleted and files potentially needing updates to the user.
    *   `prime-coordinator` uses `<ask_followup_question>` to request explicit confirmation ("Proceed with deletion?", "Cancel"). **CRITICAL: Do not proceed without explicit user confirmation.**

4.  **Execute Deletion:**
    *   **(If Confirmed):** `prime-coordinator` uses `<execute_command>` to delete the mode directory: `rm -rf .ruru/modes/<mode-slug>/`
    *   **(If Confirmed & Exists):** `prime-coordinator` uses `<execute_command>` to delete the rules directory: `rm -rf .roo/rules-<mode-slug>/`

5.  **Update Build Collections (If Necessary):**
    *   `prime-coordinator` checks if the mode slug exists in `.ruru/config/build_collections.json`.
    *   If found, `prime-coordinator` delegates the removal of the mode slug entry from the relevant collection(s) in `.ruru/config/build_collections.json` to `prime-dev` via `new_task`. Await completion.

6.  **Run Build Script:**
    *   `prime-coordinator` uses `<execute_command>` to run the build script to update `.roomodes` and the mode summary: `node build_roomodes.js`

7.  **Report Completion:**
    *   `prime-coordinator` reports the successful deletion and configuration updates to the user via `<attempt_completion>`.

**Error Handling:**
*   If user cancels, abort the workflow.
*   If file/directory deletion fails, report error to user.
*   If build script fails, report error to user.

**Notes:**
*   This workflow assumes direct deletion. Consider adding an 'archive' step as an alternative in future versions.
*   Ensure backup/version control is in place before running deletion commands.