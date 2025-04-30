+++
id = "PRIME-RULE-RESEARCH-V1"
title = "Prime Coordinator: Rule - Research Procedure"
context_type = "rules"
scope = "Handling direct research requests"
target_audience = ["prime"]
granularity = "procedure"
status = "active"
last_updated = "2025-04-21"
tags = ["rules", "research", "browser", "mcp", "prime"]
related_context = ["01-operational-principles.md", "12-logging-procedures.md"]
+++

# Rule: Research Procedure

This rule defines how to handle direct requests for research, analysis, or information gathering.

**Procedure:**

1.  **Receive Request:** Understand the research question or information needed.
2.  **Clarify (If Needed):** Use `ask_followup_question` if the research scope is unclear or too broad.
3.  **Select Tools:** Choose appropriate tools (`browser`, `fetch`, specific MCP tools like Perplexity).
4.  **Execute Research:** Use the selected tools iteratively to gather the required information.
5.  **Synthesize Results:** Compile the findings into a clear, concise summary or report.
6.  **Log Action:** Log the research performed and key findings according to Rule `07` / KB `12`.
7.  **Report Results:** Present the synthesized results to the user using `attempt_completion`.