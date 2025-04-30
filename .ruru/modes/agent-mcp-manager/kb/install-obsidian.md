+++
id = "MCP-MGR-KB-INSTALL-OBSIDIAN-V1"
title = "Install MCP Server: Obsidian (MarkusPfundstein)"
context_type = "knowledge_base"
scope = "Procedure for installing the mcp-obsidian server"
target_audience = ["agent-mcp-manager"]
granularity = "procedure"
status = "active"
last_updated = "2025-04-27" # Use current date
tags = ["kb", "mcp", "install", "obsidian", "notes", "python", "uv", "api-key"]
related_context = ["README.md"]
template_schema_doc = ".ruru/templates/toml-md/14_kb_entry.md"
relevance = "High: Specific installation guide"
+++

# Procedure: Install MCP Server - Obsidian (MarkusPfundstein)

This procedure guides the user through installing the `mcp-obsidian` server from MarkusPfundstein. This server provides tools for interacting with an Obsidian vault via the Local REST API plugin.

**Source:** <https://github.com/MarkusPfundstein/mcp-obsidian>

**Prerequisites:**

*   **Python:** Version 3.11+ recommended. Check with `python --version`.
*   **uv:** Python package installer. Check with `uv --version`. Install if needed (see <https://docs.astral.sh/uv>).
*   **Git:** Required for cloning. Check with `git --version`.
*   **Obsidian:** Desktop application installed.
*   **Obsidian Local REST API Plugin:**
    *   Instruct the user to install and enable the "Local REST API" community plugin within Obsidian.
    *   Guide them to the plugin settings to copy the generated API Key.
    *   Note the Host address (usually `http://127.0.0.1:27123`, but confirm in plugin settings).

**Installation & Configuration Steps:**

1.  **Get Obsidian Config:** Ask the user for their Obsidian Local REST API Key and Host address.
2.  **Define Install Directory:** Suggest a standard location, e.g., `/home/jez/.local/share/Roo-Code/MCP/mcp-obsidian`. Confirm with the user or use the default.
3.  **Clone Repository:**
    *   Execute cloning:
        ```bash
        git clone https://github.com/MarkusPfundstein/mcp-obsidian.git /home/jez/.local/share/Roo-Code/MCP/mcp-obsidian
        ```
    *   Confirm success.
4.  **Install Dependencies:**
    *   Navigate to the server directory:
        ```bash
        cd /home/jez/.local/share/Roo-Code/MCP/mcp-obsidian
        ```
    *   Execute dependency installation using `uv`:
        ```bash
        uv sync
        ```
    *   Confirm success.
5.  **Determine Configuration:**
    *   `command`: `"uv"` (or potentially `"uvx"`, needs confirmation based on `pyproject.toml`)
    *   `args`: `["run", "mcp-obsidian"]` (or just `["mcp-obsidian"]` if using `uvx`).
    *   `env`: `{ "OBSIDIAN_API_KEY": "<USER_KEY>", "OBSIDIAN_HOST": "<USER_HOST>" }` (Replace placeholders).
    *   *(Self-note: Verify exact run command/args if possible by inspecting `pyproject.toml` in the repo if accessible, otherwise use `uv run mcp-obsidian` as the likely command based on debugging info.)*
6.  **Update MCP Settings:**
    *   Read the MCP settings file (`/home/jez/.config/Code/User/globalStorage/rooveterinaryinc.roo-cline/settings/mcp_settings.json`).
    *   Add or update the `obsidian` server entry within the `mcpServers` object using the determined `command`, `args`, and `env` (replacing placeholders with actual user values). Ensure `disabled: false` and `alwaysAllow: []` are set.
        ```json
        {
          "mcpServers": {
            // ... other servers ...
            "obsidian": {
              "command": "uv", // Or "uvx"
              "args": ["run", "mcp-obsidian"], // Or ["mcp-obsidian"]
              "env": {
                "OBSIDIAN_API_KEY": "USER_PROVIDED_API_KEY",
                "OBSIDIAN_HOST": "USER_PROVIDED_HOST"
              },
              "disabled": false,
              "alwaysAllow": []
            }
          }
        }
        ```
    *   Write the updated content back to the settings file.
7.  **Confirmation:** Inform the user that the `obsidian` server has been configured and should be available via their MCP client. Suggest refreshing the server list if needed. Mention they can debug using `npx @modelcontextprotocol/inspector uv --directory /path/to/mcp-obsidian run mcp-obsidian`.