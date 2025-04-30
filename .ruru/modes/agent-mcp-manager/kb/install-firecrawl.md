+++
id = "MCP-MGR-KB-INSTALL-FIRECRAWL-V1"
title = "Install MCP Server: Firecrawl"
context_type = "knowledge_base"
scope = "Procedure for installing the Firecrawl MCP server from Mendable.ai"
target_audience = ["agent-mcp-manager"]
granularity = "procedure"
status = "active"
last_updated = "2025-04-27" # Use current date
tags = ["kb", "mcp", "install", "firecrawl", "mendableai", "web-crawl", "npx", "nodejs", "api-key"]
related_context = ["README.md"]
template_schema_doc = ".ruru/templates/toml-md/14_kb_entry.md"
relevance = "High: Specific installation guide"
+++

# Procedure: Install MCP Server - Firecrawl

This procedure guides the user through installing the `firecrawl-mcp-server` from Mendable.ai. This server provides tools for crawling and scraping web pages.

**Source:** <https://github.com/mendableai/firecrawl-mcp-server>

**Prerequisites:**

*   **Node.js:** Latest LTS version recommended. Check with `node --version`.
*   **npm:** Bundled with Node.js. Check with `npm --version`.
*   **Firecrawl API Key:**
    *   Explain that an API key is required to use the Firecrawl cloud service.
    *   Guide the user to sign up and obtain one from the Firecrawl dashboard: <https://firecrawl.dev/>
    *   Instruct the user to copy the generated API key.
*   **Git:** (Needed only for manual/dev install). Check with `git --version`.

**Installation & Configuration Steps:**

1.  **Get API Key:** Ask the user to provide the `FIRECRAWL_API_KEY` they obtained.
2.  **Choose Method:** Ask the user how they want to run/configure the server:
    *   **Method A: `npx` (Recommended for Client Integration):** Easiest for direct use within clients like Cursor or Cline.
    *   **Method B: Global `npm` Install:** Installs the command system-wide.
    *   **Method C: Manual Clone & Run:** For development or specific version needs.
3.  **Execute Installation & Determine Configuration:**
    *   **If Method A (`npx`):**
        *   No separate installation command needed.
        *   `command`: `"env"` (or `"cmd"` with `/c "set ... && ..."` on Windows)
        *   `args`: `["FIRECRAWL_API_KEY=<USER_KEY>", "npx", "-y", "firecrawl-mcp"]` (Replace `<USER_KEY>` placeholder).
        *   `env`: `{ "FIRECRAWL_API_KEY": "<USER_KEY>" }` (Good practice for clarity in config file).
    *   **If Method B (Global `npm`):**
        *   Execute installation: `npm install -g firecrawl-mcp` (Confirm package name if this fails).
        *   Confirm success.
        *   `command`: `"firecrawl-mcp"` (or the correct binary name if different).
        *   `args`: `[]`
        *   `env`: `{ "FIRECRAWL_API_KEY": "<USER_KEY>" }` (Replace `<USER_KEY>` placeholder).
    *   **If Method C (Manual Clone):**
        *   Define install directory (e.g., `/home/jez/.local/share/Roo-Code/MCP/firecrawl-mcp-server`).
        *   Execute cloning:
            ```bash
            git clone https://github.com/mendableai/firecrawl-mcp-server.git /home/jez/.local/share/Roo-Code/MCP/firecrawl-mcp-server
            ```
        *   Install dependencies:
            ```bash
            cd /home/jez/.local/share/Roo-Code/MCP/firecrawl-mcp-server && npm install
            ```
        *   Build server (if needed, check `package.json` for build script):
            ```bash
            npm run build
            ```
        *   Confirm success.
        *   Determine run command from `package.json` (e.g., `npm start` might run `node dist/index.js`).
        *   `command`: `"node"`
        *   `args`: `["/home/jez/.local/share/Roo-Code/MCP/firecrawl-mcp-server/dist/index.js"]` (Adjust path based on build output).
        *   `env`: `{ "FIRECRAWL_API_KEY": "<USER_KEY>" }` (Replace `<USER_KEY>` placeholder).
4.  **Optional Configuration:** Ask the user if they are using a self-hosted Firecrawl instance. If yes, ask for the URL and add `FIRECRAWL_API_URL` to the `env` object.
5.  **Update MCP Settings:**
    *   Read the MCP settings file (`/home/jez/.config/Code/User/globalStorage/rooveterinaryinc.roo-cline/settings/mcp_settings.json`).
    *   Add or update the `firecrawl` server entry within the `mcpServers` object using the determined `command`, `args`, and `env` (replacing `<USER_KEY>` with the actual key). Ensure `disabled: false` and `alwaysAllow: []` are set.
        ```json
        {
          "mcpServers": {
            // ... other servers ...
            "firecrawl": {
              "command": <command_from_step_3>,
              "args": <args_from_step_3>,
              "env": {
                "FIRECRAWL_API_KEY": "USER_PROVIDED_API_KEY"
                // Add FIRECRAWL_API_URL here if provided in step 4
              },
              "disabled": false,
              "alwaysAllow": []
            }
          }
        }
        ```
    *   Write the updated content back to the settings file.
6.  **Confirmation:** Inform the user that the `firecrawl` server has been configured and should be available.