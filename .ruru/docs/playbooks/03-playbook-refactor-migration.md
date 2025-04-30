+++
# --- Metadata ---
id = "PLAYBOOK-REFACTOR-MIGRATION-V1"
title = "Project Playbook: Technical Refactoring / Migration"
status = "published"
created_date = "2025-04-24"
updated_date = "2025-04-24"
version = "1.0"
tags = ["playbook", "documentation", "project-management", "refactoring", "migration", "technical-debt", "upgrade", "epic", "feature", "task"]
related_docs = [
    ".ruru/docs/standards/project-management-strategy-v1.md",
    ".ruru/planning/project-structure/00-epic-feature-task-plan.md",
    ".ruru/modes/util-refactor/util-refactor.mode.md",
    ".ruru/modes/core-architect/core-architect.mode.md"
]
objective = "Provide a structured approach for planning, executing, and verifying large-scale technical refactoring, framework migrations, or major dependency upgrades using the Roo Commander Epic-Feature-Task hierarchy."
scope = "Covers analysis, planning, iterative implementation, testing, and verification for significant technical improvement initiatives."
target_audience = ["Users", "Technical Leads", "Architects", "Developers", "AI Modes"]
# --- Document Specific Fields ---
example_project_type = "Framework Upgrade (e.g., Vue 2->3), Language Version Upgrade (e.g., Python 2->3), Monolith Decomposition, Major Library Replacement"
+++

# Project Playbook: Technical Refactoring / Migration

This playbook outlines a recommended approach for managing significant technical refactoring or migration efforts using Roo Commander's Epic-Feature-Task hierarchy. These projects prioritize improving the codebase's internal structure, maintainability, performance, or underlying technology without necessarily adding new user-facing features initially.

**Scenario:** You need to undertake a large technical initiative like upgrading a core framework, migrating to a new architecture pattern, significantly restructuring a complex module, or replacing a fundamental library.

## Phase 1: Scoping, Analysis & Planning

1.  **Define the Initiative (Epic):**
    *   **Goal:** Clearly articulate the *why* and *what* of the refactoring/migration effort.
    *   **Action:** Work with `roo-commander`, `core-architect`, or relevant technical leads. Create a primary Epic (e.g., `.ruru/epics/EPIC-005-vue2-to-vue3-migration.md`).
    *   **Content:** Define the `objective` (e.g., "Migrate the frontend codebase from Vue 2 to Vue 3 to leverage Composition API and improve performance"), high-level `scope_description` (which parts of the application are affected), key motivations (technical debt, performance, security, maintainability), and anticipated benefits. Set initial `status` to "Planned".

2.  **Detailed Analysis & Impact Assessment:**
    *   **Goal:** Understand the full scope, risks, dependencies, and required changes across the codebase. *This is the most critical phase for refactoring/migration.*
    *   **Action:** This may constitute the first Feature(s) under the Epic, delegated to `core-architect`, `util-senior-dev`, or `agent-context-resolver`.
    *   **Tasks (Examples):**
        *   "Analyze codebase for usage of [Deprecated API/Library]." (Delegate to `agent-context-discovery` or `util-senior-dev` using search/analysis).
        *   "Identify all components/modules affected by the [Framework] upgrade."
        *   "Research migration paths and compatibility issues for [Library X] upgrade." (Delegate to `agent-research`).
        *   "Assess current test coverage for areas targeted for refactoring." (Delegate to `lead-qa` or `test-*` specialists).
        *   "Estimate effort and potential risks for the migration."
    *   **Output:** Detailed analysis reports, potentially stored in `.ruru/docs/analysis/` or linked from the Epic/Feature. Create ADRs (`.ruru/decisions/`) for key architectural decisions made during analysis (e.g., chosen migration strategy).

3.  **Define Refactoring/Migration Strategy (Feature Breakdown):**
    *   **Goal:** Break the large initiative into manageable, logical chunks (Features) based on the analysis. The goal is often to allow for iterative changes and testing.
    *   **Action:** `core-architect` and relevant Leads define the strategy.
    *   **Feature Examples (Vue 2->3 Migration):**
        *   `FEAT-030-setup-vue3-compat-build.md`
        *   `FEAT-031-migrate-core-utils-composables.md`
        *   `FEAT-032-migrate-authentication-module-vue3.md`
        *   `FEAT-033-migrate-product-listing-vue3.md`
        *   `FEAT-034-migrate-testing-library.md`
        *   `FEAT-035-final-cleanup-remove-compat.md`
    *   **Process:** Create Feature files (`.ruru/features/`) linking to the Epic. Define the `description` (what part of the refactoring this covers) and `acceptance_criteria` (e.g., "All tests pass for migrated module", "Component X renders correctly using Composition API", "Build uses Vite"). Set status to "Draft" or "Ready for Dev". Update Epic's `related_features`.

## Phase 2: Iterative Implementation & Verification

1.  **Prioritize & Prepare Feature:**
    *   **Goal:** Select the next Feature chunk to implement based on dependencies and strategy.
    *   **Action:** Finalize the `FEAT-...md` details. Ensure any necessary preparatory work (e.g., updating build tools from a previous feature) is complete. Set status to "Ready for Dev".

2.  **Decompose Feature into Refactoring Tasks:**
    *   **Goal:** Create granular technical tasks for the refactoring/migration work within the feature's scope.
    *   **Action:** Technical Leads or `util-senior-dev` decompose the Feature.
    *   **Process:**
        *   Follow MDTM Task Creation workflow (Rule `04`).
        *   Assign tasks primarily to `util-refactor`, framework specialists (e.g., `framework-vue`), or `util-senior-dev`.
        *   **Set `feature_id` and `epic_id`** in Task metadata.
        *   **Task Examples:** "Refactor `AuthStore.js` to use Pinia and Composition API", "Update `ProductCard.vue` template syntax for Vue 3", "Replace deprecated `EventBus` usage with `mitt` in `main.js`", "Configure Vite build settings for Vue 3 compatibility".
        *   Tasks *must* emphasize verifying that external behavior remains unchanged (unless the change is the specific goal, like a performance improvement benchmark). Acceptance Criteria should include "All related unit/integration tests pass".
        *   Delegate tasks via `new_task`.
        *   Update Feature's `related_tasks`.

3.  **Task Execution & Verification:**
    *   **Goal:** Perform the refactoring/migration safely and correctly.
    *   **Action:** Specialists execute tasks. They MUST:
        *   Carefully `read_file` of existing code.
        *   Apply changes using precise tools (`apply_diff`, `search_and_replace`).
        *   Run relevant tests (`unit`, `integration`) frequently. If tests are lacking, a prerequisite task might be to write them (`test-integration` specialist).
        *   Update `TASK-...md` status and checklist.

4.  **Monitoring & Code Review:**
    *   **Goal:** Track progress, ensure quality and behavioral equivalence.
    *   **Action:** `manager-project` / Leads monitor task statuses. Code reviews (`util-reviewer`) are **essential** for refactoring to catch subtle issues. Merge changes carefully, potentially using feature branches managed by `dev-git`.

5.  **Feature Status Update:**
    *   **Action:** Update `FEAT-...md` status ("In Progress", "In Review", "Done") based on task progress and reviews.

## Phase 3: Integration, Regression Testing & Completion

1.  **Post-Feature Integration Testing:**
    *   **Goal:** After a refactoring Feature is marked "Done", verify it hasn't negatively impacted other parts of the system.
    *   **Action:** Run broader integration (`test-integration`) and end-to-end (`test-e2e`) test suites. Address any regressions by creating new bug-fix tasks linked to the refactoring Feature/Epic.

2.  **Iterate or Finalize:**
    *   **Action:** If more refactoring Features remain in the Epic, return to Phase 2, Step 1.
    *   Once all Features are complete and regression testing passes, update the main Epic status to "Done".

3.  **Cleanup (Optional):**
    *   **Action:** Define and execute tasks for removing old code, compatibility layers, or temporary tooling related to the migration/refactoring.

## Key Considerations for Refactoring/Migration:

*   **Testing is Paramount:** Success hinges on having good test coverage *before* starting, or building it as part of the process. Tasks should frequently include "Run tests" or "Write necessary tests" as acceptance criteria.
*   **Iterative Approach:** Breaking the work into Features based on modules, layers, or specific APIs allows for incremental changes and testing, reducing risk compared to a "big bang" approach.
*   **Behavior Preservation:** The primary goal (unless explicitly stated otherwise, like a performance optimization) is to change the *internal* structure without altering *external* behavior. Code reviews and testing must focus on this.
*   **Tooling:** Leverage automated tools where possible (e.g., codemods, automated testing frameworks, linters configured for the target).
*   **Documentation:** Update relevant technical documentation (`.ruru/docs/`) as part of the process.

This playbook provides a framework for tackling large technical improvements systematically within Roo Commander.