+++
id = "MCP-MGR-KB-INSTALL-ATLASSIAN-V1"
title = "Install MCP Server: Atlassian (sooperset)"
context_type = "knowledge_base"
scope = "Procedure for installing the mcp-atlassian server"
target_audience = ["agent-mcp-manager"]
granularity = "procedure"
status = "active"
last_updated = "2025-04-27" # Use current date
tags = ["kb", "mcp", "install", "atlassian", "jira", "confluence", "docker", "python", "api-key"]
related_context = ["README.md"]
template_schema_doc = ".ruru/templates/toml-md/14_kb_entry.md"
relevance = "High: Specific installation guide"
+++

# Procedure: Install MCP Server - Atlassian (sooperset)

This procedure guides the user through installing the `mcp-atlassian` server from sooperset. This server provides tools for interacting with Jira and Confluence (Cloud and Server/Data Center).

**Source:** <https://github.com/sooperset/mcp-atlassian>

**Prerequisites:**

*   **Docker:** Docker must be installed and running. Check with `docker --version`.
*   **Atlassian Account Details & API Tokens:**
    *   Determine if the user wants to connect to Cloud or Server/Data Center instances.
    *   **For Cloud:**
        *   Need Atlassian account email (`CONFLUENCE_USERNAME`, `JIRA_USERNAME`).
        *   Need Confluence Cloud URL (`CONFLUENCE_URL`, e.g., `https://your-domain.atlassian.net/wiki`).
        *   Need Jira Cloud URL (`JIRA_URL`, e.g., `https://your-domain.atlassian.net`).
        *   Need API Token(s): Guide user to <https://id.atlassian.com/manage-profile/security/api-tokens> to create token(s) (`CONFLUENCE_API_TOKEN`, `JIRA_API_TOKEN`). Emphasize copying the token immediately.
    *   **For Server/Data Center:**
        *   Need Confluence Server URL (`CONFLUENCE_URL`).
        *   Need Jira Server URL (`JIRA_URL`).
        *   Need Personal Access Token(s) (PAT): Guide user to their profile -> Personal Access Tokens to create token(s) (`CONFLUENCE_PERSONAL_TOKEN`, `JIRA_PERSONAL_TOKEN`). Emphasize copying the token immediately.

**Installation & Configuration Steps:**

1.  **Get Atlassian Config:** Ask the user for the necessary URLs, username (for Cloud), and API Tokens/PATs based on the services (Jira/Confluence) and deployment type (Cloud/Server) they want to connect.
2.  **Pull Docker Image:**
    *   Execute:
        ```bash
        docker pull ghcr.io/sooperset/mcp-atlassian:latest
        ```
    *   Confirm success.
3.  **Determine Configuration (Docker Method):**
    *   `command`: `"docker"`
    *   `args`: `["run", "-i", "--rm"]` (Environment variables will be added to `env` block). Add image name at the end: `ghcr.io/sooperset/mcp-atlassian:latest`.
    *   `env`: Build this object based on user input from Step 1. Only include variables for the services/deployment types being used. Example for Confluence Cloud + Jira Cloud:
        ```json
        {
          "CONFLUENCE_URL": "USER_CONFLUENCE_URL",
          "CONFLUENCE_USERNAME": "USER_EMAIL",
          "CONFLUENCE_API_TOKEN": "USER_CONFLUENCE_TOKEN",
          "JIRA_URL": "USER_JIRA_URL",
          "JIRA_USERNAME": "USER_EMAIL",
          "JIRA_API_TOKEN": "USER_JIRA_TOKEN"
          // Add optional vars like CONFLUENCE_SPACES_FILTER, JIRA_PROJECTS_FILTER, READ_ONLY_MODE="true" if requested
        }
        ```
4.  **Update MCP Settings:**
    *   Read the MCP settings file (`/home/jez/.config/Code/User/globalStorage/rooveterinaryinc.roo-cline/settings/mcp_settings.json`).
    *   Add or update the `atlassian` server entry within the `mcpServers` object using `command`, the full `args` list including the image name, and the constructed `env` object. Ensure `disabled: false` and `alwaysAllow: []` are set.
        ```json
        {
          "mcpServers": {
            // ... other servers ...
            "atlassian": {
              "command": "docker",
              "args": ["run", "-i", "--rm", "ghcr.io/sooperset/mcp-atlassian:latest"],
              "env": { // Populated from Step 3
                "CONFLUENCE_URL": "...",
                "CONFLUENCE_USERNAME": "...",
                "CONFLUENCE_API_TOKEN": "...",
                // etc.
              },
              "disabled": false,
              "alwaysAllow": []
            }
          }
        }
        ```
    *   Write the updated content back to the settings file.
5.  **Confirmation:** Inform the user that the `atlassian` server has been configured and should be available via their MCP client. Suggest refreshing the server list if needed.