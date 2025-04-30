+++
id = "AGENT-MCP-KB-INSTALL-CUSTOM-URL-V1"
title = "Agent MCP Manager: KB - Install Custom Server from GitHub URL"
context_type = "knowledge_base"
scope = "Procedure for installing a custom MCP server from a GitHub repository"
target_audience = ["agent-mcp-manager"]
granularity = "procedure"
status = "active"
last_updated = "2025-04-27" # Use current date
tags = ["kb", "mcp", "install", "custom", "github", "agent-mcp-manager"]
related_context = [
    ".roo/rules-agent-mcp-manager/01-initialization-rule.md",
    "llms.json" # Assumed config file for servers
    ]
template_schema_doc = ".ruru/templates/toml-md/14_kb_procedure.README.md"
relevance = "High: Defines the custom GitHub installation process"
+++

# KB: Install Custom Server from GitHub URL

This document outlines the procedure for installing a custom MCP server hosted in a GitHub repository.

**Procedure:**

1.  **Get GitHub URL:**
    *   Use `<ask_followup_question>` to ask the user: "Please provide the full HTTPS or SSH URL for the GitHub repository containing the custom MCP server."
    *   Provide suggestions like:
        *   `https://github.com/example-user/my-mcp-server.git`
        *   `git@github.com:example-user/my-mcp-server.git`
        *   `Cancel Installation`
    *   Await user input. If cancelled, report cancellation and stop.
    *   Store the provided URL. Validate it looks like a plausible git URL (basic check). If invalid, re-prompt or report failure.

2.  **Determine Target Directory:**
    *   Extract a repository name from the URL (e.g., `my-mcp-server` from `https://github.com/example-user/my-mcp-server.git`). Sanitize the name if necessary (remove `.git`, replace invalid characters).
    *   Define the target installation path: `.ruru/mcp-servers/custom/[sanitized-repo-name]`.

3.  **Clone Repository:**
    *   Use `<execute_command>` to run: `git clone [PROVIDED_URL] [TARGET_DIRECTORY_PATH]`
    *   Example: `git clone https://github.com/example-user/my-mcp-server.git .ruru/mcp-servers/custom/my-mcp-server`
    *   Check the command result. If cloning fails, report the error and stop.

4.  **Run Installation Steps (If Applicable):**
    *   Use `<ask_followup_question>` to ask the user: "Does this server require installation steps (e.g., `npm install`, `pip install -r requirements.txt`)? If so, please provide the command(s) to run within the '[TARGET_DIRECTORY_PATH]' directory. Otherwise, select 'No installation needed'."
    *   Provide suggestions:
        *   `npm install`
        *   `pip install -r requirements.txt`
        *   `bun install`
        *   `No installation needed`
        *   `Cancel Installation`
    *   If the user provides commands:
        *   Use `<execute_command>` with the `cwd` parameter set to `[TARGET_DIRECTORY_PATH]` to run the specified command(s). Handle potential multiple commands using appropriate OS chaining (Rule `05-os-aware-commands.md`).
        *   Check command results. Report errors if they occur.
    *   If the user selects "No installation needed" or cancels, proceed.

5.  **Register Server (Requires Coordination):**
    *   **CRITICAL:** This step involves modifying `llms.json` (or the central MCP server configuration file). This agent **cannot** directly modify `llms.json`.
    *   Use `<ask_followup_question>` to inform the user: "The server code has been cloned to '[TARGET_DIRECTORY_PATH]' and installation steps (if any) were run. To complete the setup, the server needs to be registered in the main configuration (`llms.json`). Please provide the necessary details:"
    *   Ask for:
        *   `server_name`: A unique name for this server (e.g., `my-custom-server`).
        *   `start_command`: The command to start the server (e.g., `node index.js`, `python main.py`, `bun run start`). This command will be run from the server's directory (`[TARGET_DIRECTORY_PATH]`).
        *   `type`: The server type (`stdio` or `sse`).
    *   Provide example suggestions for the user to adapt.
    *   Once details are gathered, **report these details back to the coordinator** (`prime-coordinator` or `roo-commander`) using `<attempt_completion>`. State clearly that the next step is for the coordinator (or a delegated specialist like `prime-dev`) to update `llms.json` with the provided `server_name`, `start_command` (relative to its directory), and `type`.

6.  **Final Report:** After reporting the registration details to the coordinator, the agent's part in *this specific KB procedure* is complete. The final registration is handled externally.