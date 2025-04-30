+++
# --- Metadata ---
id = "PLAYBOOK-NEW-WEB-APP-V1"
title = "Project Playbook: New Greenfield Web Application"
status = "published"
created_date = "2025-04-24"
updated_date = "2025-04-24"
version = "1.0"
tags = ["playbook", "documentation", "project-management", "web-application", "greenfield", "epic", "feature", "task"]
related_docs = [
    ".ruru/docs/standards/project-management-strategy-v1.md",
    ".ruru/planning/project-structure/00-epic-feature-task-plan.md"
]
objective = "Provide a practical guide on structuring and managing the development of a new web application from scratch using the Roo Commander Epic-Feature-Task hierarchy."
scope = "Covers typical phases from initial idea to feature implementation for a standard web app."
target_audience = ["Users", "Project Managers", "Developers", "AI Modes"]
# --- Document Specific Fields ---
example_project_type = "Standard CRUD Web Application (e.g., Blog, Simple SaaS)"
+++

# Project Playbook: New Greenfield Web Application

This playbook outlines a recommended approach for structuring and managing the development of a new web application using Roo Commander's Epic-Feature-Task hierarchy.

**Scenario:** You want to build a new web application (e.g., a task management app, a simple blog platform, a customer portal) from the ground up.

## Phase 1: Initialization & High-Level Planning

1.  **Start with Roo Commander:**
    *   Use the "🚀 Start a NEW project from scratch" option.
    *   Roo Commander delegates to `manager-onboarding`.
    *   Follow prompts from `manager-onboarding` to name the project, choose initial tech stack (or defer), and set up basic workspace structure (including `.roo`/`.ruru`). `manager-onboarding` creates the initial Stack Profile (`.ruru/context/stack_profile.json`).

2.  **Define the Core Epic:**
    *   **Goal:** Capture the overall vision of the application.
    *   **Action:** Work with `roo-commander` or `manager-product` to create the primary Epic file (e.g., `.ruru/epics/EPIC-001-task-management-app-v1.md`).
    *   **Content:** Define the `objective` (e.g., "Build a web application for users to manage personal tasks"), `scope_description` (key high-level capabilities), and initial `status` ("Planned").

3.  **Initial Feature Brainstorming (Epic Decomposition):**
    *   **Goal:** Break down the Epic into major user-visible functional areas (Features).
    *   **Action:** Work with `manager-product` / `core-architect`. Identify core features needed for an MVP (Minimum Viable Product) or V1.
    *   **Examples:**
        *   `FEAT-001-user-authentication.md` (Epic: EPIC-001)
        *   `FEAT-002-task-creation-viewing.md` (Epic: EPIC-001)
        *   `FEAT-003-task-editing-completion.md` (Epic: EPIC-001)
        *   `FEAT-004-project-organization.md` (Epic: EPIC-001)
        *   `FEAT-005-basic-ui-layout.md` (Epic: EPIC-001)
    *   **Process:** Create draft Feature files (`.ruru/features/`) using the template, linking each back to `epic_id: "EPIC-001"`. Update the Epic's `related_features` list. Set initial Feature `status` to "Draft".

4.  **High-Level Architecture & Setup (Optional but Recommended):**
    *   **Goal:** Define core technical choices and set up foundational infrastructure/tooling.
    *   **Action:** Delegate to `core-architect` or relevant Leads (`lead-devops`, `lead-backend`, `lead-frontend`).
    *   **Tasks (Examples):**
        *   Define core frameworks/libraries (update Stack Profile).
        *   Design high-level data model (`lead-db`).
        *   Set up CI/CD pipeline (`lead-devops`).
        *   Establish coding standards / linting (`util-eslint`).
        *   Create ADRs (`.ruru/decisions/`) for significant choices.

## Phase 2: Feature Definition & Task Breakdown

1.  **Prioritize & Refine Features:**
    *   **Goal:** Select a Feature (or small group) to work on for the next development cycle. Fully define its requirements.
    *   **Action:** Work with `manager-product` / `manager-project`. Update the chosen Feature file (`FEAT-...md`) with detailed `description` and clear `acceptance_criteria`. Change `status` to "Ready for Dev".

2.  **Decompose Feature into Tasks:**
    *   **Goal:** Create the specific, actionable tasks needed to implement the prioritized Feature.
    *   **Action:** `manager-project` or relevant Leads (`lead-frontend`, `lead-backend`, etc.) break down the Feature.
    *   **Process:** For each required task (UI component, API endpoint, database migration, test):
        *   Follow the MDTM Task Creation workflow (Rule `04-mdtm-workflow-initiation.md`).
        *   Select the correct specialist (`assigned_to`).
        *   **Crucially:** Set `feature_id` in the Task's TOML metadata. Set `epic_id` too.
        *   Define a clear task `title`, `description`, specific `acceptance_criteria` for the task, and initial `checklist` items.
        *   Delegate the task via `new_task` referencing the created `TASK-...md` file path.
        *   Update the Feature's `related_tasks` list.

## Phase 3: Implementation & Tracking

1.  **Task Execution:**
    *   **Goal:** Complete the individual tasks.
    *   **Action:** Assigned specialist AI modes execute their tasks, updating the checklist and status (`🟡 To Do` -> `🟢 Done` or `⚪ Blocked`) within their `TASK-...md` file. They report completion/blockers to their coordinator (`manager-project` or `roo-commander`).

2.  **Monitoring & Coordination:**
    *   **Goal:** Track progress and resolve issues.
    *   **Action:** `manager-project` / `roo-commander` monitor task statuses (using `read_file` on task files or potentially a future dashboard/query tool).
    *   Handle blocked tasks (following Rule `05` - simple fix or escalation).
    *   Review completed tasks (potentially delegating to `util-reviewer`). Change task status to `🟣 Review` or finalize.

3.  **Feature Status Update:**
    *   **Goal:** Reflect the progress of the Feature based on its tasks.
    *   **Action:** When all essential tasks for a Feature are moving towards completion or review, `manager-project` updates the Feature file (`FEAT-...md`) status (e.g., to "In Progress", then "In Review").
    *   Once all tasks are Done and reviewed, update Feature status to "Done".

## Phase 4: Iteration & Deployment (Simplified)

1.  **Select Next Feature:** Return to Phase 2, Step 1 to prioritize and define the next Feature.
2.  **Deployment Prep:** Once a meaningful set of Features (or an MVP) is "Done", initiate deployment planning (likely involving `lead-devops`). This could be its own Feature or part of an Epic.

## Key Roles (Typical):

*   **User:** Provides initial vision, requirements, priorities, and feedback.
*   **`roo-commander`:** Overall orchestration, initial setup delegation, high-level monitoring.
*   **`manager-onboarding`:** Initial project setup and context gathering.
*   **`manager-product`:** Epic/Feature definition, prioritization (can overlap with user).
*   **`core-architect`:** High-level technical design, technology choices.
*   **`manager-project` / Leads:** Feature decomposition, task management, specialist coordination.
*   **Specialists:** Task execution.

This playbook provides a template. Adapt the specific Epics, Features, and task breakdown based on the unique requirements of your web application. Consistent use of linking IDs (`epic_id`, `feature_id`) is vital for maintaining structure and traceability.