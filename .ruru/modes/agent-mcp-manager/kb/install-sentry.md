+++
id = "MCP-MGR-KB-INSTALL-SENTRY-V1"
title = "Install MCP Server: Sentry"
context_type = "knowledge_base"
scope = "Procedure for installing the official Sentry MCP server"
target_audience = ["agent-mcp-manager"]
granularity = "procedure"
status = "active"
last_updated = "2025-04-27" # Use current date
tags = ["kb", "mcp", "install", "sentry", "monitoring", "errors", "nodejs", "typescript", "api-key"]
related_context = ["README.md"]
template_schema_doc = ".ruru/templates/toml-md/14_kb_entry.md"
relevance = "High: Specific installation guide"
+++

# Procedure: Install MCP Server - Sentry

This procedure guides the user through installing the official `sentry` server from the `modelcontextprotocol/servers` repository. This server provides tools for interacting with the Sentry error tracking service.

**Source:** <https://github.com/modelcontextprotocol/servers/tree/main/src/sentry>

**Prerequisites:**

*   **Node.js:** Version 14+ recommended. Check with `node --version`.
*   **npm:** Bundled with Node.js. Check with `npm --version`.
*   **Git:** Required for cloning. Check with `git --version`.
*   **Sentry Auth Token:**
    *   Explain that a Sentry API Auth Token (Personal Access Token) is required.
    *   Guide the user to create one in their Sentry settings: User Settings -> Auth Tokens -> Create New Token.
    *   Instruct them to grant necessary scopes (e.g., `org:read`, `project:read`, `project:write`, `event:read`).
    *   Instruct the user to copy the generated token securely.
*   **Sentry Org/Project Slugs (Optional):** User might need their organization slug and project slug(s) if they want to scope the server's access. These are usually visible in Sentry URLs.

**Installation & Configuration Steps:**

1.  **Get Sentry Credentials:** Ask the user for their Sentry Auth Token (`SENTRY_AUTH_TOKEN`). Optionally, ask for organization (`SENTRY_ORGANIZATION_SLUG`) and project slugs (`SENTRY_PROJECT_SLUG` or comma-separated `SENTRY_PROJECT_NAMES` depending on implementation). Also ask for `SENTRY_BASE_URL` if using self-hosted Sentry.
2.  **Define Install Directory:** Suggest a standard location for the main repo, e.g., `/home/jez/.local/share/Roo-Code/MCP/mcp-servers-repo`. Confirm with the user or use the default.
3.  **Clone Repository (if not already cloned):**
    *   Check if the target directory exists.
    *   If not, execute cloning:
        ```bash
        git clone https://github.com/modelcontextprotocol/servers.git /home/jez/.local/share/Roo-Code/MCP/mcp-servers-repo
        ```
    *   Confirm success.
4.  **Install Dependencies:**
    *   Navigate to the sentry server directory within the cloned repo:
        ```bash
        cd /home/jez/.local/share/Roo-Code/MCP/mcp-servers-repo/src/sentry
        ```
    *   Execute dependency installation:
        ```bash
        npm install
        ```
    *   Confirm success.
5.  **Build Server:**
    *   Execute the build command (still in the `src/sentry` directory):
        ```bash
        npm run build
        ```
    *   Confirm success. This should create a `dist` directory.
6.  **Determine Configuration:**
    *   `command`: `"node"`
    *   `args`: `["/home/jez/.local/share/Roo-Code/MCP/mcp-servers-repo/src/sentry/dist/index.js"]`
    *   `env`: Build this object based on user input from Step 1. `SENTRY_AUTH_TOKEN` is required.
        ```json
        {
          "SENTRY_AUTH_TOKEN": "<USER_TOKEN>",
          // "SENTRY_ORGANIZATION_SLUG": "<USER_ORG_SLUG>", // Optional
          // "SENTRY_PROJECT_SLUG": "<USER_PROJECT_SLUG>", // Optional
          // "SENTRY_BASE_URL": "<USER_SENTRY_URL>" // Optional, defaults to sentry.io
        }
        ```
7.  **Update MCP Settings:**
    *   Read the MCP settings file (`/home/jez/.config/Code/User/globalStorage/rooveterinaryinc.roo-cline/settings/mcp_settings.json`).
    *   Add or update the `sentry` server entry within the `mcpServers` object using the determined `command`, `args`, and `env` (replacing placeholders). Ensure `disabled: false` and `alwaysAllow: []` are set.
        ```json
        {
          "mcpServers": {
            // ... other servers ...
            "sentry": {
              "command": "node",
              "args": ["/home/jez/.local/share/Roo-Code/MCP/mcp-servers-repo/src/sentry/dist/index.js"],
              "env": {
                "SENTRY_AUTH_TOKEN": "USER_PROVIDED_AUTH_TOKEN"
                // Add optional Sentry vars here if provided
              },
              "disabled": false,
              "alwaysAllow": []
            }
          }
        }
        ```
    *   Write the updated content back to the settings file.
8.  **Confirmation:** Inform the user that the `sentry` server has been configured and should be available via their MCP client. Suggest refreshing the server list if needed. Mention they can debug using `npx @modelcontextprotocol/inspector node dist/index.js`.