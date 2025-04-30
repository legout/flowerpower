+++
id = "MCP-MGR-KB-INSTALL-PERPLEXITY-V1"
title = "Install MCP Server: Perplexity Ask"
context_type = "knowledge_base"
scope = "Procedure for installing the Perplexity Ask MCP server"
target_audience = ["agent-mcp-manager"]
granularity = "procedure"
status = "active"
last_updated = "2025-04-27" # Use current date
tags = ["kb", "mcp", "install", "perplexity", "search", "ask", "docker", "api-key"]
related_context = ["README.md"]
template_schema_doc = ".ruru/templates/toml-md/14_kb_entry.md"
relevance = "High: Specific installation guide"
+++

# Procedure: Install MCP Server - Perplexity Ask

This procedure guides the user through installing the `perplexity-ask` server, likely found within the `ppl-ai/modelcontextprotocol` repository. This server provides tools for interacting with the Perplexity AI search/answer engine.

**Source:** <https://github.com/ppl-ai/modelcontextprotocol> (Specifically the `perplexity-ask` server, often run via Docker)

**Prerequisites:**

*   **Docker:** Docker must be installed and running. Check with `docker --version`.
*   **Perplexity API Key:**
    *   Explain that an API key is required.
    *   Guide the user to obtain one from their Perplexity account settings: <https://www.perplexity.ai/settings/api>
    *   Instruct the user to copy the generated API key.
*   **Git:** (Optional, for Docker build). Check with `git --version`.

**Installation & Configuration Steps:**

1.  **Get API Key:** Ask the user to provide the `PERPLEXITY_API_KEY` they obtained.
2.  **Choose Method:** Ask the user if they want to use the pre-built Docker image (recommended) or build it from source.
3.  **Execute Installation & Determine Configuration (Docker Method):**
    *   **If Using Pre-built Image (Recommended, if available - *needs confirmation if ppl-ai publishes one*):**
        *   *(Self-note: Research did not confirm an official pre-built image from ppl-ai, but showed examples using `mcp/perplexity-ask`. Assume building is necessary unless a pre-built image URL is found.)*
    *   **If Building Docker Image (Likely required):**
        *   Requires cloning the main `modelcontextprotocol` repo first if not already done (suggest `/home/jez/.local/share/Roo-Code/MCP/ppl-ai-modelcontextprotocol`).
            ```bash
            # Only if repo not already cloned:
            # git clone https://github.com/ppl-ai/modelcontextprotocol.git /home/jez/.local/share/Roo-Code/MCP/ppl-ai-modelcontextprotocol
            ```
        *   Execute Docker build (from the root of the cloned repo, assuming Dockerfile is at `servers/perplexity-ask/Dockerfile`):
            ```bash
            docker build -t mcp/perplexity-ask:latest -f servers/perplexity-ask/Dockerfile .
            ```
        *   Confirm success.
        *   `command`: `"docker"`
        *   `args`: `["run", "--rm", "-i", "mcp/perplexity-ask:latest"]`
        *   `env`: `{ "PERPLEXITY_API_KEY": "<USER_KEY>" }` (Replace `<USER_KEY>` placeholder).
4.  **Update MCP Settings:**
    *   Read the MCP settings file (`/home/jez/.config/Code/User/globalStorage/rooveterinaryinc.roo-cline/settings/mcp_settings.json`).
    *   Add or update the `perplexity-ask` server entry within the `mcpServers` object using the determined `command`, `args`, and `env` (replacing `<USER_KEY>` with the actual key). Ensure `disabled: false` and `alwaysAllow: []` are set.
        ```json
        {
          "mcpServers": {
            // ... other servers ...
            "perplexity-ask": {
              "command": "docker",
              "args": ["run", "--rm", "-i", "mcp/perplexity-ask:latest"], // Use pre-built image URL if found
              "env": {
                "PERPLEXITY_API_KEY": "USER_PROVIDED_API_KEY"
              },
              "disabled": false,
              "alwaysAllow": []
            }
          }
        }
        ```
    *   Write the updated content back to the settings file.
5.  **Confirmation:** Inform the user that the `perplexity-ask` server has been configured and should be available via their MCP client. Suggest refreshing the server list if needed.