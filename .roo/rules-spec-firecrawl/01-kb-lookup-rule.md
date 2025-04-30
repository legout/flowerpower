+++
id = "KB-LOOKUP-SPEC-FIRECRAWL"
title = "KB Lookup Rule: Firecrawl Specialist"
context_type = "rules"
scope = "Mode-specific knowledge base access" # Added a reasonable scope
target_mode_slug = "spec-firecrawl"
kb_directory = ".ruru/modes/spec-firecrawl/kb/"
target_audience = ["spec-firecrawl"] # Added target audience
granularity = "ruleset"
status = "active"
last_updated = "2025-04-18" # Updated date
# version = ""
# related_context = []
tags = ["kb-lookup", "firecrawl", "rules"] # Added relevant tags
# relevance = ""
+++

# Knowledge Base Lookup Rule

This rule instructs the AI model operating in the specified `target_mode_slug` to consult the designated `kb_directory` for relevant information before responding to user queries or performing tasks.

**Purpose:** To ensure the mode leverages its specialized knowledge base for accuracy, consistency, and adherence to established guidelines or best practices documented within that KB.

**Mechanism:**

1.  **Identify Intent:** Before generating a response, the AI analyzes the user's request to determine if it relates to topics covered in the mode's knowledge base.
2.  **Consult KB:** If relevant, the AI searches the specified `kb_directory` (and its subdirectories) for pertinent Markdown files (`.md`).
3.  **Synthesize Information:** Information retrieved from the KB is integrated into the AI's reasoning process and response generation.
4.  **Prioritize KB:** Information from the KB should generally be prioritized over the AI's general knowledge when conflicts arise, especially regarding specific procedures, configurations, or established decisions for the mode's domain.

**Scope:** This rule applies specifically when the AI is operating under the mode defined by `target_mode_slug`.