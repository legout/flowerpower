# Workflow for Context Resolver

Follow these steps to handle context queries:

1.  **Receive Query:**
    *   You will be invoked by another mode (e.g., Roo Commander, a Specialist) needing context.
    *   The query should specify the *type* of summary needed (e.g., "current status of TASK-XYZ", "key decisions about database choice") and ideally mention relevant source files/directories if known (e.g., `.ruru/tasks/TASK-XYZ.md`, `.ruru/decisions/`).

2.  **Identify & Prioritize Sources:**
    *   Consult `03-source-prioritization.md` for the standard order of checking sources.
    *   Prioritize specific file paths mentioned in the query.
    *   If only a topic or ID is given, infer the likely path (e.g., `.ruru/tasks/[TaskID].md`, `.ruru/decisions/[ADR-ID].md`).
    *   Consider core planning documents (`.ruru/planning/`) and the stack profile (`.ruru/context/stack_profile.md`) if relevant.
    *   If the query is general, use `list_files` on relevant directories (`.ruru/tasks/`, `.ruru/decisions/`, `.ruru/planning/`, `.ruru/docs/`) to identify candidate files (potentially filtering by name or checking modification times if available).
    *   Check mode-specific context/instructions if the query relates to another mode's capabilities.

3.  **Read Sources:**
    *   Use the `read_file` tool iteratively for each identified source file.
    *   Handle potential errors gracefully (e.g., file not found). Keep track of which requested sources could not be read.

4.  **Synthesize Summary:**
    *   Based *only* on the content successfully read from the sources, construct a concise summary that directly answers the input query.
    *   Use the templates in `05-summary-templates.md` as a guide for structure and formatting.
    *   Employ the standard emojis (🎯 Goal, 📄 Status, 💡 Decision, 🧱 Blocker, ➡️ Next Steps) for clarity.
    *   **Crucially, cite the source file** for each piece of information (e.g., `(from .ruru/decisions/ADR-002.md)`).
    *   Explicitly note any requested or critical source files that could not be read.

5.  **Report Back:**
    *   Use the `attempt_completion` tool to deliver the final, synthesized summary to the mode that initiated the query.
    *   **Do NOT log this action** in the project journal (`.ruru/tasks/`).