+++
id = "KB-MCP-MANAGER-CHECK-UPDATES-V0.1"
title = "KB: Check for MCP Server Updates (Placeholder)"
status = "draft"
created_date = "2025-04-24"
updated_date = "2025-04-24"
version = "0.1"
tags = ["kb", "agent-mcp-manager", "workflow", "mcp", "update", "check", "placeholder"]
owner = "agent-mcp-manager"
related_docs = [
    ".roo/rules-agent-mcp-manager/01-initialization-rule.md",
    ".roo/mcp.json"
    ]
objective = "To define the procedure for checking if installed MCP servers have updates available (e.g., via Git)."
scope = "Executed when the user selects the 'Check for Updates' option from the agent's prompt."
roles = ["Agent (agent-mcp-manager)", "User"]
trigger = "User selection of '🔄 Check for MCP Server Updates'."
success_criteria = ["Agent successfully checks relevant sources (e.g., Git remotes) for updates for installed servers.", "Agent reports findings to the user."]
failure_criteria = ["Agent cannot read `.roo/mcp.json`.", "Agent fails to execute necessary commands (e.g., `git fetch`).", "Agent cannot determine update status."]
+++

# KB Procedure: Check for MCP Server Updates (Placeholder)

## 1. Objective 🎯
Check installed MCP servers (defined in `.roo/mcp.json` and likely residing in `.ruru/mcp-servers/`) for available updates, typically by checking their Git repository status.

## 2. Procedure Steps 🪜

**(Placeholder - To be implemented)**

1.  **Read Configuration:** Use `read_file` to load `.roo/mcp.json`.
2.  **Identify Servers:** Parse the JSON to identify installed servers, paying attention to those likely installed via Git (look for a `source_url` or similar metadata if added during installation, or infer based on directory structure in `.ruru/mcp-servers/`).
3.  **Iterate and Check:** For each relevant server:
    *   Determine its local directory (e.g., `.ruru/mcp-servers/<server-name>`).
    *   Use `execute_command` with the `cwd` parameter set to the server's directory to run `git fetch origin`.
    *   Use `execute_command` (again with `cwd`) to run `git status -uno` or `git log HEAD..origin/main` (or similar, depending on branch conventions) to see if the local branch is behind the remote.
    *   Record the update status for the server.
4.  **Report Findings:** Present a summary of servers checked and their update status to the user using `<attempt_completion>`. Suggest next steps if updates are found (e.g., "Updates found for 'vertex-ai'. Would you like to attempt an update?").

## 3. Rationale / Notes 🤔
*   This procedure assumes servers installed via Git are the primary candidates for updates managed this way.
*   Error handling for Git commands (e.g., repository not found, no remote) needs to be added.
*   A mechanism to actually *apply* the update (e.g., `git pull`) would be a separate KB procedure, likely triggered by user confirmation after this check.