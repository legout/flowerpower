+++
id = "MCP-MGR-KB-INSTALL-SEQTHINK-V1"
title = "Install MCP Server: Sequential Thinking"
context_type = "knowledge_base"
scope = "Procedure for installing the Sequential Thinking MCP server"
target_audience = ["agent-mcp-manager"]
granularity = "procedure"
status = "active"
last_updated = "2025-04-27" # Use current date
tags = ["kb", "mcp", "install", "sequential-thinking", "problem-solving", "npx", "docker", "nodejs"]
related_context = ["README.md"]
template_schema_doc = ".ruru/templates/toml-md/14_kb_entry.md"
relevance = "High: Specific installation guide"
+++

# Procedure: Install MCP Server - Sequential Thinking

This procedure guides the user through installing the `sequentialthinking` server from the Model Context Protocol organization. This server provides tools for structured problem-solving.

**Source:** <https://github.com/modelcontextprotocol/servers/tree/main/src/sequentialthinking> (Package: `@modelcontextprotocol/server-sequential-thinking`)

**Prerequisites:**

*   **Node.js:** Latest LTS version recommended. Check with `node --version`.
*   **npm/npx:** Bundled with Node.js. Check with `npm --version` / `npx --version`.
*   **Docker:** (Optional, for Docker method). Docker must be installed and running. Check with `docker --version`.
*   **Git:** (Optional, for Docker build or manual install). Check with `git --version`.

**Installation & Configuration Steps:**

1.  **Choose Method:** Ask the user which installation method they prefer: `npx` (recommended for client integration) or `Docker`.
2.  **Execute Installation & Determine Configuration:**
    *   **If Method A (`npx`):**
        *   No separate installation command needed.
        *   `command`: `"npx"`
        *   `args`: `["-y", "@modelcontextprotocol/server-sequential-thinking"]`
        *   `env`: `{}` (No specific env vars identified as required in research).
    *   **If Method B (`Docker`):**
        *   Requires cloning the main `servers` repo first if not already done (suggest `/home/jez/.local/share/Roo-Code/MCP/mcp-servers-repo`).
            ```bash
            # Only if repo not already cloned:
            # git clone https://github.com/modelcontextprotocol/servers.git /home/jez/.local/share/Roo-Code/MCP/mcp-servers-repo
            ```
        *   Execute Docker build (from the root of the cloned `servers` repo):
            ```bash
            docker build -t mcp/sequentialthinking -f src/sequentialthinking/Dockerfile .
            ```
        *   Confirm success.
        *   `command`: `"docker"`
        *   `args`: `["run", "--rm", "-i", "mcp/sequentialthinking"]`
        *   `env`: `{}` (No specific env vars identified as required in research).
3.  **Update MCP Settings:**
    *   Read the MCP settings file (`/home/jez/.config/Code/User/globalStorage/rooveterinaryinc.roo-cline/settings/mcp_settings.json`).
    *   Add or update the `sequential-thinking` server entry within the `mcpServers` object using the determined `command`, `args`, and `env`. Ensure `disabled: false` and `alwaysAllow: []` are set.
        ```json
        {
          "mcpServers": {
            // ... other servers ...
            "sequential-thinking": {
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
4.  **Confirmation:** Inform the user that the `sequential-thinking` server has been configured and should be available via their MCP client. Suggest refreshing the server list if needed.