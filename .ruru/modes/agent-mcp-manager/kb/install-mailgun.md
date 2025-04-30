+++
id = "MCP-MGR-KB-INSTALL-MAILGUN-V1"
title = "Install MCP Server: Mailgun"
context_type = "knowledge_base"
scope = "Procedure for installing the official Mailgun MCP server"
target_audience = ["agent-mcp-manager"]
granularity = "procedure"
status = "active"
last_updated = "2025-04-27" # Use current date
tags = ["kb", "mcp", "install", "mailgun", "email", "nodejs", "api-key"]
related_context = ["README.md"]
template_schema_doc = ".ruru/templates/toml-md/14_kb_entry.md"
relevance = "High: Specific installation guide"
+++

# Procedure: Install MCP Server - Mailgun

This procedure guides the user through installing the official `mailgun-mcp-server` from Mailgun. This server provides tools for interacting with the Mailgun email service API.

**Source:** <https://github.com/mailgun/mailgun-mcp-server>

**Prerequisites:**

*   **Node.js:** Version 18+ recommended. Check with `node --version`.
*   **npm:** Bundled with Node.js. Check with `npm --version`.
*   **Git:** Required for cloning. Check with `git --version`.
*   **Mailgun Account & API Key:**
    *   Explain that a Mailgun API key is required.
    *   Guide the user to their Mailgun account settings (API Keys section) to find or create an API key.
    *   Instruct the user to copy the API key securely.

**Installation & Configuration Steps:**

1.  **Get API Key:** Ask the user to provide the `MAILGUN_API_KEY` they obtained.
2.  **Define Install Directory:** Suggest a standard location, e.g., `/home/jez/.local/share/Roo-Code/MCP/mailgun-mcp-server`. Confirm with the user or use the default.
3.  **Clone Repository:**
    *   Execute cloning:
        ```bash
        git clone https://github.com/mailgun/mailgun-mcp-server.git /home/jez/.local/share/Roo-Code/MCP/mailgun-mcp-server
        ```
    *   Confirm success.
4.  **Install Dependencies:**
    *   Navigate to the server directory:
        ```bash
        cd /home/jez/.local/share/Roo-Code/MCP/mailgun-mcp-server
        ```
    *   Execute dependency installation:
        ```bash
        npm install
        ```
    *   Confirm success. (Note: No explicit build step like `npm run build` is mentioned in the primary source README for running).
5.  **Determine Configuration:**
    *   `command`: `"node"`
    *   `args`: `["/home/jez/.local/share/Roo-Code/MCP/mailgun-mcp-server/src/mailgun-mcp.js"]` (Using the path to the main script).
    *   `env`: `{ "MAILGUN_API_KEY": "<USER_KEY>" }` (Replace `<USER_KEY>` placeholder).
6.  **Update MCP Settings:**
    *   Read the MCP settings file (`/home/jez/.config/Code/User/globalStorage/rooveterinaryinc.roo-cline/settings/mcp_settings.json`).
    *   Add or update the `mailgun` server entry within the `mcpServers` object using the determined `command`, `args`, and `env` (replacing `<USER_KEY>` with the actual key). Ensure `disabled: false` and `alwaysAllow: []` are set.
        ```json
        {
          "mcpServers": {
            // ... other servers ...
            "mailgun": {
              "command": "node",
              "args": ["/home/jez/.local/share/Roo-Code/MCP/mailgun-mcp-server/src/mailgun-mcp.js"],
              "env": {
                "MAILGUN_API_KEY": "USER_PROVIDED_API_KEY"
              },
              "disabled": false,
              "alwaysAllow": []
            }
          }
        }
        ```
    *   Write the updated content back to the settings file.
7.  **Confirmation:** Inform the user that the `mailgun` server has been configured and should be available via their MCP client. Mention they can test with `NODE_ENV=test npm test` in the server directory.