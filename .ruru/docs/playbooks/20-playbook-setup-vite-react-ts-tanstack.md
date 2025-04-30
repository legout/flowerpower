+++
# --- Metadata ---
id = "PLAYBOOK-SETUP-VITE-REACT-TS-TANSTACK-V1"
title = "Project Playbook: Setup Vite + React + TypeScript + TanStack Query"
status = "published"
created_date = "2025-04-24"
updated_date = "2025-04-24"
version = "1.0"
tags = ["playbook", "documentation", "project-management", "setup", "vite", "react", "typescript", "tanstack-query", "frontend", "epic", "feature", "task"]
related_docs = [
    ".ruru/docs/standards/project-management-strategy-v1.md",
    ".ruru/planning/project-structure/00-epic-feature-task-plan.md",
    ".ruru/modes/util-vite/util-vite.mode.md", # If available
    ".ruru/modes/dev-react/dev-react.mode.md",
    ".ruru/modes/util-typescript/util-typescript.mode.md"
]
objective = "Guide the setup of a new frontend project using Vite, React, TypeScript, and TanStack Query (React Query) via Roo Commander."
scope = "Covers project initialization, dependency installation, basic TanStack Query provider setup, and verification."
target_audience = ["Users", "Frontend Developers", "AI Modes"]
# --- Document Specific Fields ---
example_project_type = "New Frontend Web Application"
project_name_placeholder = "[projectName]" # e.g., "my-react-app"
package_manager_placeholder = "[npm|yarn|pnpm]" # User choice or default
+++

# Project Playbook: Setup Vite + React + TypeScript + TanStack Query

This playbook outlines the steps to initialize a new frontend project using Vite with the React + TypeScript template and integrate TanStack Query for data fetching and caching.

**Scenario:** You are starting a new React project and want a modern, fast setup using Vite, TypeScript, and TanStack Query.

## Phase 1: Project Initialization

1.  **Define the Setup Goal (Epic/Feature):**
    *   **Goal:** Create a new Vite project configured with React, TypeScript, and TanStack Query.
    *   **Action:** Create a Feature (e.g., `.ruru/features/FEAT-230-setup-vite-react-ts-tanstack.md`). If part of a larger app, link to its Epic.
    *   **Content:** Define `objective`, specify target stack. Set `status` to "Planned".

2.  **Get Project Name & Package Manager (Coordinator Task):**
    *   **Goal:** Obtain necessary details from the user.
    *   **Tool:** `ask_followup_question`
    *   **Procedure:**
        ```xml
        <ask_followup_question>
         <question>Let's set up your Vite + React + TS + TanStack Query project.
         1. What do you want to name the project directory? (e.g., my-react-app)
         2. Which package manager do you prefer? (npm, yarn, pnpm)
         </question>
         <follow_up>
           <suggest>Project Name: [Suggest a name], Package Manager: npm</suggest>
           <suggest>Project Name: [Suggest a name], Package Manager: pnpm</suggest>
           <suggest>Cancel Setup</suggest>
         </follow_up>
        </ask_followup_question>
        ```
    *   Store user input as `[projectName]` and `[packageManager]`. Handle cancellation.

3.  **Initialize Vite Project (Coordinator Task):**
    *   **Goal:** Create the base project using the Vite CLI.
    *   **Tool:** `execute_command`
    *   **Procedure:**
        1.  Construct the command based on `[packageManager]`:
            *   npm: `npm create vite@latest [projectName] -- --template react-ts`
            *   yarn: `yarn create vite [projectName] --template react-ts`
            *   pnpm: `pnpm create vite [projectName] --template react-ts`
        2.  Explain: "Initializing Vite project `[projectName]` with React+TS template using `[packageManager]`..."
        3.  Execute: `<execute_command><command>[Vite Init Command]</command></execute_command>` (Run in parent directory).
        4.  Await result.
    *   **Error Handling:** Report command execution errors.

## Phase 2: Dependency Installation & Configuration

1.  **Install Initial Dependencies (Coordinator Task):**
    *   **Goal:** Install dependencies defined by the Vite template.
    *   **Tool:** `execute_command`
    *   **Procedure:**
        1.  Construct command:
            *   npm: `npm install`
            *   yarn: `yarn install`
            *   pnpm: `pnpm install`
        2.  Explain: "Installing base dependencies..."
        3.  Execute: `<execute_command><command>[Install Command]</command><cwd>[projectName]</cwd></execute_command>`
        4.  Await result. Handle errors.

2.  **Install TanStack Query (Coordinator Task):**
    *   **Goal:** Add TanStack Query package.
    *   **Tool:** `execute_command`
    *   **Procedure:**
        1.  Construct command:
            *   npm: `npm install @tanstack/react-query`
            *   yarn: `yarn add @tanstack/react-query`
            *   pnpm: `pnpm add @tanstack/react-query`
        2.  *(Optional)* Add devtools: Append `@tanstack/react-query-devtools` to the install command.
        3.  Explain: "Installing TanStack Query..."
        4.  Execute: `<execute_command><command>[Install Query Command]</command><cwd>[projectName]</cwd></execute_command>`
        5.  Await result. Handle errors.

3.  **Set up QueryClientProvider (Delegate Task):**
    *   **Goal:** Wrap the application with the necessary TanStack Query provider.
    *   **Action:** Define Task (`TASK-SETUP-QUERYCLIENT-...`). Delegate to `dev-react` or `util-typescript`.
    *   **Message:** "Modify the main application entry point file (likely `[projectName]/src/main.tsx`) to set up TanStack Query:
        1. Import `QueryClient` and `QueryClientProvider` from `@tanstack/react-query`.
        2. Create a `queryClient` instance: `const queryClient = new QueryClient()`.
        3. Wrap the main `<App />` component (or the root component) with `<QueryClientProvider client={queryClient}>`.
        4. *(Optional)* Import and add `<ReactQueryDevtools initialIsOpen={false} />` inside the provider if devtools were installed."
    *   **Process:** Use MDTM workflow. Specialist uses `read_file` then `apply_diff` or `search_and_replace`.

## Phase 3: Verification & Documentation

1.  **Basic Build/Dev Server Check (Coordinator Task):**
    *   **Goal:** Ensure the setup doesn't immediately fail.
    *   **Tool:** `execute_command`
    *   **Procedure:**
        1.  Try running the dev server: `<execute_command><command>[packageManager] run dev</command><cwd>[projectName]</cwd><timeout_seconds>30</timeout_seconds></execute_command>` (Use timeout as `dev` runs continuously). Check `stderr` for immediate errors.
        2.  Try running a build: `<execute_command><command>[packageManager] run build</command><cwd>[projectName]</cwd></execute_command>`. Check `exit_code`.
    *   **Action:** Report success or any errors found to the user. These are basic checks, not full tests.

2.  **Update README (Task):**
    *   **Goal:** Add notes about TanStack Query setup.
    *   **Action:** Define Task (`TASK-DOC-TANSTACK-...`). Delegate to `util-writer`.
    *   **Message:** "Update `[projectName]/README.md`. Add a small section noting that TanStack Query (`@tanstack/react-query`) has been installed and the application is wrapped in a `QueryClientProvider` in `src/main.tsx`."
    *   **Process:** Use MDTM workflow.

3.  **Complete Feature:**
    *   **Action:** Mark the Setup Feature (`FEAT-230-...`) as "Done". Inform the user the basic setup is complete.

## Key Considerations:

*   **Package Manager Choice:** Ensure commands match the user's selected manager.
*   **Vite Template Updates:** Vite templates can change; verify the exact initialization command and generated file structure (`main.tsx` vs `main.jsx`).
*   **TanStack Query Configuration:** This playbook sets up the *basic* provider. Further configuration (default options, garbage collection time) might be needed later.
*   **Error Handling:** Provide clear feedback if `npm/yarn/pnpm` commands fail (dependency conflicts, network issues).

This playbook provides a streamlined path to getting a common React development stack up and running.