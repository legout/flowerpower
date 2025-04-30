+++
id = "MCP-MGR-KB-INSTALL-DISCORD-SLIM-V1"
title = "Install MCP Server: Discord (slimslenderslacks)"
context_type = "knowledge_base"
scope = "Procedure for installing the mcp-discord server from slimslenderslacks"
target_audience = ["agent-mcp-manager"]
granularity = "procedure"
status = "placeholder" # Marked as placeholder due to lack of specific info
last_updated = "2025-04-27" # Use current date
tags = ["kb", "mcp", "install", "discord", "chat", "nodejs", "api-key", "placeholder"]
related_context = ["README.md", "install-discord-hanweg.md", "install-discord-v3.md"] # Link to other discord KBs if they exist
template_schema_doc = ".ruru/templates/toml-md/14_kb_entry.md"
relevance = "Medium: Specific installation guide, but needs verification"
+++

# Procedure: Install MCP Server - Discord (slimslenderslacks)

**WARNING:** Specific installation details for `slimslenderslacks/mcp-discord` were not found in research. The following steps are based on *other* Node.js Discord MCP servers (like `v-3/discordmcp`) and **require verification** by checking the target repository's README or code.

**Source:** <https://github.com/slimslenderslacks/mcp-discord> (Needs Verification)

**Prerequisites (Likely):**

*   **Node.js:** Version 16+ likely required. Check with `node --version`.
*   **npm:** Bundled with Node.js. Check with `npm --version`.
*   **Git:** Required for cloning. Check with `git --version`.
*   **Discord Bot Token:**
    *   Explain a Discord Bot is needed. Guide user to Discord Developer Portal -> Applications -> New Application.
    *   Guide user to Bot tab -> Add Bot. Copy the **Token**.
    *   Instruct user to enable **Privileged Gateway Intents** (Presence Intent, Server Members Intent, Message Content Intent).
    *   Guide user to OAuth2 -> URL Generator. Select `bot` scope. Under Bot Permissions, select necessary permissions (e.g., Read Messages/View Channels, Send Messages, Read Message History).
    *   Instruct user to copy the generated URL, visit it, and add the bot to their server.

**Installation & Configuration Steps (Assumed - Needs Verification):**

1.  **Get Discord Token:** Ask the user for their Discord Bot Token (`DISCORD_TOKEN`).
2.  **Define Install Directory:** Suggest a standard location, e.g., `/home/jez/.local/share/Roo-Code/MCP/mcp-discord-slim`. Confirm with the user or use the default.
3.  **Clone Repository:**
    *   Execute cloning:
        ```bash
        git clone https://github.com/slimslenderslacks/mcp-discord.git /home/jez/.local/share/Roo-Code/MCP/mcp-discord-slim
        ```
    *   Confirm success.
4.  **Install Dependencies:**
    *   Navigate to the server directory:
        ```bash
        cd /home/jez/.local/share/Roo-Code/MCP/mcp-discord-slim
        ```
    *   Execute dependency installation:
        ```bash
        npm install
        ```
    *   Confirm success.
5.  **Build Server (If TypeScript):**
    *   Check `package.json` for a build script. If present, execute:
        ```bash
        npm run build
        ```
    *   Confirm success. Note the output directory (e.g., `dist`).
6.  **Determine Configuration:**
    *   `command`: `"node"`
    *   `args`: `["/home/jez/.local/share/Roo-Code/MCP/mcp-discord-slim/dist/index.js"]` (Adjust path based on build output or main script file).
    *   `env`: `{ "DISCORD_TOKEN": "<USER_TOKEN>" }` (Replace `<USER_TOKEN>` placeholder).
7.  **Update MCP Settings:**
    *   Read the MCP settings file (`/home/jez/.config/Code/User/globalStorage/rooveterinaryinc.roo-cline/settings/mcp_settings.json`).
    *   Add or update the `discord-slim` server entry within the `mcpServers` object using the determined `command`, `args`, and `env` (replacing placeholder). Ensure `disabled: false` and `alwaysAllow: []` are set.
        ```json
        {
          "mcpServers": {
            // ... other servers ...
            "discord-slim": {
              "command": "node",
              "args": ["/home/jez/.local/share/Roo-Code/MCP/mcp-discord-slim/dist/index.js"], // Verify path
              "env": {
                "DISCORD_TOKEN": "USER_PROVIDED_TOKEN"
              },
              "disabled": false,
              "alwaysAllow": []
            }
          }
        }
        ```
    *   Write the updated content back to the settings file.
8.  **Confirmation:** Inform the user that the `discord-slim` server has been configured based on assumptions and **needs verification**. Suggest checking the repository README and testing carefully. Suggest refreshing the server list if needed.