+++
id = "MCP-MGR-KB-INSTALL-GOOGLE-MAPS-V1"
title = "Install MCP Server: Google Maps"
context_type = "knowledge_base"
scope = "Procedure for installing the Google Maps MCP server"
target_audience = ["agent-mcp-manager"]
granularity = "procedure"
status = "active"
last_updated = "2025-04-27" # Use current date
tags = ["kb", "mcp", "install", "google-maps", "maps", "geocoding", "places", "npx", "docker", "api-key"]
related_context = ["README.md"]
template_schema_doc = ".ruru/templates/toml-md/14_kb_entry.md"
relevance = "High: Specific installation guide"
+++

# Procedure: Install MCP Server - Google Maps

This procedure guides the user through installing an MCP server for Google Maps, likely `@modelcontextprotocol/server-google-maps` or `@cablate/mcp-google-map`. This server provides tools for interacting with various Google Maps APIs.

**Source:** <https://github.com/modelcontextprotocol/servers/tree/main/src/google-maps> (Assumed location, package names vary)

**Prerequisites:**

*   **Node.js & npm/npx:** (For npx method). Check with `node --version`.
*   **Docker:** (For Docker method). Check with `docker --version`.
*   **Google Cloud Project & API Key:**
    *   Guide user to create a Google Cloud Project if needed.
    *   Guide user to enable necessary Google Maps Platform APIs (e.g., Geocoding API, Places API, Directions API, Distance Matrix API, Elevation API).
    *   Guide user to create an **API Key** under APIs & Services -> Credentials. Restrict the key if possible (e.g., to specific APIs and IP addresses).
    *   Instruct user to copy the API key securely.

**Installation & Configuration Steps:**

1.  **Get API Key:** Ask the user to provide the `GOOGLE_MAPS_API_KEY` they obtained.
2.  **Choose Method:** Ask the user which installation method they prefer: `npx` (recommended for client integration) or `Docker`.
3.  **Determine Configuration:**
    *   **If Method A (`npx`):**
        *   `command`: `"npx"`
        *   `args`: `["-y", "@modelcontextprotocol/server-google-maps"]` (Use `@cablate/mcp-google-map` as alternative if first fails).
        *   `env`: `{ "GOOGLE_MAPS_API_KEY": "<USER_KEY>" }` (Replace `<USER_KEY>` placeholder).
    *   **If Method B (`Docker`):**
        *   *(Self-note: Assumes image name `mcp/google-maps` based on research, needs verification if a pre-built image exists and its name).*
        *   `command`: `"docker"`
        *   `args`: `["run", "-i", "--rm", "-e", "GOOGLE_MAPS_API_KEY=<USER_KEY>", "mcp/google-maps"]` (Replace `<USER_KEY>` and potentially image name).
        *   `env`: `{ "GOOGLE_MAPS_API_KEY": "<USER_KEY>" }` (Good practice).
4.  **Update MCP Settings:**
    *   Read the MCP settings file (`/home/jez/.config/Code/User/globalStorage/rooveterinaryinc.roo-cline/settings/mcp_settings.json`).
    *   Add or update the `google-maps` server entry within the `mcpServers` object using the determined `command`, `args`, and `env` (replacing placeholders). Ensure `disabled: false` and `alwaysAllow: []` are set.
        ```json
        {
          "mcpServers": {
            // ... other servers ...
            "google-maps": {
              "command": <command_from_step_3>,
              "args": <args_from_step_3>,
              "env": {
                "GOOGLE_MAPS_API_KEY": "USER_PROVIDED_API_KEY"
              },
              "disabled": false,
              "alwaysAllow": []
            }
          }
        }
        ```
    *   Write the updated content back to the settings file.
5.  **Confirmation:** Inform the user that the `google-maps` server has been configured and should be available via their MCP client. Suggest refreshing the server list if needed.