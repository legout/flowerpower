# Source Prioritization Guidelines

When resolving context queries, prioritize reading sources in the following order, unless the query explicitly directs otherwise:

1.  **Specific File Paths Provided in Query:** If the query mentions exact file paths (e.g., `.ruru/tasks/TASK-123.md`, `.ruru/decisions/ADR-005.md`), read these first using `read_file`.
2.  **Implied Task/Decision Files:** If the query refers to a specific Task ID or decision topic without a full path, attempt to read the corresponding file in `.ruru/tasks/` or `.ruru/decisions/`.
3.  **Core Planning & Context Documents:** Check for and read key high-level documents if relevant to the query (and if they exist):
    *   `.ruru/planning/project_vision.md`
    *   `.ruru/planning/project_plan.md`
    *   `.ruru/planning/requirements.md`
    *   `.ruru/planning/architecture.md`
    *   `.ruru/context/stack_profile.md`
4.  **Relevant Directory Scan:** If the query is general (e.g., "recent decisions", "status of Feature X tasks"), use `list_files` on the most relevant top-level directory (`.ruru/decisions/`, `.ruru/tasks/`, `.ruru/planning/`, `.ruru/docs/`) and read the most recent or relevant files identified.
5.  **Mode-Specific Context/Instructions:** If the query relates to a specific mode's capabilities or internal knowledge, check for relevant files within that mode's definition directory, particularly its `custom-instructions/` folder (e.g., `v7.1/modes/[classification]/[domain]/[mode-slug]/custom-instructions/`).
6.  **General Documentation:** If necessary and relevant, check standard documentation locations:
    *   `.ruru/docs/standards/`
    *   `.ruru/docs/guides/`
    *   `.ruru/docs/knowledge/`

**General Principles:**

*   **Specificity First:** Always prioritize the most specific sources mentioned or implied by the query.
*   **Recency Often Matters:** For status updates or recent decisions, prioritize files with recent modification dates if available from `list_files`.
*   **Read-Only:** Remember this mode is read-only. Do not attempt to modify any files.
*   **Report Missing Files:** If a requested or highly relevant source file cannot be read (e.g., does not exist), clearly note this limitation in the summary. Do not guess its content. Refer to `06-collaboration-escalation.md` for error handling.