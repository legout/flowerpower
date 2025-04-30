+++
id = "KB-MCP-MANAGER-UNSPLASH-V1.2" # Updated ID and Version
title = "KB: Install Unsplash MCP Server (using bun and direct env config)"
status = "active"
created_date = "2025-04-24"
updated_date = "2025-04-24" # Update date
version = "1.2" # Increment version
tags = ["kb", "agent-mcp-manager", "workflow", "mcp", "install", "unsplash", "configuration", "setup", "interactive", "api-key"] # Added api-key tag
owner = "agent-mcp-manager"
related_docs = [
    ".roo/rules-agent-mcp-manager/01-initialization-rule.md",
    ".roo/mcp.json",
    "https://github.com/shariqriazz/upsplash-mcp-server" # Added repo URL
    ]
objective = "To install and configure the Unsplash MCP server interactively."
scope = "Executed when the user selects the 'Install Unsplash Image Server' option."
roles = ["Agent (agent-mcp-manager)", "User"]
trigger = "User selection of '🖼️ Install Unsplash Image Server'."
success_criteria = [
    "Repository cloned successfully into `.ruru/mcp-servers/upsplash-mcp-server`.",
    "Dependencies installed successfully.",
    "User prompted for and provided `UNSPLASH_ACCESS_KEY`.",
    "API key obtained from user.",
    "Build process completed successfully.",
    "`.roo/mcp.json` updated correctly with the new server entry, including the API key in the `env` object."
    ]
failure_criteria = [
    "Git clone fails.",
    "Dependency installation fails.",
    "User cancels API key input.",
    "Build process fails.",
    "Agent fails to read/write/parse `.roo/mcp.json`."
    ]
target_audience = ["agent-mcp-manager"] # Added target audience
+++

# KB Procedure: Install Unsplash MCP Server

## 1. Objective 🎯
Install the `upsplash-mcp-server` from its GitHub repository, configure it with the necessary API key, build it, and update the central MCP configuration.

## 2. Preconditions🚦
*   `git` is installed and accessible in the environment's PATH.
*   `bun` is installed and accessible in the environment's PATH.

## 3. Procedure Steps 🪜

1.  **Define Variables:**
    *   `repo_url`: "https://github.com/shariqriazz/upsplash-mcp-server.git"
    *   `server_name`: "upsplash-mcp-server"
    *   `clone_dir`: ".ruru/mcp-servers"
    *   `target_dir`: ".ruru/mcp-servers/upsplash-mcp-server"
    *   `mcp_config_path`: ".roo/mcp.json"
    *   `env_file_path`: ".ruru/mcp-servers/upsplash-mcp-server/.env"

2.  **Clone Repository:**
    *   Inform the user: "Cloning the Unsplash MCP server repository..."
    *   Use `execute_command`: `git clone {{repo_url}} {{target_dir}}`
    *   Verify success (exit code 0). If fails, report error and stop.

3.  **Install Dependencies:**
    *   Inform the user: "Installing dependencies using bun..."
    *   Use `execute_command` with `cwd={{target_dir}}`: `bun install`
    *   Verify success (exit code 0). If fails, report error and stop.

4.  **Get API Key:**
    *   Use `ask_followup_question`:
        *   `question`: "Please provide your Unsplash Access Key. You can get one from the Unsplash Developer portal (https://unsplash.com/developers). It's required for the server to function."
        *   `follow_up`: `<suggest>Enter API Key here</suggest>` (Provide a placeholder suggestion, the user needs to paste their actual key).
    *   Store the user's response (the API key) securely in a temporary variable (e.g., `api_key`). Handle potential cancellation/refusal gracefully. If refused, inform the user the server won't work without it and stop.

5.  **Build Server:**
    *   Inform the user: "Building the server using bun..."
    *   Use `execute_command` with `cwd={{target_dir}}`: `bun run build`
    *   Verify success (exit code 0). If fails, report error and stop.

6.  **Update MCP Configuration (`.roo/mcp.json`):**
    *   Inform the user: "Updating the central MCP configuration..."
    *   Use `read_file` to get the current content of `{{mcp_config_path}}`.
    *   Parse the JSON content. Handle potential parsing errors.
    *   **Check if server already exists:** If an entry with `name: "upsplash-mcp-server"` already exists, inform the user and ask if they want to overwrite/update it or cancel. Proceed based on user choice.
    *   **Add/Update Server Entry:** Create/update the JSON object for the server:
        ```json
        {
          "name": "upsplash-mcp-server",
          "description": "Provides access to Unsplash images.",
          "command": "bun", // Use bun to run
          "args": [".ruru/mcp-servers/upsplash-mcp-server/build/index.js"], // Verified from package.json
          "env": { // Add API key directly to env object
            "UNSPLASH_ACCESS_KEY": "{{api_key}}" // Use the key obtained in Step 4
          },
          "alwaysAllow": { // Define default permissions - adjust as needed
            "tools": ["search_photos", "download_photo"], // Verified tool names
            "resources": []
          }
        }
        ```
        *   **Note:** The tool names were verified by inspecting the server code. The API key is directly included in the `env` object.
    *   Add the new/updated server object to the `servers` array in the parsed JSON.
    *   Use `write_to_file` to save the updated JSON back to `{{mcp_config_path}}`. Ensure proper JSON formatting.
    *   Verify success. If fails, report error and stop.

7.  **Report Completion:**
    *   Use `attempt_completion`: "Successfully installed and configured the Unsplash MCP server (`upsplash-mcp-server`). It has been added to `.roo/mcp.json`. You may need to reload extensions and/or VS Code for the changes to take full effect."

## 4. Rationale / Notes 🤔
*   This procedure uses `bun` for installation, build, and execution, as requested.
*   It interactively prompts for the essential `UNSPLASH_ACCESS_KEY` and adds it directly to the `env` object in `.roo/mcp.json`.
*   The run command path (`build/index.js`) and tool names (`search_photos`, `download_photo`) have been verified.
*   Error handling is included at each critical step.