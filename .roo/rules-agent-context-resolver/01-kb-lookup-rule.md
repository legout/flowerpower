+++
id = "KB-LOOKUP-AGENT-CONTEXT-RESOLVER"
title = "KB Lookup Rule: Agent Context Resolver"
context_type = "rules"
scope = "Mode-specific KB lookup configuration"
target_audience = ["agent-context-resolver"]
target_mode_slug = "agent-context-resolver"
kb_directory = ".ruru/modes/agent-context-resolver/kb"
granularity = "ruleset"
status = "active"
last_updated = "2025-04-18"
# version = ""
# related_context = []
tags = ["kb", "lookup", "context", "agent-context-resolver"]
# relevance = ""
+++

# Knowledge Base Lookup Rule

**Rule:** When responding to a user query or performing a task, this mode **MUST** prioritize searching its designated Knowledge Base (KB) directory before relying solely on its internal knowledge or general training data.

**KB Directory:** `.ruru/modes/agent-context-resolver/kb`

**Process:**

1.  **Identify Keywords:** Extract key concepts, terms, or entities from the user's request.
2.  **Search KB:** Search the specified `kb_directory` (and its subdirectories) for files or content matching the identified keywords. Prioritize files with relevant names or metadata.
3.  **Synthesize Information:** If relevant information is found in the KB, synthesize it to formulate the response or guide the task execution. Clearly indicate when information is derived from the KB.
4.  **Fallback:** If no relevant information is found in the KB, proceed using internal knowledge, clearly stating that the KB did not contain specific information on the topic.

**Rationale:** Ensures that mode-specific, curated knowledge is leveraged first, leading to more accurate, consistent, and contextually appropriate responses and actions.