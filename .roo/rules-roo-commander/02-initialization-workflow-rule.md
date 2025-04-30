+++
id = "ROO-CMD-RULE-INIT-V5" # Incremented version
title = "Roo Commander: Rule - Initial Request Processing & Mode Management" # Updated title
context_type = "rules"
scope = "Initial user interaction handling, presenting comprehensive starting options and routing to specific KB procedures"
target_audience = ["roo-commander"]
granularity = "procedure"
status = "active"
last_updated = "2025-04-27" # Use current date
tags = ["rules", "workflow", "initialization", "onboarding", "intent", "options", "kb-routing", "roo-commander", "mode-management"] # Added tag
related_context = [
    "01-operational-principles.md",
    # Specific KB Action files
    ".ruru/modes/roo-commander/kb/initial-actions/00-install-mcp.md", # Added MCP Install option
    ".ruru/modes/roo-commander/kb/initial-actions/01-start-new-project.md",
    ".ruru/modes/roo-commander/kb/initial-actions/02-onboard-existing-project.md",
    ".ruru/modes/roo-commander/kb/initial-actions/03-clone-onboard.md",
    ".ruru/modes/roo-commander/kb/initial-actions/04-use-existing-files.md",
    ".ruru/modes/roo-commander/kb/initial-actions/05-plan-design.md",
    ".ruru/modes/roo-commander/kb/initial-actions/06-fix-bug.md",
    ".ruru/modes/roo-commander/kb/initial-actions/07-refactor-code.md",
    ".ruru/modes/roo-commander/kb/initial-actions/08-write-docs.md",
    ".ruru/modes/roo-commander/kb/initial-actions/09-review-status.md",
    ".ruru/modes/roo-commander/kb/initial-actions/10-research-topic.md",
    ".ruru/modes/roo-commander/kb/initial-actions/11-execute-delegate.md",
    ".ruru/modes/roo-commander/kb/initial-actions/12-manage-config.md",
    ".ruru/modes/roo-commander/kb/initial-actions/13-update-preferences.md",
    ".ruru/modes/roo-commander/kb/initial-actions/14-learn-capabilities.md",
    ".ruru/modes/roo-commander/kb/initial-actions/15-join-community.md",
    ".ruru/modes/roo-commander/kb/initial-actions/16-something-else.md",
    # Option 17 now handles Mode Management
    # Key delegate modes
    "manager-onboarding",
    "dev-git",
    "core-architect",
    "manager-product",
    "agent-research",
    "prime-coordinator",
    "dev-fixer",
    "util-refactor",
    "util-writer"
    ]
template_schema_doc = ".ruru/templates/toml-md/16_ai_rule.README.md"
relevance = "Critical: Defines the entry point for user interaction and routes to specific procedures"
+++

# Rule: Initial Request Processing (Explicit KB Routing)

This rule governs how you handle the **first user message** in a session, presenting a comprehensive list of starting options to clarify intent and initiate the correct workflow by executing procedures defined in specific Knowledge Base (KB) files.

**Standard Initial Prompt (if needed):**

```xml
 <ask_followup_question>
  <question>Welcome to Roo Commander v7 (Wallaby)! How can I assist you today?</question>
  <follow_up>
    <suggest>🔌 Install/Manage MCP Servers</suggest> <!-- Option 0 -->
    <suggest>🎩 Start a NEW project from scratch</suggest> <!-- Option 1 -->
    <suggest>📂 Analyze/Onboard the CURRENT project workspace</suggest> <!-- Option 2 -->
    <suggest>🌐 Clone a Git repository & onboard</suggest> <!-- Option 3 -->
    <suggest>🗃️ Use existing project files/plans to define the work</suggest> <!-- Option 4 -->
    <suggest>📑 Plan/Design a new feature or project</suggest> <!-- Option 5 -->
    <suggest>🐞 Fix a specific bug</suggest> <!-- Option 6 -->
    <suggest>♻️ Refactor or improve existing code</suggest> <!-- Option 7 -->
    <suggest>✍️ Write or update documentation</suggest> <!-- Option 8 -->
    <suggest>📟 Review project status / Manage tasks (MDTM)</suggest> <!-- Option 9 -->
    <suggest>❓ Research a topic / Ask a technical question</suggest> <!-- Option 10 -->
    <suggest>🎺 Execute a command / Delegate a specific known task</suggest> <!-- Option 11 -->
    <suggest>🪃 Manage Roo Configuration (Advanced)</suggest> <!-- Option 12 -->
    <suggest>🖲️ Update my preferences / profile</suggest> <!-- Option 13 -->
    <suggest>🦘 Learn about Roo Commander capabilities</suggest> <!-- Option 14 -->
    <suggest>🐾 Join the Roo Commander Community (Discord)</suggest> <!-- Option 15 -->
    <suggest>🤔 Something else... (Describe your goal)</suggest> <!-- Option 16 -->
    <suggest>🧑‍🎨 Mode Management</suggest> <!-- Option 17 -->
  </follow_up>
 </ask_followup_question>```

**Procedure:**

1.  **Analyze Initial User Request:**
    *   Check for explicit mode switch requests ("switch to `[mode-slug]`").
    *   Briefly analyze keywords if the user states a goal directly.

2.  **Determine Response Path:**

    *   **A. Direct Mode Request:**
        *   If user explicitly requests switching to a specific mode: Confirm understanding and attempt `<switch_mode> [mode-slug]`. Log action (Rule `08`). **End this workflow.**

    *   **B. Direct Goal Stated (High Confidence - Non-Onboarding):**
        *   If the user's first message clearly states a goal that confidently maps to a specific action *other than onboarding/setup* (e.g., "fix bug 123", "refactor `userService.js`"):
            1.  Acknowledge the goal.
            2.  Propose the most relevant specialist mode via `ask_followup_question`.
            3.  Include suggestions: `<suggest>Yes, use [Proposed Mode]</suggest>`, `<suggest>No, let me choose from all starting options</suggest>`.
            4.  If "Yes", proceed to standard delegation (Rule `03`). Log action. **End this workflow.**
            5.  If "No", proceed to **Path C**.

    *   **C. All Other Cases (Default Path):**
        *   Includes: Vague requests, requests for help/options, requests initially mentioning "new project" or "onboard existing", or user selecting "No" in Path B.
        *   **Action:** Present the **Standard Initial Prompt** (defined above) using `<ask_followup_question>`.
        *   Await user's selection. Proceed to Step 3.

3.  **Handle User Selection (from Standard Initial Prompt):**
    *   Once the user selects an option (identified 0-16) from the standard prompt:
        1.  Identify the selected option number.
        2.  Log the chosen starting path (Rule `08`).
        3.  **Execute the detailed procedure defined in the corresponding KB file**:
            *   Option 0: Execute KB `.ruru/modes/roo-commander/kb/initial-actions/00-install-mcp.md`.
            *   Option 1: Execute KB `.ruru/modes/roo-commander/kb/initial-actions/01-start-new-project.md`.
            *   Option 2: Execute KB `.ruru/modes/roo-commander/kb/initial-actions/02-onboard-existing-project.md`.
            *   Option 3: Execute KB `.ruru/modes/roo-commander/kb/initial-actions/03-clone-onboard.md`.
            *   Option 4: Execute KB `.ruru/modes/roo-commander/kb/initial-actions/04-use-existing-files.md`.
            *   Option 5: Execute KB `.ruru/modes/roo-commander/kb/initial-actions/05-plan-design.md`.
            *   Option 6: Execute KB `.ruru/modes/roo-commander/kb/initial-actions/06-fix-bug.md`.
            *   Option 7: Execute KB `.ruru/modes/roo-commander/kb/initial-actions/07-refactor-code.md`.
            *   Option 8: Execute KB `.ruru/modes/roo-commander/kb/initial-actions/08-write-docs.md`.
            *   Option 9: Execute KB `.ruru/modes/roo-commander/kb/initial-actions/09-review-status.md`.
            *   Option 10: Execute KB `.ruru/modes/roo-commander/kb/initial-actions/10-research-topic.md`.
            *   Option 11: Execute KB `.ruru/modes/roo-commander/kb/initial-actions/11-execute-delegate.md`.
            *   Option 12: Execute KB `.ruru/modes/roo-commander/kb/initial-actions/12-manage-config.md`.
            *   Option 13: Execute KB `.ruru/modes/roo-commander/kb/initial-actions/13-update-preferences.md`.
            *   Option 14: Execute KB `.ruru/modes/roo-commander/kb/initial-actions/14-learn-capabilities.md`.
            *   Option 15: Execute KB `.ruru/modes/roo-commander/kb/initial-actions/15-join-community.md`.
            *   Option 16 ("Something else"): Execute KB `.ruru/modes/roo-commander/kb/initial-actions/16-something-else.md`.
            *   Option 17 ("Mode Management"): Present the user with the following choices and initiate the corresponding workflow:
                *   Create New Mode (`.ruru/workflows/WF-NEW-MODE-CREATION-004.md`)
                *   Mode KB Enrichment with Vertex AI MCP (`.ruru/workflows/WF-MODE-KB-ENRICHMENT-002.md`)
                *   Mode KB Enrichment with Context7 (`.ruru/workflows/WF-CONTEXT7-ENRICHMENT-001.md`)
                *   Mode KB Refresh with Context 7 (`.ruru/workflows/WF-CONTEXT7-REFRESH-001.md`)
                *   Delete Modes (Note: Workflow needs creation)
        4.  Follow the steps within the chosen KB procedure or subsequent workflow, including any user interaction or delegation it defines. **End this initialization workflow** upon completion of the KB procedure or delegated workflow.

**Key Objective:** To provide clear starting options and route the user interaction to the precise, detailed procedure stored in the relevant Knowledge Base file or subsequent workflow, ensuring consistent handling for each initial user intention, including mode management tasks.