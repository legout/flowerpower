+++
id = "MCP-MGR-KB-INSTALL-FETCH-V1"
title = "Install MCP Server: Fetch"
context_type = "knowledge_base"
scope = "Procedure for installing the official MCP Fetch server"
target_audience = ["agent-mcp-manager"]
granularity = "procedure"
status = "active"
last_updated = "2025-04-27" # Use current date
tags = ["kb", "mcp", "install", "fetch", "python", "uv", "pip"]
related_context = ["README.md"]
template_schema_doc = ".ruru/templates/toml-md/14_kb_entry.md"
relevance = "High: Specific installation guide"
+++

# Procedure: Install MCP Server - Fetch

This procedure guides the user through installing the official `mcp-server-fetch` from the `modelcontextprotocol` organization. This server allows fetching and processing web content.

**Source:** <https://github.com/modelcontextprotocol/servers/tree/main/src/fetch>

**Prerequisites:**

*   Python installed (required for `pip` fallback).
*   `uv` installed (recommended).
    *   Check `uv`: Use `execute_command` with `uv --version`.
*   `pip` installed (fallback if `uv` is not available).
    *   Check `pip`: Use `execute_command` with `pip --version` or `python -m pip --version`.

**Installation & Configuration Steps:**

1.  **Check for `uv`:**
    *   Execute `uv --version`.
    *   If successful (exit code 0), proceed with the `uvx` method (Step 2).
    *   If it fails, proceed to check for `pip` (Step 3).
2.  **Configure using `uvx` (Recommended):**
    *   `method`: `"uvx"`
    *   `command`: `"uvx"`
    *   `args`: `["mcp-server-fetch"]`
    *   Skip to Step 4 (Update MCP Settings).
3.  **Check for `pip` and Install/Configure:**
    *   Execute `python -m pip --version` (or `pip --version`).
    *   If successful (exit code 0):
        *   Execute `pip install mcp-server-fetch`. Confirm success.
        *   `method`: `"pip"`
        *   `command`: `"python"` (or specific executable if needed)
        *   `args`: `["-m", "mcp_server_fetch"]`
        *   Proceed to Step 4 (Update MCP Settings).
    *   If `pip` check fails: Report error to user - neither `uv` nor `pip` found. **Stop.**
4.  **Update MCP Settings:**
    *   Read the MCP settings file (`/home/jez/.config/Code/User/globalStorage/rooveterinaryinc.roo-cline/settings/mcp_settings.json`).
    *   Add or update the `fetch` server entry within the `mcpServers` object using the determined `command` and `args`. Ensure `disabled: false` and `alwaysAllow: []` are set.
        ```json
        {
          "mcpServers": {
            // ... other servers ...
            "fetch": {
              "command": <command_from_step_3>,
              "args": <args_from_step_3>,
              "disabled": false,
              "alwaysAllow": []
              // No 'env' needed for this server based on research
            }
          }
        }
        ```
    *   Write the updated content back to the settings file.
5.  **Confirmation:** Inform the user that the `fetch` server has been configured and should be available. Mention that Node.js is an optional dependency for potentially better HTML simplification.