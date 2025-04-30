+++
# --- Metadata ---
id = "PLAYBOOK-SETUP-VITE-REACT-TS-ANTD-V1"
title = "Project Playbook: Setup Vite + React + TypeScript + Ant Design (Antd)"
status = "published"
created_date = "2025-04-24"
updated_date = "2025-04-24"
version = "1.0"
tags = ["playbook", "documentation", "project-management", "setup", "vite", "react", "typescript", "antd", "ant-design", "frontend", "ui-library", "epic", "feature", "task"]
related_docs = [
    ".ruru/docs/standards/project-management-strategy-v1.md",
    ".ruru/planning/project-structure/00-epic-feature-task-plan.md",
    ".ruru/modes/util-vite/util-vite.mode.md", # If available
    ".ruru/modes/dev-react/dev-react.mode.md",
    ".ruru/modes/design-antd/design-antd.mode.md",
    ".ruru/modes/util-typescript/util-typescript.mode.md"
]
objective = "Guide the setup of a new frontend project using Vite, React, TypeScript, and the Ant Design (Antd) component library."
scope = "Covers project initialization, dependency installation, importing Antd's global CSS, and basic component usage verification."
target_audience = ["Users", "Frontend Developers", "AI Modes"]
# --- Document Specific Fields ---
example_project_type = "New Frontend Web Application using Ant Design"
project_name_placeholder = "[projectName]" # e.g., "my-antd-app"
package_manager_placeholder = "[npm|yarn|pnpm]" # User choice or default
+++

# Project Playbook: Setup Vite + React + TypeScript + Ant Design (Antd)

This playbook outlines the steps to initialize a new frontend project using Vite with the React + TypeScript template and integrate the Ant Design (Antd) component library.

**Scenario:** You are starting a new React project and want to use Vite, TypeScript, and the comprehensive component suite provided by Ant Design.

## Phase 1: Project Initialization

1.  **Define the Setup Goal (Epic/Feature):**
    *   **Goal:** Create a new Vite project configured with React, TypeScript, and Ant Design.
    *   **Action:** Create a Feature (e.g., `.ruru/features/FEAT-270-setup-vite-react-ts-antd.md`). If part of a larger app, link to its Epic.
    *   **Content:** Define `objective`, specify target stack. Set `status` to "Planned".

2.  **Get Project Name & Package Manager (Coordinator Task):**
    *   **Goal:** Obtain necessary details from the user.
    *   **Tool:** `ask_followup_question`
    *   **Procedure:** (Same prompt as previous setup playbooks)
        ```xml
        <ask_followup_question>
         <question>Let's set up your Vite + React + TS + Ant Design project.
         1. What do you want to name the project directory? (e.g., my-antd-app)
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

## Phase 2: Ant Design Installation & Configuration

1.  **Install Initial Dependencies (Coordinator Task):**
    *   **Goal:** Install dependencies defined by the Vite template.
    *   **Tool:** `execute_command`
    *   **Procedure:**
        1.  Construct command: `[packageManager] install`
        2.  Explain: "Installing base dependencies..."
        3.  Execute: `<execute_command><command>[packageManager] install</command><cwd>[projectName]</cwd></execute_command>`
        4.  Await result. Handle errors.

2.  **Install Ant Design Dependencies (Coordinator Task):**
    *   **Goal:** Add the core `antd` package and optionally `@ant-design/icons`.
    *   **Tool:** `execute_command`
    *   **Procedure:**
        1.  Construct command (adjust based on `[packageManager]`):
            *   npm: `npm install antd @ant-design/icons`
            *   yarn: `yarn add antd @ant-design/icons`
            *   pnpm: `pnpm add antd @ant-design/icons`
            *   *(Note: `@ant-design/icons` is optional but commonly used with Antd)*
        2.  Explain: "Installing Ant Design (antd) and Ant Design Icons..."
        3.  Execute: `<execute_command><command>[Antd Install Command]</command><cwd>[projectName]</cwd></execute_command>`
        4.  Await result. Handle errors.

3.  **Import Ant Design CSS (Delegate Task):**
    *   **Goal:** Import the global Ant Design stylesheet.
    *   **Action:** Define Task (`TASK-IMPORT-ANTD-CSS-...`). Delegate to `dev-react` or `design-antd`.
    *   **Message:** "Modify the main application entry point file (likely `[projectName]/src/main.tsx`). Import the Ant Design core CSS file by adding this line at or near the top: `import 'antd/dist/reset.css';`"
    *   **Process:** Use MDTM workflow. Specialist uses `read_file` then `apply_diff` or `insert_content`.

## Phase 3: Verification & Documentation

1.  **Basic Build/Dev Server Check (Coordinator Task):**
    *   **Goal:** Ensure the setup with Antd doesn't break the build or dev server.
    *   **Tool:** `execute_command`
    *   **Procedure:** (Same as previous playbooks)
        1.  Try running dev server: `<execute_command><command>[packageManager] run dev</command><cwd>[projectName]</cwd><timeout_seconds>30</timeout_seconds></execute_command>`. Check `stderr`.
        2.  Try running build: `<execute_command><command>[packageManager] run build</command><cwd>[projectName]</cwd></execute_command>`. Check `exit_code`.
    *   **Action:** Report success or errors.

2.  **Add Example Antd Component (Task):**
    *   **Goal:** Verify Antd components can be imported and rendered with styles.
    *   **Action:** Define Task (`TASK-ADD-ANTD-EXAMPLE-...`). Delegate to `dev-react` or `design-antd`.
    *   **Message:** "Modify `[projectName]/src/App.tsx`. Import a simple Antd component (e.g., `Button` from `antd` and maybe an icon like `HomeOutlined` from `@ant-design/icons`). Render the component (e.g., `<Button type='primary' icon={<HomeOutlined />}>Hello Antd</Button>`). Verify the application still runs (`[packageManager] run dev`) and the button appears with Ant Design styles and the icon."
    *   **Process:** Use MDTM workflow. Specialist verifies locally or reports back success/failure.

3.  **Update README (Task):**
    *   **Goal:** Add notes about Ant Design setup.
    *   **Action:** Define Task (`TASK-DOC-ANTD-...`). Delegate to `util-writer`.
    *   **Message:** "Update `[projectName]/README.md`. Add a section noting that Ant Design (`antd`) and `@ant-design/icons` have been installed. Mention that the required CSS (`antd/dist/reset.css`) is imported in `src/main.tsx`."
    *   **Process:** Use MDTM workflow.

4.  **Complete Feature:**
    *   **Action:** Mark the Setup Feature (`FEAT-270-...`) as "Done". Inform the user the basic Ant Design setup is complete.

## Key Considerations:

*   **CSS Import:** Importing `antd/dist/reset.css` is essential for the components to render correctly. Ensure this is done in the main application entry point before your own custom styles that might override Antd.
*   **Theming:** Ant Design uses a `ConfigProvider` component for theming, often configured with a theme object. This playbook doesn't include advanced theming setup, which would involve creating a theme object and wrapping the app in `<ConfigProvider>`.
*   **Icons:** The `@ant-design/icons` package is large. For production builds, consider setting up build tools (like `babel-plugin-import` or Vite equivalent) to automatically tree-shake unused icons, although Vite often handles this reasonably well by default with modern Antd versions.
*   **Component Imports:** Antd components are imported directly from the `antd` package (e.g., `import { Button, Input } from 'antd';`).

This playbook provides the steps to integrate Ant Design into a Vite/React/TS project, focusing on the core library and CSS setup.