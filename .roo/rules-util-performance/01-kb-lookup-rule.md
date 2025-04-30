+++
id = "util-performance-kb-lookup"
title = "KB Lookup Rule for util-performance"
context_type = "rules"
scope = "Mode-specific knowledge base access"
target_audience = ["util-performance"]
granularity = "ruleset"
status = "active"
last_updated = "2025-04-19" # Assuming today's date
# version = ""
# related_context = []
tags = ["kb-lookup", "util-performance", "rules"]
# relevance = ""

# --- KB Lookup Specific Fields ---
target_mode_slug = "util-performance"
kb_directory = ".ruru/modes/util-performance/kb/"
+++

# Knowledge Base Lookup Rule

Before responding to a user request, ALWAYS check your dedicated Knowledge Base (KB) directory at `.modes/util-performance/kb/` for relevant information, guidelines, examples, or procedures.

Consult the `README.md` file within that directory first for an overview of the available knowledge.

Incorporate any relevant findings from your KB into your response. Even if the KB is currently empty or sparse, performing this check is a required step in your process.