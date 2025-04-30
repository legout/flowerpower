+++
# --- Basic Metadata (Standard AI Rule Template) ---
id = "STD-RULE-ERROR-HANDLING-V1-TPL" # Template ID
title = "Standard Rule Template: Error Handling Procedure"
context_type = "rules_template" # Indicate this is a template for rules
scope = "Defines standard error handling procedures for AI modes"
target_audience = ["all_modes"] # Applicable broadly, tailor during mode creation
granularity = "procedure"
status = "template" # Mark as template
last_updated = "2025-04-26" # Use current date
tags = ["template", "rules", "error-handling", "procedure", "reporting", "recovery"]
related_context = ["01_standard_interaction_style.md"] # Link to interaction style
template_schema_doc = ".ruru/templates/toml-md/16_ai_rule.README.md"
# relevance = "High: Ensures consistent error reporting and handling"

# --- Rule-Specific Fields (Placeholder for tailoring) ---
# Tailor these during mode creation based on the specific mode's role
# Example: Define specific error codes or escalation paths
# specific_error_codes = {}
# escalation_contact = "lead-..."
+++

# Standard Rule: Error Handling Procedure ([MODE NAME] - Tailor This Title)

**Objective:** To ensure errors encountered during task execution are handled consistently, reported clearly, and facilitate recovery.

**Procedure:**

1.  **Identify Error:** Recognize when a tool use fails, a command returns a non-zero exit code, generated output is invalid, or an unexpected situation prevents progress.
2.  **Log Error:** Record the error details (e.g., tool name, parameters used, error message, exit code, relevant context) in the designated logging location (e.g., MDTM task file, coordination log) as per Rule `08-logging-procedure-simplified.md`.
3.  **Report Error Clearly:** Inform the coordinator/user about the error using `<attempt_completion>` (if stopping) or `<ask_followup_question>` (if seeking immediate guidance).
    *   State clearly that an error occurred.
    *   Provide the specific error message received, if any.
    *   Mention the step or tool that failed.
    *   *(Self-Correction - Optional but Recommended):* Briefly state if you attempted any automatic recovery steps (e.g., retrying a command) and the outcome.
4.  **Suggest Next Steps (If Possible):** Based on the error, suggest potential next actions:
    *   Retry the step?
    *   Try an alternative approach?
    *   Request specific clarification or input?
    *   Abort the current task/sub-task?
    *   *(Tailor: Add mode-specific suggestions, e.g., "Check API key validity" for an API mode, "Validate input file format" for a data processing mode).*
5.  **Await Instruction:** Do not proceed with the original task path after a significant error unless explicitly instructed to retry or modify the approach by the coordinator/user.

**(Add Mode-Specific Error Handling Here):** *(Tailor this section. E.g., Define how to handle specific API rate limits, file-not-found errors during processing, or validation errors in generated code).*
