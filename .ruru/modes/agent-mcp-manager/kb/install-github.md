+++
id = "MCP-MGR-KB-INSTALL-GITHUB-V1"
title = "Install MCP Server: GitHub"
context_type = "knowledge_base"
scope = "Procedure for installing the official GitHub MCP server"
target_audience = ["agent-mcp-manager"]
granularity = "procedure"
status = "active"
last_updated = "2025-04-27" # Use current date
tags = ["kb", "mcp", "install", "github", "docker", "go", "pat"]
related_context = ["README.md"]
template_schema_doc = ".ruru/templates/toml-md/14_kb_entry.md"
relevance = "High: Specific installation guide"
+++

# Procedure: Install MCP Server - GitHub

This procedure guides the user through installing the official `github-mcp-server` from GitHub. This server provides tools for interacting with GitHub repositories, issues, pull requests, etc.

**Source:** <https://github.com/github/github-mcp-server>

**Prerequisites:**

*   **GitHub Personal Access Token (PAT):**
    *   Explain that a PAT is required for authentication.
    *   Guide the user to generate a **Fine-grained token** here: <https://github.com/settings/tokens?type=beta>
    *   Instruct them to grant the necessary permissions based on the tools they intend to use (e.g., read/write issues, read repositories, etc.). Emphasize granting least privilege.
    *   **CRITICAL:** Instruct the user to copy the generated token immediately and store it securely, as it won't be shown again.
*   **Docker:** (Recommended Method) Docker must be installed and running. Check with `docker --version`.
*   **Go:** (Alternative Method) Go toolchain installed if building from source. Check with `go version`.
*   **Git:** (Alternative Method) Git installed if building from source. Check with `git --version`.

**Installation & Configuration Steps:**

1.  **Get PAT:** Ask the user to provide the GitHub PAT they generated. Store this securely for the configuration step.
2.  **Choose Method:** Ask the user which installation method they prefer: `Docker` (recommended) or `Build from Source`.
3.  **Execute Installation & Determine Configuration:**
    *   **If `Docker`:**
        *   No separate installation command needed.
        *   `command`: `"docker"`
        *   `args`: `["run", "-i", "--rm", "-e", "GITHUB_PERSONAL_ACCESS_TOKEN=<USER_PAT>", "ghcr.io/github/github-mcp-server"]` (Replace `<USER_PAT>` placeholder during the update step).
        *   `env`: `{ "GITHUB_PERSONAL_ACCESS_TOKEN": "<USER_PAT>" }` (This is redundant with the `-e` arg but good practice for clarity in the config file).
    *   **If `Build from Source`:**
        *   Define install directory (e.g., `/home/jez/.local/share/Roo-Code/MCP/github-mcp-server`).
        *   Execute cloning:
            ```bash
            git clone https://github.com/github/github-mcp-server.git /home/jez/.local/share/Roo-Code/MCP/github-mcp-server
            ```
        *   Execute build:
            ```bash
            cd /home/jez/.local/share/Roo-Code/MCP/github-mcp-server/cmd/github-mcp-server && go build -o github-mcp-server
            ```
        *   Confirm success with the user.
        *   `command`: `"/home/jez/.local/share/Roo-Code/MCP/github-mcp-server/cmd/github-mcp-server/github-mcp-server"` (Full path to the built binary)
        *   `args`: `["stdio"]`
        *   `env`: `{ "GITHUB_PERSONAL_ACCESS_TOKEN": "<USER_PAT>" }` (Replace `<USER_PAT>` placeholder during the update step).
4.  **Optional Configuration:** Ask the user if they want to configure specific toolsets (`GITHUB_TOOLSETS`), enable dynamic toolsets (`GITHUB_DYNAMIC_TOOLSETS=1`), or specify a GitHub Enterprise host (`GITHUB_HOST`). Add these to the `env` object if provided.
5.  **Update MCP Settings:**
    *   Read the MCP settings file (`/home/jez/.config/Code/User/globalStorage/rooveterinaryinc.roo-cline/settings/mcp_settings.json`).
    *   Add or update the `github` server entry within the `mcpServers` object using the determined `command`, `args`, and `env` (replacing `<USER_PAT>` with the actual token). Ensure `disabled: false` and `alwaysAllow: []` are set.
        ```json
        {
          "mcpServers": {
            // ... other servers ...
            "github": {
              "command": <command_from_step_3>,
              "args": <args_from_step_3>,
              "env": {
                "GITHUB_PERSONAL_ACCESS_TOKEN": "USER_PROVIDED_PAT",
                // Add optional env vars from step 4 here if provided
              },
              "disabled": false,
              "alwaysAllow": []
            }
          }
        }
        ```
    *   Write the updated content back to the settings file.
6.  **Confirmation:** Inform the user that the `github` server has been configured and should be available.