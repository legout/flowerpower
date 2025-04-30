+++
id = "MCP-MGR-KB-INSTALL-MEMORY-V1"
title = "Install MCP Server: Memory"
context_type = "knowledge_base"
scope = "Procedure for installing the official MCP Memory server"
target_audience = ["agent-mcp-manager"]
granularity = "procedure"
status = "active"
last_updated = "2025-04-27" # Use current date
tags = ["kb", "mcp", "install", "memory", "nodejs", "typescript", "storage"]
related_context = ["README.md"]
template_schema_doc = ".ruru/templates/toml-md/14_kb_entry.md"
relevance = "High: Specific installation guide"
+++

# Procedure: Install MCP Server - Memory

This procedure guides the user through installing the official `memory` server from the `modelcontextprotocol/servers` repository. This server provides persistent storage capabilities for MCP interactions.

**Source:** <https://github.com/modelcontextprotocol/servers/tree/main/src/memory>

**Prerequisites:**

*   **Node.js:** Version 16+ recommended. Check with `node --version`.
*   **npm:** Bundled with Node.js. Check with `npm --version`.
*   **Git:** Required for cloning. Check with `git --version`.

**Installation & Configuration Steps:**

1.  **Define Install Directory:** Suggest a standard location, e.g., `/home/jez/.local/share/Roo-Code/MCP/mcp-servers-repo`. Confirm with the user or use the default.
2.  **Clone Repository (if not already cloned):**
    *   Check if the target directory exists.
    *   If not, execute cloning:
        ```bash
        git clone https://github.com/modelcontextprotocol/servers.git /home/jez/.local/share/Roo-Code/MCP/mcp-servers-repo
        ```
    *   Confirm success.
3.  **Install Dependencies:**
    *   Navigate to the memory server directory within the cloned repo:
        ```bash
        cd /home/jez/.local/share/Roo-Code/MCP/mcp-servers-repo/src/memory
        ```
    *   Execute dependency installation:
        ```bash
        npm install
        ```
    *   Confirm success.
4.  **Build Server:**
    *   Execute the build command (still in the `src/memory` directory):
        ```bash
        npm run build
        ```
    *   Confirm success. This should create a `build` or `dist` directory. Assume `build` for the configuration step unless build output indicates otherwise.
5.  **Determine Configuration:**
    *   `command`: `"node"`
    *   `args`: `["/home/jez/.local/share/Roo-Code/MCP/mcp-servers-repo/src/memory/build/index.js"]` (Adjust if build output directory is different, e.g., `dist`).
    *   `env`: `{}` (Initially empty).
6.  **Configure Storage (Optional but Recommended):**
    *   Ask the user if they want to specify a file path for memory persistence using `MEMORY_FILE_PATH`.
    *   If yes, ask for the desired path (e.g., `/home/jez/.local/share/Roo-Code/MCP/memory.json`).
    *   Add `MEMORY_FILE_PATH` to the `env` object:
        ```json
        "env": {
          "MEMORY_FILE_PATH": "/path/to/user/specified/memory.json"
        }
        ```
    *   *(Note: Mention other backends like Qdrant/ChromaDB exist in forks but require different env vars like `OPENAI_API_KEY`, `QDRANT_URL`, etc., and are not covered by this basic install.)*
7.  **Update MCP Settings:**
    *   Read the MCP settings file (`/home/jez/.config/Code/User/globalStorage/rooveterinaryinc.roo-cline/settings/mcp_settings.json`).
    *   Add or update the `memory` server entry within the `mcpServers` object using the determined `command`, `args`, and `env`. Ensure `disabled: false` and `alwaysAllow: []` are set.
        ```json
        {
          "mcpServers": {
            // ... other servers ...
            "memory": {
              "command": "node",
              "args": ["/home/jez/.local/share/Roo-Code/MCP/mcp-servers-repo/src/memory/build/index.js"],
              "env": {
                // Add MEMORY_FILE_PATH here if provided in step 6
              },
              "disabled": false,
              "alwaysAllow": []
            }
          }
        }
        ```
    *   Write the updated content back to the settings file.
8.  **Confirmation:** Inform the user that the `memory` server has been configured and should be available.