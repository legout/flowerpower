+++
# --- Metadata ---
id = "PLAYBOOK-SETUP-VITE-REACT-TS-SHADCN-V1"
title = "Project Playbook: Setup Vite + React + TypeScript + Shadcn/UI"
status = "published"
created_date = "2025-04-24"
updated_date = "2025-04-24"
version = "1.0"
tags = ["playbook", "documentation", "project-management", "setup", "vite", "react", "typescript", "shadcn", "tailwind", "ui-library", "frontend", "epic", "feature", "task"]
related_docs = [
    ".ruru/docs/standards/project-management-strategy-v1.md",
    ".ruru/planning/project-structure/00-epic-feature-task-plan.md",
    ".ruru/docs/playbooks/22-playbook-setup-vite-react-ts-tailwind.md", # Prerequisite
    ".ruru/modes/util-vite/util-vite.mode.md", # If available
    ".ruru/modes/dev-react/dev-react.mode.md",
    ".ruru/modes/design-shadcn/design-shadcn.mode.md",
    ".ruru/modes/design-tailwind/design-tailwind.mode.md",
    ".ruru/modes/util-typescript/util-typescript.mode.md"
]
objective = "Guide the setup of a new frontend project using Vite, React, TypeScript, Tailwind CSS, and initialize Shadcn/UI for component integration."
scope = "Covers prerequisite Tailwind setup, Shadcn/UI CLI initialization, configuration, and adding an example component."
target_audience = ["Users", "Frontend Developers", "AI Modes"]
# --- Document Specific Fields ---
example_project_type = "New Frontend Web Application using Shadcn/UI"
project_name_placeholder = "[projectName]" # e.g., "my-shadcn-app"
package_manager_placeholder = "[npm|yarn|pnpm]" # User choice or default
+++

# Project Playbook: Setup Vite + React + TypeScript + Shadcn/UI

This playbook outlines the steps to initialize a new frontend project using Vite (React + TypeScript), configure Tailwind CSS, and then initialize and set up Shadcn/UI.

**Scenario:** You are starting a new React project and want to use Vite, TypeScript, Tailwind CSS, and the composable components provided by Shadcn/UI.

**Prerequisite:** A working Vite + React + TypeScript + Tailwind CSS setup. This playbook assumes the steps from `22-playbook-setup-vite-react-ts-tailwind.md` have been completed or are performed first.

## Phase 1: Project Initialization & Tailwind Setup (Prerequisite)

1.  **Complete Tailwind Setup:**
    *   **Action:** Ensure the project `[projectName]` exists and has Vite, React, TypeScript, Tailwind CSS, PostCSS, and Autoprefixer installed and configured correctly as per Playbook 22.
    *   **Verification:** Confirm `tailwind.config.js`, `postcss.config.js` exist and are configured, and `src/index.css` includes `@tailwind` directives.

## Phase 2: Shadcn/UI Initialization

1.  **Define Shadcn/UI Setup Goal (Feature):**
    *   **Goal:** Initialize Shadcn/UI in the existing Vite project.
    *   **Action:** Create a Feature (e.g., `.ruru/features/FEAT-260-setup-shadcn-ui.md`). If part of a larger app, link to its Epic.
    *   **Content:** Define `objective`, mention prerequisites. Set `status` to "Planned".

2.  **Run Shadcn/UI Init Command (Coordinator Task - Interactive):**
    *   **Goal:** Use the Shadcn/UI CLI to configure the project. This requires interactive input.
    *   **Tool:** `execute_command` (for the CLI), `ask_followup_question` (to relay CLI prompts to user)
    *   **Procedure:**
        1.  Explain: "Now we'll initialize Shadcn/UI using its CLI. I will run the command, and it will ask you some questions. I'll relay the questions to you for your input."
        2.  Execute the init command (adjust based on `[packageManager]`):
            *   npx: `npx shadcn-ui@latest init`
            *   yarn: `yarn dlx shadcn-ui@latest init`
            *   pnpm: `pnpm dlx shadcn-ui@latest init`
            ```xml
            <execute_command>
             <command>[Shadcn Init Command]</command>
             <cwd>[projectName]</cwd>
             <!-- Increase timeout if needed, init might take time -->
             <timeout_seconds>120</timeout_seconds>
            </execute_command>
            ```
        3.  **Monitor Output:** Observe the `stdout` from `execute_command`. The Shadcn CLI will ask interactive questions (e.g., "Which style?", "Which base color?", "Where is your global CSS file?", "Use CSS variables?", "Where is your tailwind.config.js?", "Configure imports alias?", "Where is your `tsconfig.json`?", "Are you using React Server Components?").
        4.  **Relay Questions to User:** For *each question* detected in the `stdout`, use `<ask_followup_question>` to present the exact question and its options (if any) to the user. Provide sensible defaults as suggestions based on the Vite+React+TS setup (e.g., Suggest `./src/index.css` for global CSS, `tailwind.config.js` for Tailwind config, `@/*` for alias, `tsconfig.json`, CSS variables: Yes, Style: Default, Base Color: Slate, Server Components: No).
            ```xml
            <!-- Example Relay Prompt -->
            <ask_followup_question>
             <question>Shadcn/UI setup asks: "[Question text from CLI output]"</question>
             <follow_up>
               <!-- Parse options from CLI output or provide common ones -->
               <suggest>[Option 1 from CLI / Sensible Default]</suggest>
               <suggest>[Option 2 from CLI]</suggest>
               ...
             </follow_up>
            </ask_followup_question>
            ```
        5.  **Send User's Answer Back to CLI:** This is the tricky part. Standard `<execute_command>` doesn't support interactive input *back* to the running process.
            *   **Workaround 1 (Manual):** Instruct the user to run the `npx shadcn-ui@latest init` command *manually* in their *own* terminal within the `[projectName]` directory and answer the prompts there. Then ask them to confirm once done.
            *   **Workaround 2 (Less Reliable AI Guessing):** Attempt to answer *all* prompts non-interactively by providing default flags to the `init` command if possible (check Shadcn CLI docs). This is less flexible.
            *   **Workaround 3 (Future Tool):** Requires a Roo Code tool enhancement for interactive terminal sessions.
            *   **Chosen Path (for this playbook - assuming Workaround 1):** Instruct the user to run the command manually.
                ```xml
                 <ask_followup_question>
                  <question>To configure Shadcn/UI interactively, please run the following command **in your own terminal** inside the `[projectName]` directory and answer the setup questions:

                  ```bash
                  # If using npm/npx:
                  npx shadcn-ui@latest init

                  # If using yarn:
                  # yarn dlx shadcn-ui@latest init

                  # If using pnpm:
                  # pnpm dlx shadcn-ui@latest init
                  ```

                  Please let me know once you have completed the `init` process. Sensible defaults for Vite+React+TS are usually: Style: Default, Color: Slate, Global CSS: `src/index.css`, CSS Variables: Yes, Alias: `@/*`, `tsconfig.json`: `tsconfig.json`, Server Components: No.
                  </question>
                  <follow_up>
                    <suggest>I have completed the `shadcn-ui init` command.</suggest>
                    <suggest>I encountered an error during init.</suggest>
                  </follow_up>
                 </ask_followup_question>
                ```
        6.  Await user confirmation. Handle errors reported by the user.
    *   **Outputs:** Shadcn/UI configuration files (`components.json`) created/updated, utility files added (`src/lib/utils.ts`), potentially global CSS updated.

## Phase 3: Adding & Verifying a Component

1.  **Add Example Shadcn/UI Component (Coordinator Task):**
    *   **Goal:** Install a sample component using the Shadcn/UI CLI.
    *   **Tool:** `execute_command`
    *   **Procedure:**
        1.  Explain: "Let's add a sample component, like the Button, using the Shadcn/UI CLI."
        2.  Construct command:
            *   npx: `npx shadcn-ui@latest add button`
            *   yarn: `yarn dlx shadcn-ui@latest add button`
            *   pnpm: `pnpm dlx shadcn-ui@latest add button`
        3.  Execute: `<execute_command><command>[Shadcn Add Command]</command><cwd>[projectName]</cwd></execute_command>`
        4.  Await result. Handle errors (e.g., component not found, config issues).
    *   **Outputs:** Component files added (e.g., `src/components/ui/button.tsx`).

2.  **Use Example Component (Delegate Task):**
    *   **Goal:** Import and render the added component to verify setup.
    *   **Action:** Define Task (`TASK-USE-SHADCN-BTN-...`). Delegate to `dev-react` or `design-shadcn`.
    *   **Message:** "Modify `[projectName]/src/App.tsx`. Import the `Button` component (likely from `~/components/ui/button` or `@/components/ui/button` depending on alias config). Render the button (e.g., `<Button>Shadcn Button</Button>`). Verify the application still runs (`[packageManager] run dev`) and the button appears with Shadcn/Tailwind styles."
    *   **Process:** Use MDTM workflow. Specialist verifies locally or reports back.

## Phase 4: Documentation & Completion

1.  **Update README (Task):**
    *   **Goal:** Add notes about Shadcn/UI setup.
    *   **Action:** Define Task (`TASK-DOC-SHADCN-...`). Delegate to `util-writer`.
    *   **Message:** "Update `[projectName]/README.md`. Add a section noting that Shadcn/UI has been initialized. Mention the `components.json` file and that components are added via the CLI (`npx shadcn-ui@latest add [component]`). Link to the Shadcn/UI documentation (https://ui.shadcn.com/)."
    *   **Process:** Use MDTM workflow.

2.  **Complete Feature:**
    *   **Action:** Mark the Setup Feature (`FEAT-260-...`) as "Done". Inform the user the basic Shadcn/UI setup is complete and they can add more components via the CLI.

## Key Considerations:

*   **Tailwind Prerequisite:** Shadcn/UI heavily relies on Tailwind CSS. Ensure Tailwind is correctly set up first.
*   **Interactive CLI:** The `shadcn-ui init` command is interactive. The playbook currently suggests manual execution by the user due to limitations in standard `execute_command`. This is the most practical workaround.
*   **Configuration (`components.json`):** The `init` command creates `components.json`, defining paths and aliases. Ensure this file is correctly generated.
*   **Component Installation:** Components are added individually via the CLI, which copies their source code into your project (typically under `src/components/ui`), allowing full customization.

This playbook guides the user through integrating Shadcn/UI, acknowledging the interactive nature of its setup process.