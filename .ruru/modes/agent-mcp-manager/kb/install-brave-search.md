+++
id = "MCP-MGR-KB-INSTALL-BRAVE-SEARCH-V1"
title = "Install MCP Server: Brave Search"
context_type = "knowledge_base"
scope = "Procedure for installing the Brave Search MCP server"
target_audience = ["agent-mcp-manager"]
granularity = "procedure"
status = "active"
last_updated = "2025-04-27" # Use current date
tags = ["kb", "mcp", "install", "brave", "search", "npx", "nodejs", "api-key"]
related_context = ["README.md"]
template_schema_doc = ".ruru/templates/toml-md/14_kb_entry.md"
relevance = "High: Specific installation guide"
+++

# Procedure: Install MCP Server - Brave Search

This procedure guides the user through installing the `brave-search` server from the Model Context Protocol organization. This server provides tools for interacting with the Brave Search API.

**Source:** <https://github.com/modelcontextprotocol/servers/tree/main/src/brave-search> (Package: `@modelcontextprotocol/server-brave-search`)

**Prerequisites:**

*   **Node.js:** Latest LTS version recommended. Check with `node --version`.
*   **npm:** Bundled with Node.js. Check with `npm --version`.
*   **Brave Search API Key:**
    *   Explain that an API key is required.
    *   Guide the user to obtain one (free tier available) from the Brave Search API website: <https://brave.com/search/api/>
    *   Instruct the user to copy the generated API key.

**Installation & Configuration Steps:**

1.  **Get API Key:** Ask the user to provide the `BRAVE_API_KEY` they obtained.
2.  **Determine Configuration (using `npx`):**
    *   The recommended method uses `npx` directly in the client configuration.
    *   `command`: `"npx"`
    *   `args`: `["-y", "@modelcontextprotocol/server-brave-search"]`
    *   `env`: `{ "BRAVE_API_KEY": "<USER_KEY>" }` (Replace `<USER_KEY>` placeholder).
3.  **Update MCP Settings:**
    *   Read the MCP settings file (`/home/jez/.config/Code/User/globalStorage/rooveterinaryinc.roo-cline/settings/mcp_settings.json`).
    *   Add or update the `brave-search` server entry within the `mcpServers` object using the determined `command`, `args`, and `env` (replacing `<USER_KEY>` with the actual key). Ensure `disabled: false` and `alwaysAllow: []` are set.
        ```json
        {
          "mcpServers": {
            // ... other servers ...
            "brave-search": {
              "command": "npx",
              "args": [
                "-y",
                "@modelcontextprotocol/server-brave-search"
              ],
              "env": {
                "BRAVE_API_KEY": "USER_PROVIDED_API_KEY"
              },
              "disabled": false,
              "alwaysAllow": []
            }
          }
        }
        ```
    *   Write the updated content back to the settings file.
4.  **Confirmation:** Inform the user that the `brave-search` server has been configured and should be available via their MCP client. Suggest refreshing the server list if needed.