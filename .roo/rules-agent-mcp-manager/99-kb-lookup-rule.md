+++
id = "AGENT-MCP-MANAGER-RULE-KB-LOOKUP-V1"
title = "MCP Manager Agent: Rule - KB Lookup Trigger"
context_type = "rules"
scope = "Mode-specific knowledge base access conditions"
target_audience = ["agent-mcp-manager"]
granularity = "procedure"
status = "active"
last_updated = "2025-04-24" # Use current date
tags = ["rules", "kb-lookup", "knowledge-base", "context", "reference", "agent-mcp-manager"]
related_context = [
    ".ruru/modes/agent-mcp-manager/kb/",
    ".ruru/modes/agent-mcp-manager/kb/README.md",
    ".roo/rules-agent-mcp-manager/01-initialization-rule.md"
    ]
template_schema_doc = ".ruru/templates/toml-md/16_ai_rule.README.md"
relevance = "Critical: Defines how the mode accesses its specific procedures"
+++

# Rule: KB Lookup Trigger (MCP Manager Agent)

This rule defines when you **MUST** consult the detailed Knowledge Base (KB) located in `.ruru/modes/agent-mcp-manager/kb/`.

**Consult the KB When:**

1.  **Executing Installation:** After the user selects an installation or management option (Vertex AI, Unsplash, Custom URL) via the `01-initialization-rule.md`, you **MUST** read and follow the procedure defined in the corresponding KB file (e.g., `kb/install-vertex-ai.md`, `kb/install-custom-url.md`, `kb/check-updates.md`, `kb/check-updates.md`).
2.  **Checking Prerequisites:** Before starting any installation or update process or update process, consult the relevant KB file to identify the specific prerequisites (tools, authentication methods) required for that server/task.
3.  **Handling Configuration:** Refer to the KB file for guidance on what configuration details to prompt the user for and how to structure the `.env` file or update `.roo/mcp.json`.
4.  **Needing Specific Commands:** Use the KB file as the source for specific `git clone` URLs, `git pull` commands, dependency installation commands (`bun install`, `npm install`, etc.), or other necessary commands for a particular server type.

**Procedure for KB Lookup:**

1.  **Identify Target Document:** Determine the specific KB document needed based on the user's selected installation or management option (e.g., `install-vertex-ai.md`). Use the KB README (`.ruru/modes/agent-mcp-manager/kb/README.md`) for an overview if needed.
2.  **Use `read_file`:** Access the content of the target KB document.
3.  **Apply Information:** Follow the detailed steps, guidelines, and commands within the KB procedure to perform the requested action (install, update, etc.). Report any deviations or issues encountered back to the coordinator (`roo-commander`).

**Key Objective:** To ensure that specific, potentially complex installation and management procedures for different MCP servers are reliably executed by following the detailed instructions stored in the mode's Knowledge Base.