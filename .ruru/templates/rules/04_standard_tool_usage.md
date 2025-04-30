+++
# --- Basic Metadata (Standard AI Rule Template) ---
id = "STD-RULE-TOOL-USAGE-V1-TPL" # Template ID
title = "Standard Rule Template: Tool Preference & Usage"
context_type = "rules_template" # Indicate this is a template for rules
scope = "Defines standard preferences and procedures for tool usage"
target_audience = ["all_modes"] # Applicable broadly, tailor during mode creation
granularity = "guideline"
status = "template" # Mark as template
last_updated = "2025-04-26" # Use current date
tags = ["template", "rules", "tools", "mcp", "preference", "usage", "workflow"]
related_context = [
    "01_standard_interaction_style.md",
    "02_standard_error_handling.md",
    ".roo/rules/03-standard-tool-use-xml-syntax.md", # Workspace rule
    ".roo/rules/10-vertex-mcp-usage-guideline.md" # Workspace rule
    ]
template_schema_doc = ".ruru/templates/toml-md/16_ai_rule.README.md"
# relevance = "High: Ensures consistent and efficient tool usage"

# --- Rule-Specific Fields (Placeholder for tailoring) ---
# Tailor these during mode creation based on the specific mode's role
# Example: Define specific tool preferences or forbidden tools
# preferred_tools = ["apply_diff", "search_and_replace"]
# forbidden_tools = ["write_to_file"] # Example for a refactoring mode
+++

# Standard Rule: Tool Preference & Usage ([MODE NAME] - Tailor This Title)

**Objective:** To ensure efficient, safe, and consistent use of available tools according to workspace standards and mode-specific needs.

**General Guidelines:**

1.  **Tool Selection:** Choose the *most appropriate* tool for the specific task at hand, considering efficiency, safety, and the nature of the operation (e.g., reading, writing, searching, executing).
2.  **XML Syntax:** Strictly adhere to the standard XML syntax for all tool calls as defined in `.roo/rules/03-standard-tool-use-xml-syntax.md`.
3.  **Iterative Use:** Use tools one at a time and await the result before proceeding, as per `.roo/rules/06-iterative-execution-policy.md`. Do not chain multiple distinct operations within a single tool call unless the tool explicitly supports it (e.g., multiple edits in `apply_diff`).
4.  **Explain Intent:** Briefly explain *why* you are using a specific tool before invoking it.
5.  **Report Results:** Concisely report the outcome (success or failure) after receiving the tool result.

**Specific Tool Preferences & Usage:**

1.  **MCP Tools:**
    *   **Preference:** **MUST** prefer using tools provided by connected MCP servers (e.g., `vertex-ai-mcp-server`) over standard tools (`read_file`, `write_to_file`, `execute_command`, `search_files`) when an equivalent MCP tool exists and is available. Check the MCP server list and available tools provided in your context.
    *   **Fallback:** If a preferred MCP tool fails or the server is unavailable, **MUST** attempt the operation using the standard fallback tool (e.g., use `read_file` if `vertex-ai-mcp-server.read_file_content` fails). Report when fallback is used.
    *   **Output Handling:** Follow the guidelines in `.roo/rules/10-vertex-mcp-usage-guideline.md` regarding `save_*` vs. direct output tools.
2.  **File Reading:**
    *   Prefer `read_file` (or MCP equivalent) over `execute_command cat ...`.
    *   Use `start_line` and `end_line` parameters for large files when only a portion is needed.
3.  **File Writing/Editing:**
    *   **Small Changes/Replacements:** Prefer `apply_diff` or `search_and_replace` (or MCP `edit_file_content`) for targeted modifications to existing files. Ensure `SEARCH` blocks in `apply_diff` are exact matches (use `read_file` first if unsure).
    *   **Adding Content:** Use `insert_content` for adding new lines without modifying existing ones.
    *   **New Files/Overwrites:** Use `write_to_file` (or MCP `write_file_content`) only for creating new files or when a complete overwrite is necessary and intended. **Avoid** using `write_to_file` for minor edits to large existing files due to performance and risk.
4.  **Command Execution:**
    *   Use `execute_command` (or MCP equivalent) for CLI operations.
    *   Generate OS-aware commands based on `environment_details.os` as per `.roo/rules/05-os-aware-commands.md`.
    *   Prefer simple, non-interactive commands or correctly chained commands. Avoid generating complex shell scripts.
5.  **Searching:**
    *   Prefer `search_files` (or MCP equivalent) over `execute_command grep ...` for richer, context-aware results.

**(Add Mode-Specific Tool Preferences/Restrictions Here):** *(Tailor this section. E.g., "For refactoring, strictly prefer `apply_diff` over `write_to_file`," or "When interacting with [Specific API], always use the dedicated MCP tool `[mcp_server.tool_name]`").*