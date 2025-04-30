# Context / Knowledge Base (Revised for TOML)

*   **MDTM-TOML System:** The Markdown-Driven Task Management system uses structured Markdown files with **TOML metadata** at the beginning to track tasks through their lifecycle. The rest of the file is standard Markdown/GFM.
*   **Task Statuses:** Standard statuses (e.g., `"🟡 To Do"`, `"🟢 Done"`) are defined in the MDTM documentation and used in the TOML `status` field.
*   **Directory Structure:** Tasks are organized in `.ruru/tasks/FEATURE_*/` directories.
*   **TOML Metadata:** Key fields like `id`, `title`, `status`, `type`, `priority`, `tags`, `depends_on`, `related_docs`, `assigned_to` are defined in the TOML block using `key = value` syntax. Arrays use `[...]`.
*   **Context Needs:** Refer to the following standard locations:
    *   `.ruru/templates/tasks/`: Standard MDTM task file templates **using TOML frontmatter**.
    *   `.ruru/docs/standards/status_values.md`: Documentation of status emojis and their meanings.
    *   `.ruru/docs/standards/mdtm_toml_schema_guide.md` (or `.toml`): A guide or schema defining the expected TOML structure and fields for MDTM tasks.
    *   `.ruru/docs/diagrams/`: Mermaid diagrams showing MDTM workflows.
    *   `.ruru/docs/guides/mdtm_best_practices_toml.md`: MDTM best practices focusing on TOML usage.
    *   `v7.0/modes/01x-director/project-manager/custom-instructions/mdtm_ai_toml_context.md`: The concise TOML context guide specifically created for AI modes (within this mode's specific instruction folder).