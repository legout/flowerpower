+++
id = "KB-ROO-CMD-INIT-ACTION-00-INSTALL-MCP-V1"
title = "KB: Initial Action - Install/Manage MCP Servers"
status = "active"
created_date = "2025-04-24"
updated_date = "2025-04-24"
version = "1.0"
tags = ["kb", "roo-commander", "initial-action", "mcp", "install", "delegate"]
owner = "Roo Commander"
related_docs = [
    ".roo/rules-roo-commander/02-initialization-workflow-rule.md",
    ".ruru/modes/agent-mcp-manager/agent-mcp-manager.mode.md"
    ]
objective = "To delegate the task of installing or managing MCP servers to the specialized agent."
scope = "Executed when the user selects Option 0 from the Roo Commander initial prompt."
roles = ["Coordinator (Roo Commander)"]
trigger = "User selection of '🔌 Install/Manage MCP Servers'."
success_criteria = ["Task successfully delegated to `agent-mcp-manager`."]
failure_criteria = ["Delegation using `new_task` fails."]
+++

# KB Procedure: Initial Action - Install/Manage MCP Servers

## 1. Objective 🎯
Delegate the interactive process of installing or managing MCP servers to the `agent-mcp-manager` mode.

## 2. Procedure Steps 🪜

1.  **Log Action:** Log the user's selection of Option 0.
2.  **Delegate Task:** Use the `new_task` tool to delegate the task to the `agent-mcp-manager`.
    *   **Tool:** `new_task`
    *   **Parameters:**
        *   `mode`: `agent-mcp-manager`
        *   `message`: "Initiate MCP server installation/management process."
3.  **Monitor:** Await completion or further interaction requests from the `agent-mcp-manager` mode (Rule `04`).

## 3. Rationale / Notes 🤔
This action serves as a simple routing mechanism from the main Roo Commander initialization flow to the dedicated agent responsible for handling MCP server installation and management.