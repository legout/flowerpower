+++
id = "RULE-SPEC-BUN-KB-LOOKUP-V1"
title = "Rule: spec-bun Knowledge Base Lookup"
context_type = "rules"
scope = "Defines how spec-bun should utilize its Knowledge Base"
target_audience = ["spec-bun"]
granularity = "procedure"
status = "active"
last_updated = "2025-04-26" # Use current date
tags = ["rules", "kb", "lookup", "spec-bun", "bun"]
related_context = [".ruru/modes/spec-bun/kb/"]
+++

# Rule: Knowledge Base Lookup for 🐇 Bun Specialist

**Objective:** To ensure the `spec-bun` mode effectively utilizes its dedicated Knowledge Base (KB) located at `.ruru/modes/spec-bun/kb/` when performing tasks.

**Procedure:**

1.  **Prioritize KB:** Before attempting to answer questions, generate code, or perform actions related to Bun, **MUST** first consult the files within the `.ruru/modes/spec-bun/kb/` directory. Start by reading the `README.md` file there to understand the structure and content of the available KB files.
2.  **Targeted Reading:** Based on the specific task or query, identify the most relevant KB file(s) (e.g., if asked about testing, look for files related to `bun test` or Jest compatibility). Use `read_file` to access their content.
3.  **Synthesize Information:** Integrate the information retrieved from the KB into your response or plan. Reference specific details or examples found in the KB where applicable.
4.  **Identify Gaps:** If the KB does not contain the necessary information, note this limitation. You may then proceed using your general knowledge or suggest further research (delegated by the coordinator) if appropriate for a "Deep Dive" context.
5.  **Continuous Improvement:** If significant gaps are identified or new best practices emerge, suggest updates to the KB (via the coordinator) to maintain its relevance and accuracy.
