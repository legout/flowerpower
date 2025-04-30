# Initial Actions Knowledge Base (`.ruru/modes/roo-commander/kb/initial-actions/`)

This directory contains specific Knowledge Base (KB) procedure files detailing how the `roo-commander` mode should handle each of the primary starting options presented to the user during the initial interaction workflow (defined in `.roo/rules-roo-commander/02-initialization-workflow-rule.md`).

## Purpose

Each file in this directory outlines the specific steps, user prompts, and delegations required for Roo Commander to initiate a particular workflow based on the user's chosen starting point. This modular approach keeps the main initialization rule concise while providing detailed, maintainable procedures for each distinct action.

## KB Files

1.  **`01-start-new-project.md`**: Procedure for handling the "Start a NEW project from scratch" option, confirming intent and delegating to `manager-onboarding`.
2.  **`02-onboard-existing-project.md`**: Procedure for handling the "Analyze/Onboard the CURRENT project workspace" option, confirming intent and delegating to `manager-onboarding`.
3.  **`03-clone-onboard.md`**: Procedure for handling the "Clone a Git repository & onboard" option, including prompting for URL, delegating clone to `dev-git`, and then delegating onboarding to `manager-onboarding`.
4.  **`04-use-existing-files.md`**: Procedure for handling the "Use existing project files/plans..." option, prompting for file paths and delegating to `manager-onboarding` with the file context.
5.  **`05-plan-design.md`**: Procedure for handling the "Plan/Design a new feature or project" option, clarifying focus (technical vs. product) and delegating to `core-architect` or `manager-product`.
6.  **`06-fix-bug.md`**: Procedure for handling the "Fix a specific bug" option, gathering initial details and delegating to `dev-fixer`.
7.  **`07-refactor-code.md`**: Procedure for handling the "Refactor or improve existing code" option, gathering target/goals and delegating to `util-refactor`.
8.  **`08-write-docs.md`**: Procedure for handling the "Write or update documentation" option, gathering requirements and delegating to `util-writer`.
9.  **`09-review-status.md`**: Procedure for handling the "Review project status / Manage tasks (MDTM)" option, determining context (MDTM vs. general) and delegating to `manager-project` or `agent-context-resolver`.
10. **`10-research-topic.md`**: Procedure for handling the "Research a topic / Ask a technical question" option, gathering the query and delegating to `agent-research`.
11. **`11-execute-delegate.md`**: Procedure for handling the "Execute a command / Delegate a specific known task" option, performing safety checks for commands or validating/delegating direct tasks.
12. **`12-manage-config.md`**: Procedure for handling the "Manage Roo Configuration (Advanced)" option, gathering the change request and delegating safely to `prime-coordinator`.
13. **`13-update-preferences.md`**: Procedure for handling the "Update my preferences / profile" option, gathering changes and delegating the update of `00-user-preferences.md` to `prime-coordinator`.
14. **`14-learn-capabilities.md`**: Procedure for handling the "Learn about Roo Commander capabilities" option, retrieving and presenting the mode summary.
15. **`15-join-community.md`**: Procedure for handling the "Join the Roo Commander Community (Discord)" option, presenting community info and the Discord link.
16. **`16-something-else.md`**: Procedure for handling the "Something else..." fallback option, prompting for a clearer goal and re-analyzing intent.

**Usage:** The main initialization rule (`.roo/rules-roo-commander/02-...`) directs Roo Commander to execute the specific procedure contained within the relevant file based on the user's selection.