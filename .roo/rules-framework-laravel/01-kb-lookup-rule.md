+++
id = "framework-laravel-kb-lookup"
title = "KB Lookup Rule for framework-laravel"
context_type = "rules"
scope = "Mode-specific knowledge base guidance"
target_audience = ["framework-laravel"]
granularity = "ruleset"
status = "active"
last_updated = "2025-04-19" # Set to current date
# version = ""
# related_context = []
tags = ["kb-lookup", "framework-laravel", "rules"]
# relevance = ""
target_mode_slug = "framework-laravel"
kb_directory = ".modes/framework-laravel/kb/"
+++

# Knowledge Base Lookup Rule

**Objective:** Ensure consistent and accurate responses by leveraging curated knowledge specific to the `framework-laravel` mode.

**Rule:**

1.  **Prioritize KB:** Before generating any response or taking significant action based on a user request, **ALWAYS** first consult the contents of your dedicated Knowledge Base (KB) directory located at `.modes/framework-laravel/kb/`.
2.  **Search Strategy:**
    *   Identify keywords and concepts in the user's request.
    *   Look for files within the KB directory (`.modes/framework-laravel/kb/`) whose names or content match these keywords or concepts. Pay attention to `README.md` files for overviews.
    *   Prioritize information from files that seem most relevant to the specific task or question.
3.  **Apply KB Information:** If relevant information, guidelines, code snippets, examples, or procedures are found in the KB, **strictly adhere** to them in your response or action. Your primary goal is to act as an expert informed by this curated knowledge.
4.  **Handling Missing Information:** If, after a thorough check, the KB directory does not contain information relevant to the specific user request:
    *   Proceed using your general knowledge and capabilities.
    *   **Explicitly state** in your internal thinking process or reasoning (if applicable) that the KB was consulted but did not contain specific guidance for the request. For example: `<thinking>Checked KB at .modes/framework-laravel/kb/ for specific guidance on [topic], but found none. Proceeding with general knowledge.</thinking>`. This is crucial for identifying knowledge gaps.
5.  **Do Not Invent:** Do not invent KB content or claim the KB contains information it doesn't. Accuracy about the KB's contents is essential.

**Rationale:** This rule ensures that the mode consistently utilizes its specialized knowledge base, leading to more accurate, standardized, and context-aware interactions. It also helps identify areas where the KB needs expansion.