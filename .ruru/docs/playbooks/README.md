+++
# --- Metadata ---
id = "DOC-PLAYBOOKS-README-V1"
title = "README: Roo Commander Project Management Playbooks"
status = "published"
created_date = "2025-04-24"
updated_date = "2025-04-24"
version = "1.0"
tags = ["readme", "documentation", "playbook", "project-management", "workflow", "guide", "epic", "feature", "task", "strategy"]
related_docs = [
    ".ruru/docs/standards/project-management-strategy-v1.md",
    ".ruru/planning/project-structure/00-epic-feature-task-plan.md"
]
objective = "Provide an overview and index for the standardized project management playbooks used within the Roo Commander ecosystem."
scope = "Explains the purpose, structure, and usage of playbooks for various project types and capability demonstrations."
target_audience = ["Users", "Developers", "Project Managers", "Architects", "AI Modes"]
+++

# README: Roo Commander Project Management Playbooks

## 1. Introduction & Purpose

This directory (`.ruru/docs/playbooks/`) contains a collection of standardized **Project Playbooks**. These documents serve as practical guides and illustrative examples for applying Roo Commander's structured project management methodology, based on the **Epic -> Feature -> Task** hierarchy (detailed in `project-management-strategy-v1.md`), to common software development scenarios and capability demonstrations.

**Goals of these Playbooks:**

*   **Provide Concrete Examples:** Illustrate how to break down different types of projects (e.g., new apps, feature additions, refactoring, demos) into Epics, Features, and Tasks.
*   **Standardize Workflows:** Offer recommended sequences of actions, phases, and typical mode delegations for specific project types.
*   **Guide Users:** Help human users understand how to initiate and structure work effectively when interacting with Roo Commander.
*   **Inform AI:** Provide structured context for Roo Commander and its specialist modes, enabling them to better understand the context, objectives, and typical steps involved in various project types.
*   **Promote Best Practices:** Encourage consistent use of planning artifacts, testing, documentation, and security considerations within the Roo Commander ecosystem.

## 2. Core Methodology Reference

All playbooks build upon the foundational concepts defined in:

*   **`.ruru/docs/standards/project-management-strategy-v1.md`**: Defines the Epic, Feature, and Task artifacts, their purpose, and the overall hierarchical approach.
*   **`.ruru/planning/project-structure/00-epic-feature-task-plan.md`**: Outlines the planned implementation of the hierarchy system itself.
*   **`.roo/rules/04-mdtm-workflow-initiation.md`**: Details the mandatory process for creating and delegating individual Tasks using the MDTM format.

## 3. Using the Playbooks

*   **For Users:** Read the relevant playbook before starting a new project of a similar type to understand the suggested phases, steps, and how to interact with Roo Commander effectively.
*   **For AI Modes (Especially `roo-commander`):** When a user initiates a project that matches a playbook scenario, consult the corresponding playbook to guide the planning, decomposition, and delegation process. Use it as a template for structuring the work, identifying necessary steps, and selecting appropriate specialist modes. Adapt the playbook based on specific user requirements.

## 4. Available Playbooks

*(Note: Filenames use hyphens. IDs and titles reflect the content.)*

*   **`01-playbook-new-web-app.md`** (ID: `PLAYBOOK-NEW-WEB-APP-V1`)
    *   **Title:** Project Playbook: New Greenfield Web Application
    *   **Summary:** Guides building a standard web app from scratch, covering initialization, core Epic/Feature definition, backend/frontend task breakdown, and basic setup. Assumes standard CRUD-like functionality.

*   **`02-playbook-add-major-feature.md`** (ID: `PLAYBOOK-ADD-FEATURE-V1`)
    *   **Title:** Project Playbook: Adding a Major Feature to an Existing Application
    *   **Summary:** Outlines adding significant new functionality to an existing codebase. Emphasizes context analysis, impact assessment, integration design, careful task decomposition considering existing code, and integration testing.

*   **`03-playbook-refactor-migration.md`** (ID: `PLAYBOOK-REFACTOR-MIGRATION-V1`)
    *   **Title:** Project Playbook: Technical Refactoring / Migration
    *   **Summary:** Focuses on large-scale technical improvements (framework upgrades, architectural changes). Stresses detailed analysis, strategic decomposition into testable features/chunks, rigorous verification, and documentation of changes.

*   **`04-playbook-research-prototype.md`** (ID: `PLAYBOOK-RESEARCH-POC-V1`)
    *   **Title:** Project Playbook: Research & Prototyping
    *   **Summary:** Structures exploratory work like technology evaluation or proof-of-concept building. Covers defining research questions, information gathering (using `agent-research`), optional prototype implementation, analysis, and documenting findings/recommendations.

*   **`05-playbook-cli-development.md`** (ID: `PLAYBOOK-CLI-DEV-V1`)
    *   **Title:** Project Playbook: Command-Line Interface (CLI) Tool Development
    *   **Summary:** Guides the creation of a Node.js-based CLI tool. Covers project setup (`package.json` with `bin` field, `tsconfig.json`), core structure (`commander.js`), implementing commands, build processes, and release preparation for npm.

*   **`06-playbook-user-authentication.md`** (ID: `PLAYBOOK-AUTH-SETUP-V1`)
    *   **Title:** Project Playbook: Implementing User Authentication
    *   **Summary:** Details setting up a core authentication system (signup, login, logout, sessions/JWTs, route protection). Covers design choices (custom vs. provider), data modeling, backend API implementation, frontend UI integration, and security considerations.

*   **`07-playbook-rest-api-crud.md`** (ID: `PLAYBOOK-API-CRUD-V1`)
    *   **Title:** Project Playbook: Developing a REST API Resource (CRUD)
    *   **Summary:** Focuses on the backend workflow for adding a new data resource with standard Create, Read, Update, Delete operations. Includes data modeling, API endpoint design, service/controller implementation, testing, and documentation.

*   **`08-playbook-ui-component-library.md`** (ID: `PLAYBOOK-UI-LIB-V1`)
    *   **Title:** Project Playbook: Building a Reusable UI Component Library
    *   **Summary:** Outlines creating shared UI components. Covers setup (including Storybook), design system integration, individual component development (implementation, testing, stories), and packaging for distribution.

*   **`09-playbook-ci-cd-setup.md`** (ID: `PLAYBOOK-CI-CD-SETUP-V1`)
    *   **Title:** Project Playbook: Setting up a CI/CD Pipeline
    *   **Summary:** Guides the automation of build, test, and deployment using platforms like GitHub Actions. Covers pipeline design, stage implementation (lint, test, build, deploy), artifact handling, containerization (optional), and secure secret management.

*   **`10-playbook-integrate-third-party-api.md`** (ID: `PLAYBOOK-API-INTEGRATION-V1`)
    *   **Title:** Project Playbook: Integrating a Third-Party API
    *   **Summary:** Details the process for integrating external services (e.g., payment, search). Covers API research, integration design (client vs. server), secure credential handling, implementation (SDKs, wrappers), testing (mocking), and data flow management.

*   **`11-playbook-frontend-state-management.md`** (ID: `PLAYBOOK-FE-STATE-MGMT-V1`)
    *   **Title:** Project Playbook: Frontend State Management Setup/Refactor
    *   **Summary:** Addresses selecting, implementing, or migrating frontend state solutions (Redux, Zustand, Pinia, etc.). Covers requirement analysis, library selection, store design (modules/slices), implementation/migration by domain, component integration, and testing.

*   **`12-playbook-performance-optimization.md`** (ID: `PLAYBOOK-PERF-OPT-V1`)
    *   **Title:** Project Playbook: Performance Optimization Audit & Fix
    *   **Summary:** Provides a systematic approach to improving application speed. Covers setting goals, baseline measurement, bottleneck analysis (frontend, backend, DB) using profiling tools, implementing targeted fixes, and verifying impact.

*   **`13-playbook-demo-interactive-dataviz.md`** (ID: `PLAYBOOK-DEMO-DATAVIZ-V1`)
    *   **Title:** Capability Playbook: Interactive Data Visualization
    *   **Summary:** Demonstrates creating complex, interactive visualizations (e.g., D3.js, Three.js). Covers data acquisition/prep, setting up the visualization environment, implementing core rendering, adding interactivity, and styling.

*   **`14-playbook-demo-generative-art-webpage.md`** (ID: `PLAYBOOK-DEMO-GENART-V1`)
    *   **Title:** Capability Playbook: Generative Art Web Page
    *   **Summary:** Showcases integrating AI-generated images (e.g., DALL-E) into a web page. Covers concept definition, prompt engineering, AI image generation (via specialist/MCP), frontend integration, and optional animation (`anime.js`).

*   **`15-playbook-demo-ai-code-explainer.md`** (ID: `PLAYBOOK-DEMO-CODE-EXPLAINER-V1`)
    *   **Title:** Capability Playbook: AI-Powered Code Explanation Tool
    *   **Summary:** Guides building a web tool where users paste code and get an AI-generated explanation, optionally with a Mermaid diagram visualization (`design-diagramer`). Covers UI setup, AI service integration, and diagram rendering.

*   **`16-playbook-demo-svg-logo-animation.md`** (ID: `PLAYBOOK-DEMO-SVG-ANIM-V1`)
    *   **Title:** Capability Playbook: Dynamic SVG Logo Animation
    *   **Summary:** Details animating an existing SVG logo using `design-animejs`. Covers SVG preparation (adding IDs/classes), defining the animation concept/sequence, implementation, triggering, and refinement.

*   **`17-playbook-demo-procedural-content-webpage.md`** (ID: `PLAYBOOK-DEMO-PROCGEN-V1`)
    *   **Title:** Capability Playbook: Procedural Content Generation (Web)
    *   **Summary:** Demonstrates creating a web page that dynamically generates text content (descriptions, bios) on demand using an LLM via an MCP server or specialist mode. Covers prompt design, UI setup, AI service integration, and result display.

*   **`18-playbook-demo-one-shot-recreation.md`** (ID: `PLAYBOOK-DEMO-ONESHOT-V1`)
    *   **Title:** Capability Playbook: 'One-Shot' Website Recreation
    *   **Summary:** Leverages the `design-one-shot` mode to attempt rapid visual recreation of a static website from a URL or description, focusing on demonstrating rapid prototyping.

*   **`19-playbook-demo-auto-readme.md`** (ID: `PLAYBOOK-DEMO-AUTO-README-V1`)
    *   **Title:** Capability Playbook: Automated README Generation from Code
    *   **Summary:** Guides analyzing a codebase (`agent-context-discovery`, `util-senior-dev`) and using `util-writer` to generate a draft `README.md` with standard sections like Installation and Usage.

*   **`20-playbook-setup-vite-react-ts-tanstack.md`** (ID: `PLAYBOOK-SETUP-VITE-REACT-TS-TANSTACK-V1`)
    *   **Title:** Project Playbook: Setup Vite + React + TypeScript + TanStack Query
    *   **Summary:** Initializes a Vite/React/TS project and integrates TanStack Query (React Query) for data fetching/caching, including provider setup.

*   **`21-playbook-setup-vite-react-ts-mui.md`** (ID: `PLAYBOOK-SETUP-VITE-REACT-TS-MUI-V1`)
    *   **Title:** Project Playbook: Setup Vite + React + TypeScript + Material UI (MUI)
    *   **Summary:** Initializes a Vite/React/TS project and integrates MUI Core, Emotion, and Material Icons, including optional basic theme setup.

*   **`22-playbook-setup-vite-react-ts-tailwind.md`** (ID: `PLAYBOOK-SETUP-VITE-REACT-TS-TAILWIND-V1`)
    *   **Title:** Project Playbook: Setup Vite + React + TypeScript + Tailwind CSS
    *   **Summary:** Initializes a Vite/React/TS project and configures Tailwind CSS, including PostCSS setup and directive injection.

*   **`23-playbook-setup-vite-react-ts-shadcn.md`** (ID: `PLAYBOOK-SETUP-VITE-REACT-TS-SHADCN-V1`)
    *   **Title:** Project Playbook: Setup Vite + React + TypeScript + Shadcn/UI
    *   **Summary:** Builds upon the Vite/React/TS/Tailwind setup by initializing Shadcn/UI using its CLI and adding an example component.

*   **`24-playbook-setup-vite-react-ts-antd.md`** (ID: `PLAYBOOK-SETUP-VITE-REACT-TS-ANTD-V1`)
    *   **Title:** Project Playbook: Setup Vite + React + TypeScript + Ant Design (Antd)
    *   **Summary:** Initializes a Vite/React/TS project and integrates Ant Design (antd) and its icons, including importing the necessary global CSS.

*   **`25-playbook-setup-react-native-expo-go.md`** (ID: `PLAYBOOK-SETUP-RN-EXPO-GO-V1`)
    *   **Title:** Project Playbook: Setup React Native Project (Expo Go)
    *   **Summary:** Guides initializing a React Native project using the Expo Go workflow via `create-expo-app`, suitable for quick starts and testing on physical devices.

## 5. Contributing New Playbooks

As new common project types or capability demonstrations emerge, new playbooks should be created following the structure and format of the existing ones. They should clearly define the scenario, outline the phases using the Epic-Feature-Task hierarchy where applicable, suggest relevant mode delegations, and highlight key considerations. Add new playbooks to the list in Section 4 of this README.