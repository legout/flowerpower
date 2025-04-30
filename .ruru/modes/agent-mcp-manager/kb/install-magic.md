+++
id = "MCP-MGR-KB-INSTALL-MAGIC-V1"
title = "Install MCP Server: Magic (21st.dev)"
context_type = "knowledge_base"
scope = "Procedure for installing the Magic MCP server from 21st.dev"
target_audience = ["agent-mcp-manager"]
granularity = "procedure"
status = "active"
last_updated = "2025-04-27" # Use current date
tags = ["kb", "mcp", "install", "magic", "21st-dev", "npx", "api-key"]
related_context = ["README.md"]
template_schema_doc = ".ruru/templates/toml-md/14_kb_entry.md"
relevance = "High: Specific installation guide"
+++

# Procedure: Install MCP Server - Magic (21st.dev)

This procedure guides the user through installing the `magic-mcp` server from 21st.dev. This server provides various AI-powered tools.

**Source:** <https://github.com/21st-dev/magic-mcp>

**Prerequisites:**

*   **Node.js:** Latest LTS version recommended. Check with `node --version`.
*   **Supported IDE Client:** Cursor, Windsurf, Cline (VSCode Extension), or Claude Desktop.
*   **21st.dev API Key:**
    *   Explain that an API key is required.
    *   Guide the user to obtain one from the 21st.dev Magic Console: <https://magic.21st.dev/> (User will likely need to sign up).
    *   Instruct the user to copy the generated API key.

**Installation & Configuration Steps:**

1.  **Get API Key:** Ask the user to provide the `TWENTY_FIRST_API_KEY` they obtained.
2.  **Identify Client:** Ask the user which IDE client they are using (e.g., `cursor`, `windsurf`, `cline`, `claude`).
3.  **Execute Installation (Recommended):**
    *   Execute the following command in the user's terminal, replacing `<client>` with the identified client slug and `<key>` with the user's API key:
        ```bash
        npx @21st-dev/cli@latest install <client> --api-key <key>
        ```
    *   This command should automatically configure the appropriate MCP settings file for the specified client.
4.  **Manual Configuration (Alternative/Verification):**
    *   Explain that the command in step 3 *should* handle configuration, but if manual setup is needed or for verification:
    *   Identify the correct MCP settings file path based on the client:
        *   Cursor: `~/.cursor/mcp.json`
        *   Windsurf: `~/.codeium/windsurf/mcp_config.json`
        *   Cline: `~/.cline/mcp_config.json` (or `/home/jez/.config/Code/User/globalStorage/rooveterinaryinc.roo-cline/settings/mcp_settings.json` for VSCode extension)
        *   Claude: `~/.claude/mcp_config.json`
    *   Read the appropriate settings file.
    *   Ensure the `magic` server entry exists within `mcpServers` and looks similar to this (adjust args based on client if necessary):
        ```json
        {
          "mcpServers": {
            // ... other servers ...
            "magic": {
              "command": "npx",
              "args": [
                "-y",
                "@21st-dev/cli@latest", // Or potentially "@smithery/cli@latest" based on some docs
                "install",
                "@21st-dev/magic-mcp",
                "--client",
                "<client_slug>" // e.g., "cline"
              ],
              "env": {
                "TWENTY_FIRST_API_KEY": "USER_PROVIDED_API_KEY"
              },
              "disabled": false,
              "alwaysAllow": [] // Default to empty
            }
          }
        }
        ```
    *   If manual changes were needed, write the updated content back to the settings file.
5.  **Confirmation:** Inform the user that the `magic-mcp` server installation command has been run (or manual configuration verified) and should be available in their IDE client. Suggest they refresh their MCP server list if applicable and test with a command like `/ui create a basic button`.