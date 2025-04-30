+++
id = "util-second-opinion-kb-lookup"
title = "KB Lookup Rule for util-second-opinion"
context_type = "rules"
scope = "Mode-specific rule for Knowledge Base consultation"
target_audience = ["util-second-opinion"]
granularity = "ruleset"
status = "active"
last_updated = "2025-04-19"
# version = "1.0"
# related_context = []
tags = ["kb-lookup", "util-second-opinion", "rules", "context"]
# relevance = "High"
target_mode_slug = "util-second-opinion"
kb_directory = ".ruru/modes/util-second-opinion/kb/"
+++

# Knowledge Base Consultation Rule

**Objective:** Ensure responses are informed by the mode's dedicated knowledge base.

**Rule:**

1.  **Identify Need:** Before formulating a response or taking significant action, determine if consulting specialized knowledge is necessary for the current task. This is especially true for tasks involving specific domain knowledge, established procedures, or mode-specific guidelines.
2.  **Consult KB:** Access and review the contents of your designated Knowledge Base (KB) directory: `.modes/util-second-opinion/kb/`. Pay close attention to files relevant to the current query or task.
3.  **Prioritize KB:** Information, instructions, or examples found within the KB should be given high priority and incorporated into your response or action plan.
4.  **Synthesize Information:** Combine relevant information from the KB with the current request context and your general capabilities.
5.  **Proceed if KB is Insufficient:** If the KB directory is empty, does not exist, or contains no relevant information for the specific task, proceed based on your core programming, the user's request, and general context. Clearly state if the KB lacked relevant information if it seems pertinent.
6.  **Do Not Hallucinate KB Content:** Never invent or assume information exists in the KB if it cannot be found.