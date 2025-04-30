+++
# --- Metadata ---
id = "PLAYBOOK-ADD-FEATURE-V1"
title = "Project Playbook: Adding a Major Feature to an Existing Application"
status = "published"
created_date = "2025-04-24"
updated_date = "2025-04-24"
version = "1.0"
tags = ["playbook", "documentation", "project-management", "feature", "existing-project", "integration", "epic", "task"]
related_docs = [
    ".ruru/docs/standards/project-management-strategy-v1.md",
    ".ruru/planning/project-structure/00-epic-feature-task-plan.md"
]
objective = "Provide a practical guide for planning, developing, and integrating a significant new feature into an existing application using the Roo Commander Epic-Feature-Task hierarchy."
scope = "Covers phases from understanding the existing context and feature requirements to implementation and integration testing."
target_audience = ["Users", "Project Managers", "Developers", "AI Modes"]
# --- Document Specific Fields ---
example_project_type = "Existing Web/Mobile/Backend Application"
+++

# Project Playbook: Adding a Major Feature to an Existing Application

This playbook outlines a recommended approach for adding a significant new feature to a pre-existing codebase using Roo Commander's Epic-Feature-Task hierarchy.

**Scenario:** You have an existing application in your workspace, and you want to add a major new piece of functionality (e.g., adding a reporting dashboard, implementing a new user role system, integrating a third-party API).

## Phase 1: Onboarding (If Necessary) & Feature Definition

1.  **Ensure Project Context:**
    *   **If Roo Commander is *new* to this project:** Initiate onboarding using the "📂 Analyze/Onboard the CURRENT project workspace" option. Follow the `manager-onboarding` prompts to ensure the Stack Profile and basic context are established.
    *   **If Roo Commander *has* worked on this project:** Briefly confirm the context is still relevant or ask `agent-context-resolver` to quickly summarize the current state if needed.

2.  **Define the New Feature (as Epic or Feature):**
    *   **Goal:** Clearly articulate the new feature's requirements and scope.
    *   **Action:** Work with `roo-commander` or `manager-product`. Decide if this new feature is large enough to warrant its own Epic or if it fits logically under an existing one.
        *   **If New Epic:** Create a new `EPIC-...md` file in `.ruru/epics/` defining the overall initiative. Then, create the primary `FEAT-...md` file for the feature itself in `.ruru/features/`, linking it to the new Epic (`epic_id`).
        *   **If Part of Existing Epic:** Create the new `FEAT-...md` file in `.ruru/features/`, linking it via `epic_id` to the relevant existing Epic. Update the existing Epic's `related_features` list.
    *   **Content:** In the `FEAT-...md` file, detail the `description`, user value, and specific `acceptance_criteria`. Set `status` to "Draft".

3.  **Initial Impact Analysis (Crucial):**
    *   **Goal:** Understand how the new feature interacts with or impacts the existing application architecture and codebase.
    *   **Action:** Delegate analysis tasks, potentially coordinated by `core-architect` or `roo-commander`.
    *   **Tasks (Examples):**
        *   "Analyze existing API endpoints related to [relevant area] and identify integration points for the new feature." (Delegate to `agent-context-resolver` or `dev-api` if specific mode exists).
        *   "Review the current database schema ([path/to/schema] or ask `lead-db`) and identify necessary modifications or additions for the [New Feature]." (Delegate to `lead-db` or `data-specialist`).
        *   "Identify existing UI components in [relevant path] that can be reused or need modification for the [New Feature] UI." (Delegate to `lead-frontend` or relevant framework specialist).
        *   "Assess potential security implications of adding [New Feature]." (Delegate to `lead-security`).
    *   **Output:** Add findings, potential risks, and dependencies to the Feature's (`FEAT-...md`) Markdown body or link to separate analysis documents/ADRs.

## Phase 2: Design & Task Breakdown

1.  **Refine Feature & Acceptance Criteria:**
    *   **Goal:** Finalize the feature definition based on the impact analysis.
    *   **Action:** Update the `FEAT-...md` file with refined requirements, clarified acceptance criteria, and potentially high-level technical approach decisions (informed by `core-architect` or leads). Create ADRs (`.ruru/decisions/`) for significant design choices.
    *   Set Feature `status` to "Ready for Dev".

2.  **Decompose Feature into Tasks:**
    *   **Goal:** Create granular, actionable tasks for implementation, considering the existing codebase.
    *   **Action:** `manager-project` or relevant Leads break down the Feature.
    *   **Process:** Similar to the greenfield playbook, but tasks must often account for existing code:
        *   Follow MDTM Task Creation workflow (Rule `04-mdtm-workflow-initiation.md`).
        *   Select specialists (`assigned_to`).
        *   **Set `feature_id` and `epic_id`** in Task metadata.
        *   **Task Examples:** "Modify `UserService.ts` to include new permission check", "Add `POST /reports` endpoint to existing API", "Create `ReportTable.vue` component reusing `BaseTable`", "Write integration tests between `OrderService` and new `ReportingService`", "Update database migration script to add `reports` table".
        *   Checklist items should reference specific existing files/modules where appropriate.
        *   Delegate tasks via `new_task` referencing the `TASK-...md` file path.
        *   Update the Feature's `related_tasks` list.

## Phase 3: Implementation & Tracking

1.  **Task Execution (with Context):**
    *   **Goal:** Implement the feature tasks, interacting with existing code.
    *   **Action:** Specialists execute tasks. **Crucially**, they must use `read_file` to understand the existing code they need to modify *before* generating changes (`apply_diff`, `search_and_replace`). They update their `TASK-...md` files.

2.  **Monitoring & Coordination:**
    *   **Goal:** Track progress, ensure correct integration, resolve issues.
    *   **Action:** `manager-project` / `roo-commander` monitor statuses. Handle blockers (Rule `05`).
    *   Code reviews (`util-reviewer`) become particularly important to catch unintended side effects on existing functionality.

3.  **Feature Status Update:**
    *   **Action:** `manager-project` updates the Feature file (`FEAT-...md`) status ("In Progress", "In Review", "Done") based on task completion and review outcomes.

## Phase 4: Integration Testing & Completion

1.  **Integration & End-to-End Testing:**
    *   **Goal:** Verify the new feature works correctly within the context of the whole application.
    *   **Action:** Define and delegate integration tests (`test-integration`) and end-to-end tests (`test-e2e`) that cover the interaction between the new feature and existing parts of the system. These can be defined as Tasks under the Feature.
    *   Execute tests and address any discovered regressions or integration bugs (potentially creating new `TASK-...md` files for fixes).

2.  **Final Review & Feature Completion:**
    *   **Action:** Once testing passes and reviews are complete, update the Feature status to "Done". Update the parent Epic's status if applicable.

## Key Considerations for Existing Projects:

*   **Context is King:** Effective onboarding or context resolution (Phase 1) is critical. Modes *must* be instructed to read existing code before modifying it.
*   **Impact Awareness:** The impact analysis step helps prevent breaking changes and identifies dependencies early.
*   **Testing Focus:** Integration and regression testing are more heavily emphasized than in greenfield projects.
*   **Refactoring:** Adding major features might reveal areas needing refactoring in the existing code. These could be spun off into separate Features/Tasks managed by `util-refactor`.

Adapt this playbook based on the specific feature's complexity and the nature of the existing application.