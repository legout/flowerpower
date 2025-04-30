+++
# --- Basic Metadata (Standard AI Rule Template) ---
id = "STD-RULE-KB-USAGE-V1-TPL" # Template ID
title = "Standard Rule Template: Knowledge Base (KB) Usage"
context_type = "rules_template" # Indicate this is a template for rules
scope = "Defines standard procedure for AI modes to utilize their KB"
target_audience = ["all_modes"] # Applicable broadly, tailor during mode creation
granularity = "procedure"
status = "template" # Mark as template
last_updated = "2025-04-26" # Use current date
tags = ["template", "rules", "kb", "knowledge-base", "lookup", "context"]
related_context = [] # Specific mode rules will link back here
template_schema_doc = ".ruru/templates/toml-md/16_ai_rule.README.md"
# relevance = "High: Ensures modes leverage their specific knowledge"

# --- Rule-Specific Fields (Placeholder for tailoring) ---
# Tailor these during mode creation based on the specific mode's role
# Example: Define the specific KB path
# kb_path = ".ruru/modes/[MODE_SLUG]/kb/"
+++

# Standard Rule: Knowledge Base (KB) Usage ([MODE NAME] - Tailor This Title)

**Objective:** To ensure this mode effectively utilizes its dedicated Knowledge Base (KB) located at `[KB_PATH - Tailor This]` when performing tasks.

**Procedure:**

1.  **Prioritize KB:** Before attempting to answer questions, generate code, or perform actions related to your specialization, **MUST** first consult the files within your designated KB directory: `[KB_PATH - Tailor This]`.
2.  **Consult README:** Start by reading the `README.md` file within the KB directory to understand its structure and the content of available files.
3.  **Targeted Reading:** Based on the specific task or query, identify the most relevant KB file(s) using the README and file names. Use `read_file` (or equivalent MCP tool) to access their content.
4.  **Synthesize Information:** Integrate the information retrieved from the KB into your response, plan, or generated artifacts. Reference specific details, examples, or procedures found in the KB where applicable.
5.  **Identify Gaps:** If the KB does not contain the necessary information for the current task, clearly state this limitation.
6.  **Fallback Strategy:** *(Tailor: Define fallback behavior. E.g., "Proceed using general knowledge," "Request specific research from the coordinator," "State inability to proceed without KB info").*
7.  **Continuous Improvement:** If significant gaps, inaccuracies, or outdated information are identified in the KB during your work, **MUST** suggest specific updates or additions to the coordinator to maintain the KB's relevance and accuracy.