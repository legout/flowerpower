+++
id = "MCP-MGR-KB-INSTALL-DUCKDUCKGO-V1"
title = "Install MCP Server: DuckDuckGo (nickclyde)"
context_type = "knowledge_base"
scope = "Procedure for installing the DuckDuckGo MCP server from nickclyde"
target_audience = ["agent-mcp-manager"]
granularity = "procedure"
status = "active"
last_updated = "2025-04-27" # Use current date
tags = ["kb", "mcp", "install", "duckduckgo", "ddg", "search", "python", "uv", "pip", "docker"]
related_context = ["README.md"]
template_schema_doc = ".ruru/templates/toml-md/14_kb_entry.md"
relevance = "High: Specific installation guide"
+++

# Procedure: Install MCP Server - DuckDuckGo (nickclyde)

This procedure guides the user through installing the `duckduckgo-mcp-server` from nickclyde. This server provides tools for searching the web using DuckDuckGo.

**Source:** <https://github.com/nickclyde/duckduckgo-mcp-server>

**Prerequisites:**

*   **Python:** Version 3.10+ likely required. Check with `python --version`.
*   **uv or pip:** Python package installer. `uv` is recommended by the source. Check with `uv --version` or `pip --version`. Install `uv` if needed (see <https://docs.astral.sh/uv>).
*   **Docker:** (Optional, for Docker method). Check with `docker --version`.
*   **Git:** (Optional, for Docker method). Check with `git --version`.

**Installation & Configuration Steps:**

1.  **Choose Method:** Ask the user which installation method they prefer: `uvx` (recommended for client integration), `pip` install, or `Docker`.
2.  **Execute Installation & Determine Configuration:**
    *   **If Method A (`uvx` - Recommended):**
        *   No separate installation command needed.
        *   `command`: `"uvx"`
        *   `args`: `["duckduckgo-mcp-server"]`
        *   `env`: `{}` (No specific env vars identified as required).
    *   **If Method B (`pip` Install):**
        *   Execute installation: `uv pip install duckduckgo-mcp-server` (or `pip install duckduckgo-mcp-server`)
        *   Confirm success.
        *   `command`: `"python"`
        *   `args`: `["-m", "duckduckgo_mcp_server.server"]`
        *   `env`: `{}` (No specific env vars identified as required).
    *   **If Method C (`Docker`):**
        *   Define install directory (e.g., `/home/jez/.local/share/Roo-Code/MCP/duckduckgo-mcp-server`).
        *   Execute cloning:
            ```bash
            git clone https://github.com/nickclyde/duckduckgo-mcp-server.git /home/jez/.local/share/Roo-Code/MCP/duckduckgo-mcp-server
            ```
        *   Build the Docker image:
            ```bash
            cd /home/jez/.local/share/Roo-Code/MCP/duckduckgo-mcp-server && docker build -t mcp/duckduckgo-mcp-server -f Dockerfile .
            ```
        *   Confirm success.
        *   `command`: `"docker"`
        *   `args`: `["run", "-i", "--rm", "mcp/duckduckgo-mcp-server"]`
        *   `env`: `{}` (No specific env vars identified as required).
3.  **Update MCP Settings:**
    *   Read the MCP settings file (`/home/jez/.config/Code/User/globalStorage/rooveterinaryinc.roo-cline/settings/mcp_settings.json`).
    *   Add or update the `duckduckgo` (or `ddg-search`) server entry within the `mcpServers` object using the determined `command`, `args`, and `env`. Ensure `disabled: false` and `alwaysAllow: []` are set.
        ```json
        {
          "mcpServers": {
            // ... other servers ...
            "duckduckgo": { // Or "ddg-search"
              "command": <command_from_step_2>,
              "args": <args_from_step_2>,
              "env": {}, // Add if any specific vars become known
              "disabled": false,
              "alwaysAllow": []
            }
          }
        }
        ```
    *   Write the updated content back to the settings file.
4.  **Confirmation:** Inform the user that the `duckduckgo` server has been configured and should be available via their MCP client. Suggest refreshing the server list if needed.