+++
# --- Metadata ---
id = "PLAYBOOK-FE-STATE-MGMT-V1"
title = "Project Playbook: Frontend State Management Setup/Refactor"
status = "published"
created_date = "2025-04-24"
updated_date = "2025-04-24"
version = "1.0"
tags = ["playbook", "documentation", "project-management", "frontend", "state-management", "refactor", "architecture", "redux", "zustand", "pinia", "ngrx", "svelte-stores", "epic", "feature", "task"]
related_docs = [
    ".ruru/docs/standards/project-management-strategy-v1.md",
    ".ruru/planning/project-structure/00-epic-feature-task-plan.md",
    ".ruru/modes/core-architect/core-architect.mode.md",
    ".ruru/modes/lead-frontend/lead-frontend.mode.md",
    # Add links to relevant framework specialists
]
objective = "Provide a structured process for selecting, implementing, or refactoring a frontend state management solution (e.g., Redux, Zustand, Pinia, NgRx) using the Roo Commander Epic-Feature-Task hierarchy."
scope = "Covers analyzing requirements, choosing a library, setting up the store, implementing/migrating state logic by domain, integrating components, testing, and documentation."
target_audience = ["Users", "Frontend Developers", "Architects", "AI Modes"]
# --- Document Specific Fields ---
example_project_type = "Frontend Application (React, Vue, Angular, Svelte) facing state complexity"
state_library_placeholder = "[LibraryName]" # e.g., "Redux", "Zustand", "Pinia"
+++

# Project Playbook: Frontend State Management Setup/Refactor

This playbook outlines a recommended approach for introducing or significantly changing the state management system in your frontend application using Roo Commander's Epic-Feature-Task hierarchy. Effective state management is crucial for maintainable and scalable frontend applications.

**Scenario:** Your application is experiencing state management challenges (e.g., excessive prop drilling, complex cross-component communication, inconsistent state updates) and needs a dedicated solution, or you are migrating from one state library to another.

## Phase 1: Analysis, Selection & Design

1.  **Define the State Management Need (Epic/Feature):**
    *   **Goal:** Articulate the problems with the current state handling (or the need for a dedicated system) and the goals of the new/refactored solution.
    *   **Action:** Create an Epic (for a major overhaul or initial setup) or a Feature (for refactoring a specific part), e.g., `.ruru/epics/EPIC-030-implement-global-state-management.md` or `.ruru/features/FEAT-100-refactor-user-state-to-[LibraryName].md`.
    *   **Content:** Define the `objective` (e.g., "Implement Zustand for global state management to simplify cross-component communication and improve state consistency", "Migrate legacy Vuex store to Pinia"), `scope_description` (which parts of the application state are targeted initially), current pain points, desired outcomes (e.g., improved dev experience, better performance). Set `status` to "Planned".

2.  **Research & Select Solution (Feature/ADR - If Choosing New):**
    *   **Goal:** Evaluate suitable state management libraries for the project's framework, scale, and team familiarity.
    *   **Action:** Define as a Feature (`FEAT-101-evaluate-state-libraries.md`). Delegate research tasks to `agent-research`, comparison/recommendation to `core-architect` or `lead-frontend`.
    *   **Tasks (Examples):**
        *   "Research pros/cons of [LibraryA] vs [LibraryB] vs [LibraryC] for [Framework]."
        *   "Analyze bundle size impact of each library."
        *   "Evaluate developer experience and ecosystem support (devtools, testing utils)."
        *   "Assess suitability for application complexity and team skills."
    *   **Output:** Create an ADR (`.ruru/decisions/`) documenting the chosen library (`[LibraryName]`) and the rationale.

3.  **Design Store Structure (Feature):**
    *   **Goal:** Plan the organization of the state store (e.g., single global store vs. modules/slices).
    *   **Action:** Define as a Feature (`FEAT-102-design-[LibraryName]-store-structure.md`). Delegate to `lead-frontend` or `core-architect`.
    *   **Tasks (Examples):**
        *   "Define main state domains/modules (e.g., `user`, `products`, `cart`, `ui`)."
        *   "Outline the state shape for each domain."
        *   "Define naming conventions for actions/mutations/reducers/selectors/getters."
        *   "Determine strategy for handling asynchronous actions (e.g., thunks, sagas, async actions)."
    *   **Output:** Document the agreed-upon structure in the Feature file or a dedicated design document.

## Phase 2: Setup & Implementation/Migration (Iterative)

1.  **Initial Library Setup (Feature):**
    *   **Goal:** Install the chosen library and configure its basic boilerplate.
    *   **Action:** Define as a Feature (`FEAT-103-setup-[LibraryName]-boilerplate.md`). Set `status` to "Ready for Dev". Decompose into Tasks.
    *   **Tasks (Examples - Delegate to Framework Specialist):**
        *   "Install `[LibraryName]` and any necessary peer dependencies (`npm install/yarn add/pnpm add`)."
        *   "Create main store configuration file (`store.js`/`ts`)."
        *   "Set up store provider/plugin in the application's entry point (`main.js`/`App.jsx`)."
        *   "Configure browser devtools extension for `[LibraryName]`."
    *   **Process:** Use MDTM workflow. Mark Feature "Done" when the basic store is integrated and visible in devtools.

2.  **Implement/Migrate State by Domain (Feature per Domain):**
    *   **Goal:** Gradually move application state into the new system, domain by domain.
    *   **Action:** For each major state domain identified in Phase 1 (e.g., 'user', 'cart'), create a Feature (e.g., `FEAT-104-implement-user-state-in-[LibraryName].md`). Set `status` to "Ready for Dev". Decompose into Tasks.
    *   **Tasks (Examples for 'User' domain):**
        *   "Define user state shape (interface/type) in the store." (Delegate to `util-typescript`)
        *   "Create user store module/slice/reducer." (Delegate to Framework Specialist)
        *   "Implement actions/mutations for `loginUser`, `logoutUser`, `updateUserProfile`."
        *   "Implement selectors/getters for `getCurrentUser`, `isAuthenticated`."
        *   "Refactor `LoginForm` component to dispatch `loginUser` action."
        *   "Refactor `UserProfile` component to read data using user selectors/getters."
        *   "Refactor Navbar component to use `isAuthenticated` selector."
        *   "(Migration Specific): Remove old state logic (e.g., Vuex module, local component state) related to user auth." (Delegate carefully to Framework Specialist)
        *   "Write unit tests for user actions and selectors/reducers." (Delegate to Framework Specialist or `test-integration`)
    *   **Process:** Use MDTM workflow. Specialists need to `read_file` existing components being refactored. Update Feature status iteratively.

## Phase 3: Integration, Testing & Finalization

1.  **Cross-Domain Integration Testing:**
    *   **Goal:** Ensure different parts of the state interact correctly and components update as expected.
    *   **Action:** Define as a Feature (`FEAT-110-state-integration-testing.md`) or add tasks to existing domain Features. Delegate to `test-integration` or `test-e2e`.
    *   **Process:** Write tests that involve state changes in one domain triggering expected effects or UI updates in components connected to other domains.

2.  **Refinement & Performance Checks:**
    *   **Goal:** Optimize selector performance, check for unnecessary re-renders.
    *   **Action:** Assign analysis tasks if performance issues are suspected. (Delegate to `util-performance`, `lead-frontend`).
    *   **Process:** Use framework devtools and state library devtools to profile component rendering and state updates. Refactor selectors or component subscriptions as needed (create new refactoring tasks).

3.  **Documentation:**
    *   **Goal:** Document the store structure, modules, key actions/selectors, and usage patterns.
    *   **Action:** Define as a Feature (`FEAT-111-state-management-documentation.md`). Delegate to `util-writer`.
    *   **Content:** Create documentation within the codebase (e.g., JSDoc/TSDoc) and/or in `.ruru/docs/frontend/` explaining the state management architecture and how developers should interact with the store.

4.  **Final Review & Epic Completion:**
    *   **Action:** Review the overall implementation and documentation. Mark relevant Features and the main State Management Epic as "Done".

## Key Considerations for State Management:

*   **Necessity:** Ensure a dedicated library is truly needed. Sometimes simpler solutions (Context API in React, provide/inject in Vue, simple Svelte stores) suffice for smaller apps. Document the *reason* for choosing a complex library.
*   **Boilerplate:** Be mindful of the boilerplate code associated with some libraries (e.g., Redux). Choose a library appropriate for the team's tolerance for boilerplate vs. convention.
*   **Modularity:** Design the store in modules or slices based on application domains to keep it organized and maintainable as the app grows.
*   **Selectors/Getters:** Use memoized selectors (like `reselect` for Redux, or built-in memoization) to prevent unnecessary computations and component re-renders.
*   **Asynchronicity:** Choose a clear pattern for handling async operations (fetching data, etc.) within your chosen library's ecosystem (e.g., Redux Thunk/Saga, `createAsyncThunk`, Pinia actions, Zustand middleware).
*   **DevTools:** Leverage the browser devtools extensions provided by most state management libraries for debugging.
*   **Testing:** Focus tests on the state logic (actions/reducers/mutations) and ensure components select and react to state changes correctly.

This playbook provides a roadmap for implementing or refactoring frontend state management, emphasizing careful design and iterative migration.