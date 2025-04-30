+++
id = "data-dbt-kb-lookup"
title = "KB Lookup Rule for data-dbt"
context_type = "rules"
scope = "Knowledge Base Consultation"
target_audience = ["data-dbt"]
granularity = "ruleset"
status = "active"
last_updated = "2025-04-19" # Assuming current date based on environment details
tags = ["kb", "knowledge-base", "lookup", "data-dbt", "rules"]
kb_directory = ".ruru/modes/data-dbt/kb/" # Custom field for clarity
+++

# Rule: Consult Knowledge Base Before Execution

**Applies To:** `data-dbt` mode

**1. Prioritize Internal Knowledge:**
Before starting any task, especially complex ones involving dbt concepts, project structure, best practices, or specific configurations, **you MUST first consult your dedicated Knowledge Base (KB) directory:** `.ruru/modes/data-dbt/kb/`.

**2. Search Strategy:**
*   Review the `README.md` in the KB directory for an overview of available documents.
*   Identify KB files relevant to the current task based on their titles and content (e.g., files covering dbt modeling patterns, testing strategies, project conventions, SQL style guides, specific tool usage).
*   Thoroughly read the relevant KB documents to understand established principles, procedures, and constraints.

**3. Application:**
*   Integrate the knowledge gained from the KB into your planning and execution.
*   Adhere strictly to any guidelines, standards, or constraints defined within the KB.
*   If the KB provides specific instructions or code snippets relevant to the task, prioritize using them.

**4. Handling Missing Information:**
*   If the KB does not contain information relevant to the current task, proceed using your general knowledge and the project context.
*   If you identify a knowledge gap that should be documented, make a note to suggest creating or updating a relevant KB article upon task completion.

**Rationale:** Consulting the KB ensures consistency, adherence to project standards, and leverages curated knowledge specific to the `data-dbt` domain within this project, even if the KB is currently under development.