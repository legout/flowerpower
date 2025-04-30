+++
id = "MCP-MGR-KB-INSTALL-GDRIVE-V1"
title = "Install MCP Server: Google Drive"
context_type = "knowledge_base"
scope = "Procedure for installing the official Google Drive MCP server"
target_audience = ["agent-mcp-manager"]
granularity = "procedure"
status = "active"
last_updated = "2025-04-27" # Use current date
tags = ["kb", "mcp", "install", "google-drive", "gdrive", "files", "nodejs", "typescript", "oauth"]
related_context = ["README.md"]
template_schema_doc = ".ruru/templates/toml-md/14_kb_entry.md"
relevance = "High: Specific installation guide"
+++

# Procedure: Install MCP Server - Google Drive

This procedure guides the user through installing the official `gdrive` server from the `modelcontextprotocol/servers` repository. This server provides tools for interacting with Google Drive files, including Docs and Sheets.

**Source:** <https://github.com/modelcontextprotocol/servers/tree/main/src/gdrive> (Package: `@modelcontextprotocol/server-gdrive`)

**Prerequisites:**

*   **Node.js:** Latest LTS version recommended. Check with `node --version`.
*   **npm:** Bundled with Node.js. Check with `npm --version`.
*   **Git:** Required for cloning. Check with `git --version`.
*   **Google Cloud Project & OAuth Credentials:**
    *   Guide user to create a Google Cloud Project if needed.
    *   Guide user to enable **Google Drive API**, **Google Sheets API**, and **Google Docs API** for the project.
    *   Guide user to configure the **OAuth consent screen** (Internal user type is okay for testing). Add the `https://www.googleapis.com/auth/drive.readonly` scope.
    *   Guide user to create **OAuth 2.0 Client ID** for a **Desktop app**.
    *   Instruct user to **Download** the client secrets JSON file.

**Installation & Configuration Steps:**

1.  **Prepare OAuth Keys:**
    *   Ask the user for the path where they downloaded the OAuth keys JSON file.
    *   Instruct the user to rename the downloaded file to `gcp-oauth.keys.json`.
    *   Define a credentials directory (e.g., `/home/jez/.config/mcp-gdrive`). Ask the user to confirm or provide an alternative path. This path will be used for the `GDRIVE_CREDS_DIR` environment variable.
    *   Instruct the user to move the renamed `gcp-oauth.keys.json` file into this chosen directory. Record the chosen path.
2.  **Define Install Directory:** Suggest a standard location for the main repo, e.g., `/home/jez/.local/share/Roo-Code/MCP/mcp-servers-repo`. Confirm with the user or use the default.
3.  **Clone Repository (if not already cloned):**
    *   Check if the target directory exists.
    *   If not, execute cloning:
        ```bash
        git clone https://github.com/modelcontextprotocol/servers.git /home/jez/.local/share/Roo-Code/MCP/mcp-servers-repo
        ```
    *   Confirm success.
4.  **Install Dependencies:**
    *   Navigate to the gdrive server directory within the cloned repo:
        ```bash
        cd /home/jez/.local/share/Roo-Code/MCP/mcp-servers-repo/src/gdrive
        ```
    *   Execute dependency installation:
        ```bash
        npm install
        ```
    *   Confirm success.
5.  **Build Server:**
    *   Execute the build command (still in the `src/gdrive` directory):
        ```bash
        npm run build
        ```
    *   Confirm success. This should create a `dist` directory.
6.  **Authenticate Server:**
    *   Instruct the user to run the authentication command, providing the path to the credentials directory chosen in Step 1:
        ```bash
        GDRIVE_CREDS_DIR=/path/to/creds/dir node /home/jez/.local/share/Roo-Code/MCP/mcp-servers-repo/src/gdrive/dist auth
        ```
        (Replace `/path/to/creds/dir` with the actual directory path).
    *   Explain this will open a browser window for Google authentication. The user must authenticate with an account in the same organization as the Google Cloud project.
    *   Authentication credentials will be saved (likely in the `GDRIVE_CREDS_DIR`). Confirm with the user that authentication was successful.
7.  **Determine Configuration:**
    *   `command`: `"node"`
    *   `args`: `["/home/jez/.local/share/Roo-Code/MCP/mcp-servers-repo/src/gdrive/dist/index.js"]`
    *   `env`: `{ "GDRIVE_CREDS_DIR": "/path/to/creds/dir" }` (Use the actual path from Step 1).
    *   *(Note: Alternatively, the user could potentially use `npx -y @modelcontextprotocol/server-gdrive` if they prefer the published package, but the auth flow might differ slightly and needs the `GDRIVE_CREDS_DIR` env var set.)*
8.  **Update MCP Settings:**
    *   Read the MCP settings file (`/home/jez/.config/Code/User/globalStorage/rooveterinaryinc.roo-cline/settings/mcp_settings.json`).
    *   Add or update the `gdrive` server entry within the `mcpServers` object using the determined `command`, `args`, and `env`. Ensure `disabled: false` and `alwaysAllow: []` are set.
        ```json
        {
          "mcpServers": {
            // ... other servers ...
            "gdrive": {
              "command": "node",
              "args": ["/home/jez/.local/share/Roo-Code/MCP/mcp-servers-repo/src/gdrive/dist/index.js"],
              "env": {
                "GDRIVE_CREDS_DIR": "/path/to/user/chosen/creds/dir" // Use actual path
              },
              "disabled": false,
              "alwaysAllow": []
            }
          }
        }
        ```
    *   Write the updated content back to the settings file.
9.  **Confirmation:** Inform the user that the `gdrive` server has been configured and should be available via their MCP client after successful authentication. Suggest refreshing the server list if needed.