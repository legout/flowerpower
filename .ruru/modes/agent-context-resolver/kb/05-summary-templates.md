# Summary Templates

Use these templates as a guide for structuring summaries. Adapt based on the specific query and available information. **Always cite sources accurately using workspace-relative paths.**

## Template: Task Status Summary

```markdown
**Context Summary (re: Task [TaskID]):**
*   🎯 **Goal:** [Extract goal/title from task TOML `title` or Markdown body] (from `[source_task_filepath]`)
*   📄 **Status:** [Extract status from task TOML `status`] (from `[source_task_filepath]`)
*   🧑‍💻 **Assigned:** [Extract assignee from task TOML `assigned_to`, if present] (from `[source_task_filepath]`)
*   📝 **Latest Update/Notes:** [Summarize recent activity or key notes from Markdown body, if available] (from `[source_task_filepath]`)
*   🧱 **Blockers:** [Summarize any noted blockers from Markdown body or status, if available] (from `[source_task_filepath]`)
*   ➡️ **Next Steps:** [Summarize any explicit next steps from Markdown body, if available] (from `[source_task_filepath]`)
*   🔗 **Related:** [List `related_docs` or `depends_on` from TOML, if relevant] (from `[source_task_filepath]`)
*   *(Note: [Mention any critical source files that couldn't be read, e.g., .ruru/planning/requirements.md])*
```

## Template: Decision Summary

```markdown
**Context Summary (re: Decision on [Topic]):**
*   💡 **Decision:** [Summarize the core decision made] (from `[source_adr_filepath]`)
*   📅 **Date:** [Extract date from ADR filename or metadata] (from `[source_adr_filepath]`)
*   🤔 **Context/Problem:** [Briefly summarize the problem addressed] (from `[source_adr_filepath]`)
*   ⚖️ **Options Considered:** [List options briefly, if available] (from `[source_adr_filepath]`)
*   ✅ **Justification:** [Summarize the key reasons for the decision] (from `[source_adr_filepath]`)
*   🚀 **Consequences/Implications:** [Summarize expected consequences] (from `[source_adr_filepath]`)
*   *(Note: [Mention any related planning docs that couldn't be read])*
```

## Template: Mode Capability Summary

```markdown
**Context Summary (re: Mode `[mode_slug]`):**
*   🎯 **Purpose:** [Summarize mode's primary function/description] (from `[source_mode_filepath.mode.md]`)
*   🛠️ **Key Capabilities:** [List 3-5 core capabilities from TOML `capabilities`] (from `[source_mode_filepath.mode.md]`)
*   🔄 **Typical Workflow:** [Summarize high-level workflow from custom instructions, if available] (from `[mode_custom_instructions_dir]/`)
*   📚 **Context/Knowledge:** [Mention key context files it uses, if listed in TOML `context_files`] (from `[source_mode_filepath.mode.md]`)
*   🔗 **Collaboration:** [Note key modes it interacts with, based on description or notes] (from `[source_mode_filepath.mode.md]`)
*   *(Note: [Mention if specific custom instruction files were unreadable])*
```

## Template: General Project Status Snippet

```markdown
**Project Status Snippet:**
*   **Overall Vision:** [Extract from `.ruru/planning/project_vision.md` or similar]
*   **Current Phase/Plan:** [Extract from `.ruru/planning/project_plan.md` or infer from active tasks]
*   **Recent Decisions:** [Summarize 1-2 key recent decisions from `.ruru/decisions/`]
*   **Active Blockers:** [Summarize any major blockers noted in recent `.ruru/tasks/` files]
*   *(Note: Based on reading [list key files read, e.g., .ruru/planning/project_plan.md, .ruru/decisions/ADR-005.md].)*
```

*(Adapt these templates. Prioritize conciseness and accurate source citation using relative paths.)*