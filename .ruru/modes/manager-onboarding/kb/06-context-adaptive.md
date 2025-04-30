# Context & Knowledge Base (Adaptive)

*   **Required Inputs:**
    *   Task ID (`[Your Task ID]`) from Coordinator.
    *   Initial User Request (`[initial_request]`) from Coordinator.
*   **Key Outputs (Generated or Delegated):**
    *   Stack Profile Path (`[stack_profile_path]`, e.g., `.ruru/context/stack_profile.json` or `.md`) - Output from `agent-context-discovery`.
    *   Requirements Doc Path (`[requirements_doc_path]`, e.g., `.ruru/docs/requirements.md`) - Output from `agent-context-discovery`.
    *   Project Name (`[project_name]`) - Confirmed with User.
    *   Initialization Choice (`[init_choice]`) - Selected by User.
*   **Key Files Used/Created:**
    *   Own Task Log (`.ruru/tasks/[Your Task ID].md`).
    *   `.gitignore` (Created for new projects).
    *   `README.md` (Created for new projects).
    *   `.ruru/` subdirectories (tasks, docs, etc. - created for new projects or verified for existing).
*   **Key Reference:** Own workflow document (`02-workflow-adaptive.md`).