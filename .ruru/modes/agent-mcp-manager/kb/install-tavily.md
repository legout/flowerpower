+++
id = "MCP-MGR-KB-INSTALL-TAVILY-V1"
title = "Install MCP Server: Tavily"
context_type = "knowledge_base"
scope = "Procedure for installing the Tavily MCP server"
target_audience = ["agent-mcp-manager"]
granularity = "procedure"
status = "active"
last_updated = "2025-04-27" # Use current date
tags = ["kb", "mcp", "install", "tavily", "search", "research", "npx", "nodejs", "api-key"]
related_context = ["README.md"]
template_schema_doc = ".ruru/templates/toml-md/14_kb_entry.md"
relevance = "High: Specific installation guide"
+++

# Procedure: Install MCP Server - Tavily

This procedure guides the user through installing the `tavily-mcp` server from Tavily AI. This server provides advanced search and research capabilities.

**Source:** <https://github.com/tavily-ai/tavily-mcp>

**Prerequisites:**

*   **Node.js:** Version 20+ recommended. Check with `node --version`.
*   **Tavily API Key:**
    *   Explain that an API key is required.
    *   Guide the user to sign up and obtain one from the Tavily dashboard: <https://app.tavily.com/home>
    *   Instruct the user to copy the generated API key.

**Installation & Configuration Steps:**

1.  **Get API Key:** Ask the user to provide the `TAVILY_API_KEY` they obtained.
2.  **Determine Configuration (using `npx`):**
    *   The recommended method uses `npx` directly in the client configuration.
    *   `command`: `"env"` (or `"cmd"` with `/c "set ... && ..."` on Windows)
    *   `args`: `["TAVILY_API_KEY=<USER_KEY>", "npx", "-y", "tavily-mcp@0.1.4"]` (Replace `<USER_KEY>` placeholder. Check for latest version if possible, but use `0.1.4` as fallback based on research).
    *   `env`: `{ "TAVILY_API_KEY": "<USER_KEY>" }` (Good practice for clarity in config file).
3.  **Update MCP Settings:**
    *   Read the MCP settings file (`/home/jez/.config/Code/User/globalStorage/rooveterinaryinc.roo-cline/settings/mcp_settings.json`).
    *   Add or update the `tavily` server entry within the `mcpServers` object using the determined `command`, `args`, and `env` (replacing `<USER_KEY>` with the actual key). Ensure `disabled: false` and `alwaysAllow: []` are set.
        ```json
        {
          "mcpServers": {
            // ... other servers ...
            "tavily": {
              "command": "env", // Or "cmd" on Windows
              "args": ["TAVILY_API_KEY=USER_PROVIDED_API_KEY", "npx", "-y", "tavily-mcp@0.1.4"],
              "env": {
                "TAVILY_API_KEY": "USER_PROVIDED_API_KEY"
              },
              "disabled": false,
              "alwaysAllow": []
            }
          }
        }
        ```
    *   Write the updated content back to the settings file.
4.  **Alternative (Smithery for Claude Desktop):** Mention that if using Claude Desktop, the user could alternatively run `npx -y @smithery/cli install @tavily-ai/tavily-mcp --client claude` which might handle the configuration automatically.
5.  **Confirmation:** Inform the user that the `tavily` server has been configured and should be available via their MCP client. Suggest refreshing the server list if needed.