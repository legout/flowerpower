+++
id = "MCP-MGR-KB-INSTALL-CLOUDFLARE-V1"
title = "Install MCP Server: Cloudflare"
context_type = "knowledge_base"
scope = "Procedure for installing the official Cloudflare MCP server"
target_audience = ["agent-mcp-manager"]
granularity = "procedure"
status = "active"
last_updated = "2025-04-27" # Use current date
tags = ["kb", "mcp", "install", "cloudflare", "workers", "wrangler", "npx", "nodejs"]
related_context = ["README.md"]
template_schema_doc = ".ruru/templates/toml-md/14_kb_entry.md"
relevance = "High: Specific installation guide"
+++

# Procedure: Install MCP Server - Cloudflare

This procedure guides the user through installing the official `mcp-server-cloudflare` from Cloudflare. This server provides tools for interacting with Cloudflare resources like Workers, R2, D1, etc.

**Source:** <https://github.com/cloudflare/mcp-server-cloudflare>

**Prerequisites:**

*   **Node.js:** Latest LTS version recommended. Check with `node --version`.
*   **npm:** Bundled with Node.js. Check with `npm --version`.
*   **Cloudflare Account:** User needs an active Cloudflare account.
*   **Cloudflare Account ID:** User needs their Cloudflare Account ID. Guide them to find it on the Cloudflare dashboard (Overview page URL usually contains it).
*   **Wrangler CLI & Login:**
    *   Explain Wrangler is the Cloudflare CLI.
    *   Check if installed: `wrangler --version`. If not, install: `npm install -g wrangler`.
    *   **Crucially**, instruct the user to log in: `npx wrangler login`. The server relies on this authentication.
*   **Cloudflare API Token (Optional but Recommended for `env`):**
    *   Explain an API token might be needed for direct configuration via `env` (less common than Wrangler login).
    *   Guide the user to create one: Cloudflare Dashboard -> My Profile -> API Tokens -> Create Token. Suggest using the "Edit Cloudflare Workers" template or creating a custom token with necessary permissions (e.g., Account.Workers Scripts:Edit, Account.Workers KV Storage:Edit, etc.).
    *   Instruct the user to copy the token securely.

**Installation & Configuration Steps:**

1.  **Confirm Prerequisites:** Verify Node.js, npm, and especially Wrangler login with the user. Ask for their Cloudflare Account ID. Optionally, ask for an API Token if they prefer direct `env` configuration.
2.  **Choose Method:**
    *   **Method A: `npx init` (Recommended for Client Integration like Claude Desktop):**
        *   Execute: `npx @cloudflare/mcp-server-cloudflare init`
        *   Explain this command handles setup and configuration for clients like Claude Desktop, using the existing Wrangler login.
        *   Verify the MCP settings file for the relevant client (e.g., `~/.claude/mcp_config.json`) was updated automatically.
    *   **Method B: Manual Clone & Run (For local execution/testing):**
        *   Define install directory (e.g., `/home/jez/.local/share/Roo-Code/MCP/mcp-server-cloudflare`).
        *   Execute cloning:
            ```bash
            git clone https://github.com/cloudflare/mcp-server-cloudflare.git /home/jez/.local/share/Roo-Code/MCP/mcp-server-cloudflare
            ```
        *   Install dependencies:
            ```bash
            cd /home/jez/.local/share/Roo-Code/MCP/mcp-server-cloudflare && npm install
            ```
        *   Build server:
            ```bash
            npm run build
            ```
        *   Confirm success.
        *   **Determine Configuration for MCP Settings File:**
            *   `command`: `"node"`
            *   `args`: `["/home/jez/.local/share/Roo-Code/MCP/mcp-server-cloudflare/dist/index.js", "run", "<ACCOUNT_ID>"]` (Replace `<ACCOUNT_ID>` placeholder).
            *   `env`: `{}` (Initially empty. Add `CLOUDFLARE_ACCOUNT_ID` and `CLOUDFLARE_API_TOKEN` here if the user provided a token and prefers this over relying solely on Wrangler login).
        *   **Update MCP Settings:**
            *   Read the MCP settings file (`/home/jez/.config/Code/User/globalStorage/rooveterinaryinc.roo-cline/settings/mcp_settings.json`).
            *   Add or update the `cloudflare` server entry using the determined `command`, `args`, and `env` (replacing `<ACCOUNT_ID>` with the user's ID and adding token if provided). Ensure `disabled: false` and `alwaysAllow: []` are set.
                ```json
                {
                  "mcpServers": {
                    // ... other servers ...
                    "cloudflare": {
                      "command": "node",
                      "args": ["/home/jez/.local/share/Roo-Code/MCP/mcp-server-cloudflare/dist/index.js", "run", "USER_ACCOUNT_ID"],
                      "env": {
                        // "CLOUDFLARE_ACCOUNT_ID": "USER_ACCOUNT_ID", // Optional if using token
                        // "CLOUDFLARE_API_TOKEN": "USER_API_TOKEN" // Optional
                      },
                      "disabled": false,
                      "alwaysAllow": []
                    }
                  }
                }
                ```
            *   Write the updated content back to the settings file.
3.  **Confirmation:** Inform the user that the `cloudflare` server has been configured (either via `npx init` or manually) and should be available, relying on their Wrangler login for authentication primarily.