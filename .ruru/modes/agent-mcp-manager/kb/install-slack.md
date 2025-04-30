+++
id = "MCP-MGR-KB-INSTALL-SLACK-V1"
title = "Install MCP Server: Slack"
context_type = "knowledge_base"
scope = "Procedure for installing the official Slack MCP server"
target_audience = ["agent-mcp-manager"]
granularity = "procedure"
status = "active"
last_updated = "2025-04-27" # Use current date
tags = ["kb", "mcp", "install", "slack", "communication", "nodejs", "typescript", "api-key"]
related_context = ["README.md"]
template_schema_doc = ".ruru/templates/toml-md/14_kb_entry.md"
relevance = "High: Specific installation guide"
+++

# Procedure: Install MCP Server - Slack

This procedure guides the user through installing the official `slack` server from the `modelcontextprotocol/servers` repository. This server provides tools for interacting with a Slack workspace.

**Source:** <https://github.com/modelcontextprotocol/servers/tree/main/src/slack>

**Prerequisites:**

*   **Node.js:** Latest LTS version recommended. Check with `node --version`.
*   **npm:** Bundled with Node.js. Check with `npm --version`.
*   **Git:** Required for cloning. Check with `git --version`.
*   **Slack App & Credentials:**
    *   Explain a Slack App is needed. Guide user to <https://api.slack.com/apps> -> "Create New App" -> "From scratch".
    *   User needs to select their workspace.
    *   Guide user to "OAuth & Permissions" section.
    *   Instruct user to add the following **Bot Token Scopes**: `channels:history`, `channels:read`, `chat:write`, `reactions:write`, `users:read`. Optionally `users:read.email`.
    *   Instruct user to "Install App to Workspace" and copy the **Bot User OAuth Token** (starts with `xoxb-`).
    *   User needs their **Team ID** (starts with `T`). Suggest finding it via `curl -s -XPOST https://slack.com/api/auth.test -H"Authorization: Bearer ${SLACK_BOT_TOKEN}" | jq .team_id` or other methods if `jq` isn't available.

**Installation & Configuration Steps:**

1.  **Get Slack Credentials:** Ask the user for their Slack Bot Token (`SLACK_BOT_TOKEN`) and Team ID (`SLACK_TEAM_ID`).
2.  **Define Install Directory:** Suggest a standard location for the main repo, e.g., `/home/jez/.local/share/Roo-Code/MCP/mcp-servers-repo`. Confirm with the user or use the default.
3.  **Clone Repository (if not already cloned):**
    *   Check if the target directory exists.
    *   If not, execute cloning:
        ```bash
        git clone https://github.com/modelcontextprotocol/servers.git /home/jez/.local/share/Roo-Code/MCP/mcp-servers-repo
        ```
    *   Confirm success.
4.  **Install Dependencies:**
    *   Navigate to the slack server directory within the cloned repo:
        ```bash
        cd /home/jez/.local/share/Roo-Code/MCP/mcp-servers-repo/src/slack
        ```
    *   Execute dependency installation:
        ```bash
        npm install
        ```
    *   Confirm success.
5.  **Build Server:**
    *   Execute the build command (still in the `src/slack` directory):
        ```bash
        npm run build
        ```
    *   Confirm success. This should create a `dist` directory.
6.  **Determine Configuration:**
    *   `command`: `"node"`
    *   `args`: `["/home/jez/.local/share/Roo-Code/MCP/mcp-servers-repo/src/slack/dist/index.js"]`
    *   `env`: `{ "SLACK_BOT_TOKEN": "<USER_TOKEN>", "SLACK_TEAM_ID": "<USER_TEAM_ID>" }` (Replace placeholders).
7.  **Optional Configuration:** Ask the user if they want to restrict access to specific channels using `SLACK_CHANNEL_IDS` (comma-separated list). If yes, add it to the `env` object.
8.  **Update MCP Settings:**
    *   Read the MCP settings file (`/home/jez/.config/Code/User/globalStorage/rooveterinaryinc.roo-cline/settings/mcp_settings.json`).
    *   Add or update the `slack` server entry within the `mcpServers` object using the determined `command`, `args`, and `env` (replacing placeholders). Ensure `disabled: false` and `alwaysAllow: []` are set.
        ```json
        {
          "mcpServers": {
            // ... other servers ...
            "slack": {
              "command": "node",
              "args": ["/home/jez/.local/share/Roo-Code/MCP/mcp-servers-repo/src/slack/dist/index.js"],
              "env": {
                "SLACK_BOT_TOKEN": "USER_PROVIDED_BOT_TOKEN",
                "SLACK_TEAM_ID": "USER_PROVIDED_TEAM_ID"
                // Add SLACK_CHANNEL_IDS here if provided
              },
              "disabled": false,
              "alwaysAllow": []
            }
          }
        }
        ```
    *   Write the updated content back to the settings file.
9.  **Confirmation:** Inform the user that the `slack` server has been configured and should be available via their MCP client. Suggest refreshing the server list if needed.