+++
id = "data-mysql-kb-lookup"
title = "KB Lookup Rule for data-mysql"
context_type = "rules"
scope = "Mode-specific knowledge base guidance"
target_audience = ["data-mysql"]
granularity = "rule"
status = "active"
last_updated = ""
# version = ""
# related_context = []
tags = ["kb", "knowledge-base", "lookup", "data-mysql"]
# relevance = ""
target_mode_slug = "data-mysql"
kb_directory = ".ruru/modes/data-mysql/kb/"
+++

# Knowledge Base Lookup Rule for data-mysql

**Objective:** Ensure the `data-mysql` mode consistently utilizes its dedicated knowledge base before responding to user requests.

**Rule:**

1.  **Prioritize KB Check:** Before formulating any response or taking action on a user's request, **ALWAYS** first consult the contents of your dedicated Knowledge Base (KB) directory located at:
    *   `{{kb_directory}}` (which resolves to `.ruru/modes/data-mysql/kb/`)

2.  **Information Types:** Look for relevant information within the KB, including (but not limited to):
    *   Best practices for MySQL development and administration.
    *   Common query patterns and optimization techniques.
    *   Schema design guidelines.
    *   Troubleshooting steps for common MySQL issues.
    *   Specific project conventions or standards related to MySQL usage.
    *   Code snippets or example queries.
    *   Security considerations for MySQL.

3.  **Apply KB Knowledge:** If relevant information is found in the KB, integrate it into your response or actions. Prioritize the guidance and procedures documented in the KB.

4.  **Proceed if No KB Info:** If no relevant information is found in the KB after a thorough check, proceed with generating a response based on your general knowledge and the user's request.

5.  **Continuous Learning (Implicit):** While not an explicit action for the mode during a single turn, the existence of this rule implies that the KB is expected to be maintained and updated over time.

**Rationale:** Ensures the mode leverages curated, specific knowledge for consistency, accuracy, and adherence to best practices or project standards defined for its domain. Even if the KB is currently sparse, adhering to this lookup process establishes the correct operational pattern.