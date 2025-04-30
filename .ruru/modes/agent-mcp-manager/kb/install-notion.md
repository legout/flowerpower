+++
id = "MCP-MGR-KB-INSTALL-NOTION-V1"
title = "Install MCP Server: Notion"
context_type = "knowledge_base"
scope = "Procedure for installing the Notion MCP server"
target_audience = ["agent-mcp-manager"]
granularity = "procedure"
status = "active"
last_updated = "2025-04-27" # Use current date
tags = ["kb", "mcp", "install", "notion", "notes", "database", "nodejs", "typescript", "api-key"]
related_context = ["README.md"]
template_schema_doc = ".ruru/templates/toml-md/14_kb_entry.md"
relevance = "High: Specific installation guide"
+++

# Procedure: Install MCP Server - Notion

This procedure guides the user through installing the `notion-mcp-server` from makenotion. This server provides tools for interacting with Notion databases and pages.

**Source:** <https://github.com/makenotion/notion-mcp-server>

**Prerequisites:**

*   **Node.js:** Version 18+ recommended. Check with `node --version`.
*   **npm:** Bundled with Node.js. Check with `npm --version`.
*   **Git:** Required for cloning. Check with `git --version`.
*   **Notion API Key (Internal Integration Token):**
    *   Explain that a Notion integration token is required.
    *   Guide the user to create an internal integration: <https://www.notion.so/my-integrations> -> "New integration".
    *   Name the integration (e.g., "MCP Server").
    *   Select the associated workspace.
    *   Under Capabilities, ensure "Read content", "Update content", and "Insert content" are checked. "Read user information including email addresses" might be needed depending on tools.
    *   Submit and copy the **Internal Integration Token** (starts with `secret_`).
*   **Notion Database ID (Optional but Recommended):**
    *   Explain that providing a Database ID scopes the server's access.
    *   Guide the user to open the target Notion database as a full page in their browser. The Database ID is the string between the last `/` and the `?` in the URL (e.g., `https://www.notion.so/your-workspace/DATABASE_ID?v=...`).
    *   Instruct the user to copy this ID.
*   **Share Integration with Database/Pages:** The user MUST share the specific databases or pages they want the server to access with the created Notion integration (via the "Share" menu in Notion).

**Installation & Configuration Steps:**

1.  **Get Notion Credentials:** Ask the user for their Notion Internal Integration Token (`NOTION_API_KEY`). Optionally, ask for the specific Database ID (`NOTION_DATABASE_ID`) they want to primarily interact with.
2.  **Define Install Directory:** Suggest a standard location, e.g., `/home/jez/.local/share/Roo-Code/MCP/notion-mcp-server`. Confirm with the user or use the default.
3.  **Clone Repository:**
    *   Execute cloning:
        ```bash
        git clone https://github.com/makenotion/notion-mcp-server.git /home/jez/.local/share/Roo-Code/MCP/notion-mcp-server
        ```
    *   Confirm success.
4.  **Install Dependencies:**
    *   Navigate to the server directory:
        ```bash
        cd /home/jez/.local/share/Roo-Code/MCP/notion-mcp-server
        ```
    *   Execute dependency installation:
        ```bash
        npm install
        ```
    *   Confirm success.
5.  **Build Server:**
    *   Execute the build command:
        ```bash
        npm run build
        ```
    *   Confirm success. This should create a `dist` directory.
6.  **Determine Configuration:**
    *   `command`: `"node"`
    *   `args`: `["/home/jez/.local/share/Roo-Code/MCP/notion-mcp-server/dist/index.js"]`
    *   `env`: Build this object based on user input from Step 1. `NOTION_API_KEY` is required.
        ```json
        {
          "NOTION_API_KEY": "<USER_TOKEN>",
          // "NOTION_DATABASE_ID": "<USER_DB_ID>" // Optional
        }
        ```
7.  **Update MCP Settings:**
    *   Read the MCP settings file (`/home/jez/.config/Code/User/globalStorage/rooveterinaryinc.roo-cline/settings/mcp_settings.json`).
    *   Add or update the `notion` server entry within the `mcpServers` object using the determined `command`, `args`, and `env` (replacing placeholders). Ensure `disabled: false` and `alwaysAllow: []` are set.
        ```json
        {
          "mcpServers": {
            // ... other servers ...
            "notion": {
              "command": "node",
              "args": ["/home/jez/.local/share/Roo-Code/MCP/notion-mcp-server/dist/index.js"],
              "env": {
                "NOTION_API_KEY": "USER_PROVIDED_API_KEY"
                // Add NOTION_DATABASE_ID here if provided
              },
              "disabled": false,
              "alwaysAllow": []
            }
          }
        }
        ```
    *   Write the updated content back to the settings file.
8.  **Confirmation:** Inform the user that the `notion` server has been configured and should be available via their MCP client. Remind them they need to share relevant Notion pages/databases with the integration. Suggest refreshing the server list if needed.