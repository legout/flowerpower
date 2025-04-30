# 12 - Central Logging Procedures

This document provides the consolidated, standard procedures for logging events, decisions, and actions within the Roo Commander operational context. Adherence to these procedures is crucial for maintaining state, ensuring traceability, and facilitating coordination.

**Core Principle:** Log significant events promptly and accurately in the designated locations using the appropriate tools. (Ref: `01-operational-principles.md` - "Logging Diligence").

**1. Events Triggering Logging:**

Log entries should be created for, but not limited to, the following events:

*   **Task Creation:** When Roo Commander initiates its own coordination task.
*   **Delegation:** When a task (simple or MDTM) is delegated to a specialist mode.
*   **Specialist Selection Rationale:** Justification for choosing a specific specialist.
*   **Significant Decisions:** Recording the outcome and rationale for architectural, strategic, or technical choices (often via ADRs).
*   **Error/Failure Detection:** When an error, failure, blocker, or safety violation is detected (from specialist reports or monitoring).
*   **Error Resolution Steps:** Decisions made and actions taken in response to errors.
*   **Escalations:** When an issue is escalated to another mode (e.g., `dev-solver`, `core-architect`).
*   **User Confirmation/Instruction:** When explicit user confirmation or instruction is received for sensitive operations or footgun usage.
*   **Workflow/Process Creation/Update:** When a new workflow or process document is created or significantly modified, including the update to the corresponding index file.
*   **Task Completion/Status Updates:** Significant milestones or status changes in ongoing tasks.
*   **Coordination Actions:** Managing dependencies, handling interruptions, re-delegating stalled tasks.

**2. Standard Logging Locations & Naming Conventions:**

*   **Commander's Task Log:**
    *   **Location:** `.ruru/tasks/`
    *   **Naming:** `TASK-CMD-YYYYMMDD-HHMMSS.md` (Created at the start of a significant coordination effort).
    *   **Content:** Primary log for Commander's actions, decisions, delegations, monitoring notes, rationales, and coordination efforts related to a specific user request or workflow. Use Markdown headings for structure.
*   **Specialist MDTM Task Files:**
    *   **Location:** `.ruru/tasks/`
    *   **Naming:** `TASK-[MODE]-[YYYYMMDD-HHMMSS].md` (Created by Commander for MDTM delegation).
    *   **Content:** Contains the detailed checklist and status updates managed primarily by the assigned specialist mode. Commander may append coordination notes if necessary.
*   **Architecture Decision Records (ADRs):**
    *   **Location:** `.ruru/decisions/`
    *   **Naming:** `YYYYMMDD-brief-topic-summary.md`
    *   **Content:** Formal record of significant architectural, technological, or strategic decisions, following the structure outlined in `06-documentation-logging.md`.
*   **General Logs (e.g., Command Output):**
    *   **Location:** `.ruru/logs/`
    *   **Naming:** Descriptive, e.g., `YYYYMMDD-HHMMSS-npm-install.log`, `build-output-[timestamp].log`.
    *   **Content:** Raw output from commands (`execute_command`), build processes, etc. Often generated automatically or via explicit redirection.
*   **Planning Documents:**
    *   **Location:** `.ruru/planning/`
    *   **Naming:** Descriptive, e.g., `project_plan_v1.md`, `feature-X-strategy.md`.
    *   **Content:** High-level plans, strategies, notes. While not strictly logs, they record planning decisions and context.

**3. Appropriate Tools for Logging:**

*   **`write_to_file`:**
    *   Use for creating *new* log files, such as:
        *   The initial Commander Task Log (`.ruru/tasks/TASK-CMD-... .md`).
        *   New ADRs (`.ruru/decisions/... .md`).
        *   New MDTM Task Files (`.ruru/tasks/TASK-[MODE]-... .md`).
        *   New planning documents (`.ruru/planning/... .md`).
    *   **Caution:** Avoid using `write_to_file` to overwrite existing log files unless intentionally replacing the entire content (rare for logs).
*   **`append_to_file`:**
    *   Use for adding chronological entries to the *end* of existing log files, such as:
        *   Adding raw output to general logs (`.ruru/logs/... .log`).
        *   Potentially adding simple, timestamped status updates to the end of Commander or specialist task logs if structure allows.
*   **`insert_content` (or `apply_diff` / `search_and_replace` for structured updates):**
    *   **Preferred** for adding structured entries *within* existing Markdown-based logs (Commander Task Logs, MDTM Task Files).
    *   Use to add new list items, update sections under specific headings, or modify checklist statuses (`- [⏳]` -> `- [✅]`).
    *   Requires careful specification of the insertion point or search/replace parameters. Use `read_file` first if unsure of the exact content/structure to modify.