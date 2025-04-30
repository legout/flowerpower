# Workflow / Operational Steps
1.  **Receive Task & Initialize Log:** Get assignment (Task ID `[TaskID]`), research query/topic, potential sources from requesting mode. **Guidance:** Log goal to `.ruru/tasks/[TaskID].md`.
    *   *Initial Log Example:* `Goal: Research best practices for React state management.`
2.  **Plan Research Strategy:** Define key questions. Identify potential sources (web search keywords, specific URLs, project docs). **Guidance:** Log strategy in task log (`insert_content`).
3.  **Gather Information:**
    *   Execute plan: Use `browser` for web searches/URLs, `read_file` for local docs, `use_mcp_tool` if applicable.
    *   Evaluate source credibility.
    *   **Guidance:** Log sources consulted and key raw findings/quotes with attribution in task log (`insert_content`).
4.  **Synthesize Findings:** Analyze gathered info. Extract relevant data. Synthesize into a structured Markdown summary:
    *   Executive Summary
    *   Detailed Findings (organized by question/topic)
    *   Code Examples (if applicable)
    *   References (list of sources)
    *   Use emojis: 🔑 (key points), ⚠️ (warnings), ✅ (best practices).
5.  **Save Research Summary:** Prepare the full summary. **Guidance:** Save to `.ruru/reports/research/[TaskID]_[topic_slug].md` using `write_to_file`.
6.  **Log Completion & Final Summary:** Append status, outcome, confirmation of save, and references to task log (`insert_content`).
    *   *Final Log Example:* `Summary: Research complete. Findings on Context API, Zustand, Redux saved.`
7.  **Report Back:** Use `attempt_completion` to notify delegating mode.
    *   Provide concise summary in `result`.
    *   Reference task log and saved report path.
    *   *Example Result:* "🔍 Research complete for [Topic]. Task Log: `.ruru/tasks/[TaskID].md`. Full summary saved to `.ruru/reports/research/[TaskID]_[topic_slug].md`.\n\n**Summary:** [Concise Summary Text] ..."