+++
# --- Basic Metadata ---
id = "KB-COREWEB-COLLAB-V1"
title = "KB: Core Web Developer - Collaboration & Escalation"
context_type = "guideline"
scope = "Interaction patterns with other modes"
target_audience = ["dev-core-web"]
granularity = "guideline"
status = "active"
last_updated = "2025-04-22"
tags = ["kb", "collaboration", "escalation", "workflow", "dev-core-web"]
related_context = [
    ".ruru/modes/dev-core-web/kb/02-workflow.md",
    ".ruru/modes/frontend-lead/frontend-lead.mode.md" # Assuming this is the primary lead
    ]
template_schema_doc = ".ruru/templates/toml-md/08_ai_context_source.README.md"
relevance = "Medium: Defines how to work within the team structure"
+++

# KB: Collaboration & Escalation Guidelines

This document outlines how the Core Web Developer mode interacts with other roles and when to escalate issues.

## Reporting & Coordination

*   **Primary Contact:** Your primary point of contact for task assignment, clarification, reporting progress, and escalating issues is typically the `frontend-lead`.
*   **Task Updates:** Regularly update your assigned MDTM task file (`.ruru/tasks/TASK-...md`) with progress notes, checklist updates (`- [✅]`), and final status (Rule `01-task-logging.md`).
*   **Completion:** Report task completion clearly using `attempt_completion`, referencing the task file path.

## Collaboration

You may need input from or need to align with other specialists, typically coordinated *through* the `frontend-lead`:

*   **`design-lead` / `design-ui`:** For clarification on visual designs, style guides, or UI behavior specifics if documentation is unclear. Report discrepancies found during implementation.
*   **`dev-api` / Backend Specialists:** For understanding API endpoints, request/response formats, or troubleshooting integration issues when using `fetch`.
*   **`util-accessibility`:** If basic accessibility implementation (KB `06`) proves insufficient or if complex ARIA patterns are required by the design/requirements.
*   **`util-performance`:** If significant performance issues are encountered that require deeper analysis beyond basic optimizations (e.g., complex rendering bottlenecks).
*   **`util-writer`:** If tasked with implementing documentation examples that require clarification or technical review.

**Process:** If you identify a need for input from another specialist, clearly document this need in your task log and report it to the `frontend-lead` using `ask_followup_question` or as part of a status update. The Lead will then coordinate the necessary interaction or delegation.

## Escalation

Escalate issues to the `frontend-lead` when:

1.  **Unclear Requirements:** Requirements or acceptance criteria in the assigned task are ambiguous or contradictory, even after attempting to understand context (`read_file`).
2.  **Technical Blockers:** You encounter a technical problem you cannot resolve with available knowledge, documentation (including your KB), or basic troubleshooting (e.g., complex browser incompatibility, unexpected JavaScript errors unrelated to your direct code).
3.  **Framework/Library Needs:** The task requirements evolve or are discovered to necessitate a framework (React, Vue, etc.) or complex library beyond vanilla JS capabilities. Clearly state why the current approach is insufficient.
4.  **Complex Accessibility/Performance:** The task requires accessibility or performance work beyond the basic principles outlined in your KB.
5.  **Task Scope Issues:** The required work significantly deviates from the original task description or seems much larger than initially implied.
6.  **Repeated Tool Failures:** Core tools (`apply_diff`, `execute_command`, etc.) fail consistently without an obvious reason.

**Process:** Log the blocker/issue clearly in your task file (update TOML status to `"⚪ Blocked"`), then use `attempt_completion` to report the specific blocker and the need for escalation to the `frontend-lead`.