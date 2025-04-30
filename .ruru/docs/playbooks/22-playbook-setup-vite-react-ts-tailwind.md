+++
# --- Metadata ---
id = "PLAYBOOK-SETUP-VITE-REACT-TS-TAILWIND-V1"
title = "Project Playbook: Setup Vite + React + TypeScript + Tailwind CSS"
status = "published"
created_date = "2025-04-24"
updated_date = "2025-04-24"
version = "1.0"
tags = ["playbook", "documentation", "project-management", "setup", "vite", "react", "typescript", "tailwind", "tailwindcss", "frontend", "css", "epic", "feature", "task"]
related_docs = [
    ".ruru/docs/standards/project-management-strategy-v1.md",
    ".ruru/planning/project-structure/00-epic-feature-task-plan.md",
    ".ruru/modes/util-vite/util-vite.mode.md", # If available
    ".ruru/modes/dev-react/dev-react.mode.md",
    ".ruru/modes/design-tailwind/design-tailwind.mode.md",
    ".ruru/modes/util-typescript/util-typescript.mode.md"
]
objective = "Guide the setup of a new frontend project using Vite, React, TypeScript, and the Tailwind CSS utility-first CSS framework."
scope = "Covers project initialization, dependency installation, Tailwind configuration file setup, PostCSS integration, and basic CSS import/usage verification."
target_audience = ["Users", "Frontend Developers", "AI Modes"]
# --- Document Specific Fields ---
example_project_type = "New Frontend Web Application using Tailwind CSS"
project_name_placeholder = "[projectName]" # e.g., "my-tailwind-app"
package_manager_placeholder = "[npm|yarn|pnpm]" # User choice or default
+++

# Project Playbook: Setup Vite + React + TypeScript + Tailwind CSS

This playbook outlines the steps to initialize a new frontend project using Vite with the React + TypeScript template and integrate the Tailwind CSS framework.

**Scenario:** You are starting a new React project and want to use Vite, TypeScript, and Tailwind CSS for styling.

## Phase 1: Project Initialization

1.  **Define the Setup Goal (Epic/Feature):**
    *   **Goal:** Create a new Vite project configured with React, TypeScript, and Tailwind CSS.
    *   **Action:** Create a Feature (e.g., `.ruru/features/FEAT-250-setup-vite-react-ts-tailwind.md`). If part of a larger app, link to its Epic.
    *   **Content:** Define `objective`, specify target stack. Set `status` to "Planned".

2.  **Get Project Name & Package Manager (Coordinator Task):**
    *   **Goal:** Obtain necessary details from the user.
    *   **Tool:** `ask_followup_question`
    *   **Procedure:** (Same prompt as previous playbooks)
        ```xml
        <ask_followup_question>
         <question>Let's set up your Vite + React + TS + Tailwind project.
         1. What do you want to name the project directory? (e.g., my-tailwind-app)
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

## Phase 2: Tailwind CSS Installation & Configuration

1.  **Install Base Dependencies (Coordinator Task):**
    *   **Goal:** Install dependencies defined by the Vite template.
    *   **Tool:** `execute_command`
    *   **Procedure:**
        1.  Construct command: `[packageManager] install`
        2.  Explain: "Installing base dependencies..."
        3.  Execute: `<execute_command><command>[packageManager] install</command><cwd>[projectName]</cwd></execute_command>`
        4.  Await result. Handle errors.

2.  **Install Tailwind Dependencies (Coordinator Task):**
    *   **Goal:** Add Tailwind CSS, PostCSS, and Autoprefixer as dev dependencies.
    *   **Tool:** `execute_command`
    *   **Procedure:**
        1.  Construct command (adjust based on `[packageManager]`):
            *   npm: `npm install -D tailwindcss postcss autoprefixer`
            *   yarn: `yarn add -D tailwindcss postcss autoprefixer`
            *   pnpm: `pnpm add -D tailwindcss postcss autoprefixer`
        2.  Explain: "Installing Tailwind CSS, PostCSS, and Autoprefixer..."
        3.  Execute: `<execute_command><command>[Tailwind Install Command]</command><cwd>[projectName]</cwd></execute_command>`
        4.  Await result. Handle errors.

3.  **Generate Tailwind & PostCSS Config Files (Coordinator Task):**
    *   **Goal:** Create the necessary configuration files using the Tailwind CLI.
    *   **Tool:** `execute_command`
    *   **Procedure:**
        1.  Construct command: `npx tailwindcss init -p` (The `-p` flag also creates `postcss.config.js`).
        2.  Explain: "Generating `tailwind.config.js` and `postcss.config.js`..."
        3.  Execute: `<execute_command><command>npx tailwindcss init -p</command><cwd>[projectName]</cwd></execute_command>`
        4.  Await result. Check `stdout`/`stderr` for confirmation or errors.
        5.  Verify files were created using `<list_files><path>[projectName]</path></list_files>`.

4.  **Configure Tailwind Template Paths (Delegate Task):**
    *   **Goal:** Tell Tailwind which files contain class names.
    *   **Action:** Define Task (`TASK-CONFIG-TAILWIND-...`). Delegate to `design-tailwind` or `util-senior-dev`.
    *   **Message:** "Modify the `[projectName]/tailwind.config.js` file. Update the `content` array to include paths to all template files using Tailwind classes. A typical Vite+React setup uses: `content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}']`."
    *   **Process:** Use MDTM workflow. Specialist uses `read_file` then `apply_diff` or `search_and_replace`.

5.  **Add Tailwind Directives to CSS (Delegate Task):**
    *   **Goal:** Import Tailwind's base, components, and utilities layers into the main CSS file.
    *   **Action:** Define Task (`TASK-ADD-TAILWIND-DIRECTIVES-...`). Delegate to `design-tailwind` or `dev-general`.
    *   **Message:** "Modify the main CSS file (likely `[projectName]/src/index.css`). Add the following Tailwind directives at the top: `@tailwind base; @tailwind components; @tailwind utilities;`."
    *   **Process:** Use MDTM workflow. Specialist uses `read_file` then `apply_diff` or `search_and_replace` (or `insert_content` at start).

## Phase 3: Verification & Documentation

1.  **Basic Build/Dev Server Check (Coordinator Task):**
    *   **Goal:** Ensure the setup with Tailwind doesn't break the build or dev server.
    *   **Tool:** `execute_command`
    *   **Procedure:** (Same as previous playbooks)
        1.  Try running dev server: `<execute_command><command>[packageManager] run dev</command><cwd>[projectName]</cwd><timeout_seconds>30</timeout_seconds></execute_command>`. Check `stderr`.
        2.  Try running build: `<execute_command><command>[packageManager] run build</command><cwd>[projectName]</cwd></execute_command>`. Check `exit_code`.
    *   **Action:** Report success or errors.

2.  **Test Tailwind Usage (Task):**
    *   **Goal:** Verify Tailwind utility classes are being applied correctly.
    *   **Action:** Define Task (`TASK-TEST-TAILWIND-...`). Delegate to `dev-react` or `design-tailwind`.
    *   **Message:** "Modify `[projectName]/src/App.tsx`. Add some basic Tailwind utility classes to an element (e.g., `<h1 className='text-3xl font-bold underline text-blue-600'>Hello Tailwind!</h1>`). Run the dev server (`[packageManager] run dev`) and verify visually that the styles (large text, bold, underline, blue color) are applied correctly."
    *   **Process:** Use MDTM workflow. Specialist modifies code and reports visual confirmation (or provides screenshot link if possible).

3.  **Update README (Task):**
    *   **Goal:** Add notes about Tailwind setup.
    *   **Action:** Define Task (`TASK-DOC-TAILWIND-...`). Delegate to `util-writer`.
    *   **Message:** "Update `[projectName]/README.md`. Add a section noting that Tailwind CSS has been installed and configured via `tailwind.config.js` and `postcss.config.js`. Mention that the base directives are imported in `src/index.css`."
    *   **Process:** Use MDTM workflow.

4.  **Complete Feature:**
    *   **Action:** Mark the Setup Feature (`FEAT-250-...`) as "Done". Inform the user the basic Tailwind setup is complete.

## Key Considerations:

*   **Configuration Files:** Ensure `tailwind.config.js` and `postcss.config.js` are created correctly in the project root.
*   **`content` Path:** The `content` array in `tailwind.config.js` is critical. It must correctly point to all files where Tailwind classes will be used, otherwise, styles won't be generated in the production build.
*   **CSS Import:** Ensure the main CSS file (e.g., `src/index.css`) containing the `@tailwind` directives is imported into the application's entry point (e.g., `src/main.tsx`). The Vite template usually does this by default.
*   **Plugins:** This playbook doesn't include installing Tailwind plugins (like `@tailwindcss/forms` or `prettier-plugin-tailwindcss`). Adding plugins would involve installing them and updating `tailwind.config.js`.

This playbook provides the standard steps for integrating Tailwind CSS into a Vite + React + TS project.