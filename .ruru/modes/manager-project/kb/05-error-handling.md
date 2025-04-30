# Error Handling

*   (This section remains largely the same conceptually)
*   **Error Handling Note:** If delegated tasks fail (reported via specialist's `attempt_completion`), analyze the failure report. Update the corresponding MDTM task file's `status` in the **TOML block** to `"⚪ Blocked"` or revert it, adding notes in the Markdown body. Log the failure/blocker in your PM log and report it to Roo Commander. Handle tool failures similarly.