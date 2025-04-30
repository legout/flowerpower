+++
id = "MCP-MGR-KB-INSTALL-ELEVENLABS-V1"
title = "Install MCP Server: ElevenLabs"
context_type = "knowledge_base"
scope = "Procedure for installing the official ElevenLabs MCP server"
target_audience = ["agent-mcp-manager"]
granularity = "procedure"
status = "active"
last_updated = "2025-04-27" # Use current date
tags = ["kb", "mcp", "install", "elevenlabs", "tts", "speech", "python", "uv", "pip", "api-key"]
related_context = ["README.md"]
template_schema_doc = ".ruru/templates/toml-md/14_kb_entry.md"
relevance = "High: Specific installation guide"
+++

# Procedure: Install MCP Server - ElevenLabs

This procedure guides the user through installing the official `elevenlabs-mcp` server from ElevenLabs. This server provides text-to-speech (TTS) capabilities.

**Source:** <https://github.com/elevenlabs/elevenlabs-mcp>

**Prerequisites:**

*   **Python:** Version 3.10+ recommended. Check with `python --version`.
*   **pip or uv:** Python package installer. `uv` is recommended by the source. Check with `pip --version` or `uv --version`. Install `uv` if needed (see <https://docs.astral.sh/uv>).
*   **ElevenLabs API Key:**
    *   Explain that an API key is required.
    *   Guide the user to their ElevenLabs account settings (Profile section) to find or generate an API key.
    *   Instruct the user to copy the API key securely.

**Installation & Configuration Steps:**

1.  **Get API Key:** Ask the user to provide the `ELEVENLABS_API_KEY` they obtained.
2.  **Choose Method:** Ask the user which installation/run method they prefer: `uvx` (recommended for client integration), `pip` install, or `Manual Clone` (for development).
3.  **Execute Installation & Determine Configuration:**
    *   **If Method A (`uvx` - Recommended):**
        *   No separate installation command needed.
        *   `command`: `"uvx"`
        *   `args`: `["elevenlabs-mcp"]`
        *   `env`: `{ "ELEVENLABS_API_KEY": "<USER_KEY>" }` (Replace `<USER_KEY>` placeholder).
    *   **If Method B (`pip` Install):**
        *   Execute installation: `pip install elevenlabs-mcp`
        *   Confirm success.
        *   `command`: `"python"`
        *   `args`: `["-m", "elevenlabs_mcp"]` (or potentially `elevenlabs_mcp.server`)
        *   `env`: `{ "ELEVENLABS_API_KEY": "<USER_KEY>" }` (Replace `<USER_KEY>` placeholder).
    *   **If Method C (Manual Clone):**
        *   Define install directory (e.g., `/home/jez/.local/share/Roo-Code/MCP/elevenlabs-mcp`).
        *   Execute cloning:
            ```bash
            git clone https://github.com/elevenlabs/elevenlabs-mcp.git /home/jez/.local/share/Roo-Code/MCP/elevenlabs-mcp
            ```
        *   Install dependencies (using `uv` recommended):
            ```bash
            cd /home/jez/.local/share/Roo-Code/MCP/elevenlabs-mcp && uv sync
            ```
            (Or `pip install -r requirements.txt` if using pip).
        *   Confirm success.
        *   Determine run command (likely `uv run elevenlabs-mcp-server` or `python -m elevenlabs_mcp`).
        *   `command`: `"uv"` (or `"python"`)
        *   `args`: `["run", "elevenlabs-mcp-server"]` (or `["-m", "elevenlabs_mcp"]`)
        *   `env`: `{ "ELEVENLABS_API_KEY": "<USER_KEY>" }` (Replace `<USER_KEY>`).
4.  **Optional Configuration:** Ask the user if they want to specify a base path for file operations using `ELEVENLABS_MCP_BASE_PATH`. If yes, add it to the `env` object. Mention other potential options seen in forks (like voice ID, model, stability) but note they might not be supported in the official version.
5.  **Update MCP Settings:**
    *   Read the MCP settings file (`/home/jez/.config/Code/User/globalStorage/rooveterinaryinc.roo-cline/settings/mcp_settings.json`).
    *   Add or update the `elevenlabs` server entry within the `mcpServers` object using the determined `command`, `args`, and `env` (replacing placeholders). Ensure `disabled: false` and `alwaysAllow: []` are set.
        ```json
        {
          "mcpServers": {
            // ... other servers ...
            "elevenlabs": {
              "command": <command_from_step_3>,
              "args": <args_from_step_3>,
              "env": {
                "ELEVENLABS_API_KEY": "USER_PROVIDED_API_KEY"
                // Add ELEVENLABS_MCP_BASE_PATH here if provided
              },
              "disabled": false,
              "alwaysAllow": []
            }
          }
        }
        ```
    *   Write the updated content back to the settings file.
6.  **Confirmation:** Inform the user that the `elevenlabs` server has been configured and should be available via their MCP client. Suggest refreshing the server list if needed.