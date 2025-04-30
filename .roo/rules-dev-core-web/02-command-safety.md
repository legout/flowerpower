+++
# --- Basic Metadata ---
id = "RULE-COREWEB-CMD-SAFETY-V1"
title = "Core Web Developer: Command Execution Safety"
context_type = "rules"
scope = "Guidelines for using the execute_command tool safely"
target_audience = ["dev-core-web"]
granularity = "guideline"
status = "active"
last_updated = "2025-04-22"
tags = ["rules", "safety", "commands", "execute_command", "dev-core-web", "worker"]
related_context = [
    ".roo/rules/05-os-aware-commands.md", # Workspace OS awareness rule
    ".roo/rules-roo-commander/07-safety-protocols-rule.md" # General safety concept
    ]
template_schema_doc = ".ruru/templates/toml-md/16_ai_rule.README.md"
relevance = "Medium: Applies if the mode uses execute_command"
+++

# Rule: Command Execution Safety

When using the `<execute_command>` tool (e.g., for running linters, formatters, or basic build steps):

1.  **Clarity:** Ensure the command you intend to run is clear, specific, and directly related to your assigned task.
2.  **Explain:** Briefly explain the purpose of the command before executing it.
3.  **OS Awareness:** Generate OS-aware commands based on `environment_details.os` (See Rule `.roo/rules/05-os-aware-commands.md`).
4.  **Non-Destructive Preference:** Prioritize commands that are non-destructive (e.g., `npm run lint`, `npm run format`, `npm run build --dry-run`).
5.  **Avoid Risky Commands:** Do **not** execute potentially destructive commands (e.g., `rm -rf`, Git commands altering history, disk formatting commands) unless explicitly instructed and confirmed by the user/coordinator via `ask_followup_question` (as per general safety protocols).
6.  **Working Directory:** Specify the `cwd` parameter if the command needs to run in a specific subdirectory. Default is the workspace root.
7.  **Error Handling:** Analyze output and non-zero exit codes. Report errors clearly when completing the task or if blocked.