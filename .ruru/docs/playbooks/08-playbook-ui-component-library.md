+++
# --- Metadata ---
id = "PLAYBOOK-UI-LIB-V1"
title = "Project Playbook: Building a Reusable UI Component Library"
status = "published"
created_date = "2025-04-24"
updated_date = "2025-04-24"
version = "1.0"
tags = ["playbook", "documentation", "project-management", "ui", "component-library", "frontend", "design-system", "storybook", "epic", "feature", "task"]
related_docs = [
    ".ruru/docs/standards/project-management-strategy-v1.md",
    ".ruru/planning/project-structure/00-epic-feature-task-plan.md",
    # Add links to relevant framework/design modes
]
objective = "Provide a structured process for designing, building, testing, documenting, and potentially distributing a reusable UI component library using the Roo Commander Epic-Feature-Task hierarchy."
scope = "Covers the lifecycle from initial setup and design system definition to individual component implementation, documentation (using Storybook), and packaging."
target_audience = ["Users", "Frontend Developers", "UI/UX Designers", "AI Modes"]
# --- Document Specific Fields ---
example_project_type = "Standalone UI Library or Internal Design System for a Frontend Framework (React, Vue, Svelte, etc.)"
+++

# Project Playbook: Building a Reusable UI Component Library

This playbook outlines a recommended approach for creating a shared library of UI components, often developed in isolation using tools like Storybook and potentially published for reuse across projects, using Roo Commander's Epic-Feature-Task hierarchy.

**Scenario:** You need to create a standardized set of UI components (buttons, inputs, modals, etc.) based on a design system for consistent use in one or more frontend applications.

## Phase 1: Foundation & Setup

1.  **Define the Library Scope (Epic):**
    *   **Goal:** Establish the overall vision, target framework(s), and core goals for the component library.
    *   **Action:** Create the main Epic (e.g., `.ruru/epics/EPIC-015-core-design-system-components-v1.md`).
    *   **Content:** Define `objective` (e.g., "Create a reusable library of accessible, themeable UI components for [Framework] based on [Design System Name/Link]"), `scope_description` (initial set of components planned, target framework), core principles (accessibility, performance, testability). Set `status` to "Planned".

2.  **Project Setup & Tooling (Feature):**
    *   **Goal:** Initialize the library's codebase, build tooling, Storybook environment, and testing setup.
    *   **Action:** Define as a Feature (`FEAT-070-component-library-setup.md`), linked to the Epic.
    *   **Tasks (Delegate to `lead-frontend`, `util-vite`/`util-senior-dev`):**
        *   "Initialize new Node.js project (`npm init`, `yarn init`, or `pnpm init`)."
        *   "Install core framework ([React/Vue/Svelte]) and TypeScript dependencies."
        *   "Configure TypeScript (`tsconfig.json`) for library development."
        *   "Install and configure Storybook for [Framework]."
        *   "Install and configure testing framework (e.g., Vitest, Jest, Testing Library)."
        *   "Install and configure CSS framework/solution (e.g., Tailwind CSS, CSS Modules, Styled Components)."
        *   "Set up build process for library distribution (e.g., Vite library mode, Rollup)." (May be deferred)
        *   "Set up linting and formatting (ESLint, Prettier)."
    *   **Process:** Use MDTM workflow. Create ADRs for significant tooling choices. Mark Feature "Done" when basic setup is runnable.

3.  **Design System Integration & Theming (Feature):**
    *   **Goal:** Define how the library will implement the visual design system (colors, typography, spacing) and support theming (if required).
    *   **Action:** Define as a Feature (`FEAT-071-design-system-theming.md`). Delegate design tasks to `lead-design` or `design-*` specialists, implementation to `lead-frontend`.
    *   **Tasks (Examples):**
        *   "Define base theme variables (colors, fonts, spacing) in [CSS/TS/Config file]."
        *   "Implement theme provider/context (if needed)."
        *   "Document theming approach in `README.md` or contribution guide."
        *   "Create base CSS reset/normalization rules."

## Phase 2: Component Development Cycle (Iterative)

*For each component or logical group of components (e.g., "Form Controls"):*

1.  **Define Component(s) (Feature):**
    *   **Goal:** Specify the requirements, API, accessibility considerations, and visual design for a component or group.
    *   **Action:** Create a Feature file (e.g., `FEAT-072-implement-button-component.md`, `FEAT-073-implement-form-controls.md`), linked to the Epic.
    *   **Content:** Define `description` (purpose of the component(s)), `acceptance_criteria` (key functional and visual requirements), list props, events, slots (API), accessibility notes (ARIA attributes, keyboard navigation), link to design mockups. Set `status` to "Ready for Dev".

2.  **Implement Component (Tasks):**
    *   **Goal:** Build the component's structure, logic, and styling.
    *   **Action:** Decompose the Feature into Tasks.
    *   **Tasks (Examples for Button - Delegate to Framework Specialist, Design Specialist):**
        *   "Create `Button.jsx`/`.vue`/`.svelte` file structure."
        *   "Implement basic button markup and props (variant, size, disabled, onClick)."
        *   "Apply base styling using [Tailwind/CSS Modules/etc.] according to design specs."
        *   "Implement variant and size styling."
        *   "Implement disabled state styling and functionality."
        *   "Ensure accessibility attributes (`aria-disabled`, etc.) are applied correctly."
    *   **Process:** Use MDTM workflow, link tasks to the Feature. Specialists use `read_file` for design tokens/base styles.

3.  **Write Component Tests (Tasks):**
    *   **Goal:** Verify component functionality and rendering.
    *   **Action:** Create Tasks linked to the Feature.
    *   **Tasks (Examples - Delegate to Framework Specialist or `test-integration`):**
        *   "Write unit tests for Button component rendering variants and sizes."
        *   "Write tests for Button click handler invocation."
        *   "Write tests for Button disabled state."
        *   "Write accessibility checks (e.g., using `jest-axe`)."
    *   **Process:** Use MDTM workflow.

4.  **Create Storybook Stories (Tasks):**
    *   **Goal:** Document component usage and variations interactively.
    *   **Action:** Create Tasks linked to the Feature.
    *   **Tasks (Examples - Delegate to Framework Specialist or `util-writer`):**
        *   "Create `Button.stories.js`/`.ts`/`.mdx` file."
        *   "Write stories demonstrating different Button variants, sizes, and states (default, disabled, loading)."
        *   "Add controls (ArgsTable) for props in Storybook."
        *   "Write usage examples and documentation within the Storybook file."
    *   **Process:** Use MDTM workflow.

5.  **Code Review & Feature Completion:**
    *   **Action:** `lead-frontend` or `util-reviewer` reviews component code, tests, and stories. Update `TASK-...md` statuses. Once all tasks are done, update Feature (`FEAT-...md`) status to "Done".

*Repeat Phase 2 for all required components/groups.*

## Phase 3: Library Integration & Refinement

1.  **Internal Usage & Feedback:**
    *   **Goal:** Integrate early versions of components into consuming applications (if applicable) to gather feedback.
    *   **Action:** Define Features/Tasks for using the components in a pilot project. Document feedback.

2.  **Refinement & Bug Fixing:**
    *   **Goal:** Address feedback and fix bugs discovered during integration.
    *   **Action:** Create new Bug Features (`FEAT-...-fix-...`) or Refactoring Features (`FEAT-...-refactor-...`) as needed, breaking them down into tasks.

## Phase 4: Final Documentation & Release Prep (Optional)

1.  **Finalize Library Documentation:**
    *   **Goal:** Ensure comprehensive documentation beyond Storybook stories.
    *   **Action:** Define as a Feature (`FEAT-090-library-documentation.md`).
    *   **Tasks (Delegate to `util-writer`):**
        *   "Write/update the main library `README.md` (installation, usage, contribution guide)."
        *   "Generate API documentation from code comments/types (if using tools like TypeDoc)."
        *   "Ensure Storybook documentation is complete and well-organized."

2.  **Prepare for Publishing (Feature):**
    *   **Goal:** Configure `package.json` and build process for npm release.
    *   **Action:** Define as a Feature (`FEAT-091-npm-release-prep.md`).
    *   **Tasks (Delegate to `util-senior-dev`/`util-vite`):**
        *   "Verify library build configuration (Vite/Rollup) produces correct formats (ESM, CJS)."
        *   "Finalize `package.json` fields (`main`, `module`, `types`, `exports`, `peerDependencies`)."
        *   "Bump version number."
        *   "Create Git tag."
        *   "Manual Step: Publish to npm (`npm publish`)."

3.  **Update Epic Status:** Mark the main Component Library Epic as "Done" or ready for its first release.

## Key Considerations for Component Libraries:

*   **Design System:** Close collaboration with designers (`lead-design`, `design-ui`) is crucial.
*   **API Design:** Define clear, consistent, and predictable props, events, and slots. Good API design is key to reusability.
*   **Accessibility:** Build accessibility in from the start (semantic HTML, ARIA attributes, keyboard navigation). Delegate checks to `util-accessibility`.
*   **Testing:** Robust testing (unit, integration, potentially visual regression) is vital for library stability.
*   **Documentation (Storybook):** Storybook is invaluable for development, testing, and documentation. Make writing stories a standard part of the workflow.
*   **Build/Packaging:** Correctly configuring the build process and `package.json` is essential if distributing via npm.

This playbook provides a framework for building high-quality, reusable UI components with Roo Commander.