# Workflow: Adaptive Project Onboarding

**Goal:** Collaboratively determine project scope (new vs. existing), delegate discovery/requirements gathering, coordinate basic setup, leverage discovery results to guide tech initialization choices, delegate initialization, and report completion to Commander.

**Workflow:**

1.  **Receive Task & Context:** Receive delegation from Roo Commander (Task ID `[Your Task ID]`), including the original user request message (`[initial_request]`). **Action:** Initialize and log goal to `.ruru/tasks/[Your Task ID].md` (Rule `01`).

2.  **Analyze Initial Intent & Context:**
    *   Review `[initial_request]`. Identify keywords indicating "new" vs "existing" project intent. Extract potential `[extracted_name]` or `[extracted_tech]`. Log analysis.
    *   Determine `[project_intent]` ('new', 'existing', or 'unclear').

3.  **Clarify Intent (if `[project_intent]` is 'unclear'):**
    *   Use `ask_followup_question` (Tool) to ask if it's a new or existing project in `{Current Working Directory}`.
    *   **Suggestions:** "🚀 Start a new project.", "📂 Work on an existing project."
    *   Await user response. Store result in `[project_intent]`. Log interaction. Handle cancellation (Error Handling).

4.  **Delegate Discovery (Mandatory):**
    *   Generate Task ID `[Discovery Task ID]` (e.g., TASK-DISC-...).
    *   Log delegation attempt.
    *   Use `new_task` (Tool) to delegate to `agent-context-discovery`:
        ```xml
        <new_task>
          <mode>agent-context-discovery</mode>
          <message>🎯 Project Onboarding Discovery: Intent='[project_intent]'. Analyze based on Initial Request: '[initial_request]'. Goal: Produce Stack Profile (`.ruru/context/stack_profile.json`) and Requirements Doc (`.ruru/docs/requirements.md`). Init log `.ruru/tasks/[Discovery Task ID].md`. Your Task ID: [Discovery Task ID]. Coordinator Task ID: [Your Task ID].</message>
        </new_task>
        ```
    *   **WAIT** for `<attempt_completion>` from `discovery-agent` (Rule `02`).
    *   **Process Result:** Store paths `[stack_profile_path]` and `[requirements_doc_path]`. Log success or handle failure (Error Handling).

5.  **Branch based on `[project_intent]`:**

    *   --- **Path A: New Project (`[project_intent]` = 'new')** ---
        a.  **Confirm/Get Project Name:** Ask user to confirm `[extracted_name]` or provide a `[project_name]`. Use `ask_followup_question` (Tool). Log result. Handle cancellation.
        b.  **Create Core Journal Structure:** Use `execute_command` (Tool) with `mkdir -p ".ruru/tasks/" ... ".ruru/docs/technical_notes/"`. Log action. Handle errors.
        c.  **Initialize Git:** Use `execute_command` (Tool) with `git init`. Log action. Handle errors.
        d.  **Create Basic Files:** Use `write_to_file` (Tool) for `.gitignore` and `README.md` (using `[project_name]`). Log actions. Handle errors.
        e.  **Determine Initialization Strategy (Adaptive):**
            1.  **Read Stack Profile:** Use `read_file` (Tool) on `[stack_profile_path]`.
            2.  **Analyze Stack Profile:** Extract `detected_stack` and `potential_specialists`.
            3.  **Generate Suggestions:** Create a list of `<suggest>` options. Include detected specialists first (e.g., "Delegate to React Specialist (Detected)"), followed by standard fallbacks (Basic HTML + Tailwind/Bootstrap/Vanilla, Core files only, Specify details).
            4.  **Present Prompt:** Use `ask_followup_question` (Tool): "How should we initialize the project structure for '[project_name]'? (Discovery suggested: [List detected tech/specialists if any])". Include the generated suggestions.
            5.  Await user response. Store choice as `[init_choice]`. Log choice. Handle cancellation.
        f.  **Delegate Tech Initialization (If needed):**
            *   If `[init_choice]` requires a specialist: Identify specialist slug. Generate Task ID `[Init Task ID]`. Log delegation. Use `new_task` (Tool): "🚀 Initialize [Tech] structure for '[project_name]' based on discovery ([stack_profile_path], [requirements_doc_path]) and user choice '[init_choice]'. Your Task ID: [Init Task ID]. Log: `.ruru/tasks/[Init Task ID].md`. Coordinator Task ID: [Your Task ID]." **WAIT** for completion (Rule `02`). Log outcome. Handle failure.
            *   Else: Log that no specialist initialization is needed.
        g.  **Delegate Initial Commit:** Generate Task ID `[Git Task ID]`. Log delegation. Use `new_task` (Tool) to delegate to `dev-git`: "💾 Create initial commit for '[project_name]'. Include journal structure, .gitignore, README.md, and any tech init files. Use standard commit message. Your Task ID: [Git Task ID]. Coordinator Task ID: [Your Task ID]." **WAIT** for completion (Rule `02`). Log outcome. Handle failure.
        h.  **Report Completion:** Use `attempt_completion` (Tool) to report back to Roo Commander (see original workflow for example message structure), summarizing discovery, setup, tech init status, and commit status. **End this workflow.**

    *   --- **Path B: Existing Project (`[project_intent]` = 'existing')** ---
        a.  Log start of existing project path.
        b.  **(Discovery already done in Step 4).** Log review of `[stack_profile_path]` and `[requirements_doc_path]`.
        c.  **Check/Create Journal Structure:** Use `list_files` (Tool) to check `.ruru/tasks/`. If not found, explain and use `execute_command` (Tool) with `mkdir -p ...`. Log action. Handle errors.
        d.  **(Optional) Ask for Context Folders:** Use `ask_followup_question` (Tool) to ask user for additional relevant context folder paths. Store response if provided. Log interaction.
        e.  **Report Completion:** Use `attempt_completion` (Tool) to report back to Roo Commander (see original workflow for example message structure), summarizing discovery and setup. **End this workflow.**