+++
id = "MCP-MGR-KB-INSTALL-STRIPE-V1"
title = "Install MCP Server: Stripe Agent Toolkit"
context_type = "knowledge_base"
scope = "Procedure for installing the Stripe Agent Toolkit MCP server"
target_audience = ["agent-mcp-manager"]
granularity = "procedure"
status = "active"
last_updated = "2025-04-27" # Use current date
tags = ["kb", "mcp", "install", "stripe", "payments", "api-key", "docker", "nodejs"]
related_context = ["README.md"]
template_schema_doc = ".ruru/templates/toml-md/14_kb_entry.md"
relevance = "High: Specific installation guide"
+++

# Procedure: Install MCP Server - Stripe Agent Toolkit

This procedure guides the user through installing the `agent-toolkit` server from Stripe. This server provides tools for AI agents to interact with the Stripe API.

**Source:** <https://github.com/stripe/agent-toolkit>

**Prerequisites:**

*   **Docker:** Docker must be installed and running (Recommended method). Check with `docker --version`.
*   **Node.js/npm/npx:** (Alternative method). Check versions with `node --version`, `npm --version`, `npx --version`.
*   **Stripe Secret Key:**
    *   Explain that a Stripe **secret** API key (starting with `sk_...`) is required. Test keys (`sk_test_...`) are recommended for initial setup.
    *   Guide the user to find their keys in the Stripe Dashboard: <https://dashboard.stripe.com/apikeys>
    *   Instruct the user to copy the secret key securely.

**Installation & Configuration Steps:**

1.  **Get Stripe Key:** Ask the user to provide their Stripe Secret Key (`STRIPE_SECRET_KEY`). Emphasize using a test key initially.
2.  **Choose Method:** Ask the user which installation method they prefer: `Docker` (recommended) or `npx`/`Manual Clone`.
3.  **Execute Installation & Determine Configuration:**
    *   **If Method A (`Docker` - Recommended):**
        *   No separate installation/build command needed if using the pre-built image.
        *   `command`: `"docker"`
        *   `args`: `["run", "--rm", "-i", "-e", "STRIPE_SECRET_KEY=<USER_KEY>", "ghcr.io/stripe/agent-toolkit:latest"]` (Replace `<USER_KEY>` placeholder).
        *   `env`: `{ "STRIPE_SECRET_KEY": "<USER_KEY>" }` (Good practice for clarity).
    *   **If Method B (`npx` - *If available, needs confirmation*):**
        *   *(Self-note: Research didn't explicitly confirm an `npx` command for this specific toolkit, but it's common for MCP servers. Assume it might exist as `@stripe/agent-toolkit` or similar.)*
        *   If an `npx` command exists:
            *   `command`: `"env"` (or `"cmd"` /c on Windows)
            *   `args`: `["STRIPE_SECRET_KEY=<USER_KEY>", "npx", "-y", "@stripe/agent-toolkit@latest"]` (Replace `<USER_KEY>` and potentially package name/version).
            *   `env`: `{ "STRIPE_SECRET_KEY": "<USER_KEY>" }`
    *   **If Method C (Manual Clone - For development):**
        *   Define install directory (e.g., `/home/jez/.local/share/Roo-Code/MCP/agent-toolkit`).
        *   Execute cloning:
            ```bash
            git clone https://github.com/stripe/agent-toolkit.git /home/jez/.local/share/Roo-Code/MCP/agent-toolkit
            ```
        *   Install dependencies (likely `npm install` based on repo structure):
            ```bash
            cd /home/jez/.local/share/Roo-Code/MCP/agent-toolkit && npm install
            ```
        *   Build server (check `package.json` for build script, e.g., `npm run build`):
            ```bash
            npm run build
            ```
        *   Confirm success.
        *   Determine run command (e.g., `node dist/index.js` or similar).
        *   `command`: `"node"`
        *   `args`: `["/home/jez/.local/share/Roo-Code/MCP/agent-toolkit/dist/index.js"]` (Adjust path).
        *   `env`: `{ "STRIPE_SECRET_KEY": "<USER_KEY>" }` (Replace `<USER_KEY>`).
4.  **Update MCP Settings:**
    *   Read the MCP settings file (`/home/jez/.config/Code/User/globalStorage/rooveterinaryinc.roo-cline/settings/mcp_settings.json`).
    *   Add or update the `stripe` server entry within the `mcpServers` object using the determined `command`, `args`, and `env` (replacing placeholders). Ensure `disabled: false` and `alwaysAllow: []` are set.
        ```json
        {
          "mcpServers": {
            // ... other servers ...
            "stripe": {
              "command": <command_from_step_3>,
              "args": <args_from_step_3>,
              "env": {
                "STRIPE_SECRET_KEY": "USER_PROVIDED_SECRET_KEY"
              },
              "disabled": false,
              "alwaysAllow": []
            }
          }
        }
        ```
    *   Write the updated content back to the settings file.
5.  **Confirmation:** Inform the user that the `stripe` agent toolkit server has been configured and should be available via their MCP client. Suggest refreshing the server list if needed.