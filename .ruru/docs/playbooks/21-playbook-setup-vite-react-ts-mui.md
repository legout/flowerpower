+++
# --- Metadata ---
id = "PLAYBOOK-SETUP-VITE-REACT-TS-MUI-V1"
title = "Project Playbook: Setup Vite + React + TypeScript + Material UI (MUI)"
status = "published"
created_date = "2025-04-24"
updated_date = "2025-04-24"
version = "1.0"
tags = ["playbook", "documentation", "project-management", "setup", "vite", "react", "typescript", "mui", "material-ui", "frontend", "ui-library", "epic", "feature", "task"]
related_docs = [
    ".ruru/docs/standards/project-management-strategy-v1.md",
    ".ruru/planning/project-structure/00-epic-feature-task-plan.md",
    ".ruru/modes/util-vite/util-vite.mode.md", # If available
    ".ruru/modes/dev-react/dev-react.mode.md",
    ".ruru/modes/design-mui/design-mui.mode.md",
    ".ruru/modes/util-typescript/util-typescript.mode.md"
]
objective = "Guide the setup of a new frontend project using Vite, React, TypeScript, and the Material UI (MUI) component library."
scope = "Covers project initialization, dependency installation (MUI Core, Emotion, icons), basic theme setup (optional), and verification."
target_audience = ["Users", "Frontend Developers", "AI Modes"]
# --- Document Specific Fields ---
example_project_type = "New Frontend Web Application using Material Design"
project_name_placeholder = "[projectName]" # e.g., "my-mui-app"
package_manager_placeholder = "[npm|yarn|pnpm]" # User choice or default
+++

# Project Playbook: Setup Vite + React + TypeScript + Material UI (MUI)

This playbook outlines the steps to initialize a new frontend project using Vite with the React + TypeScript template and integrate the Material UI (MUI) component library.

**Scenario:** You are starting a new React project and want to use Vite, TypeScript, and the MUI component library for implementing Material Design.

## Phase 1: Project Initialization

1.  **Define the Setup Goal (Epic/Feature):**
    *   **Goal:** Create a new Vite project configured with React, TypeScript, and MUI Core.
    *   **Action:** Create a Feature (e.g., `.ruru/features/FEAT-240-setup-vite-react-ts-mui.md`). If part of a larger app, link to its Epic.
    *   **Content:** Define `objective`, specify target stack. Set `status` to "Planned".

2.  **Get Project Name & Package Manager (Coordinator Task):**
    *   **Goal:** Obtain necessary details from the user.
    *   **Tool:** `ask_followup_question`
    *   **Procedure:** (Same prompt as the TanStack Query playbook, just adjust context slightly if needed)
        ```xml
        <ask_followup_question>
         <question>Let's set up your Vite + React + TS + MUI project.
         1. What do you want to name the project directory? (e.g., my-mui-app)
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

2.  **Install MUI Dependencies (Coordinator Task):**
    *   **Goal:** Add MUI Core, Emotion (default styling engine), and Material Icons.
    *   **Tool:** `execute_command`
    *   **Procedure:**
        1.  Construct command (adjust based on `[packageManager]`):
            *   npm: `npm install @mui/material @emotion/react @emotion/styled @mui/icons-material`
            *   yarn: `yarn add @mui/material @emotion/react @emotion/styled @mui/icons-material`
            *   pnpm: `pnpm add @mui/material @emotion/react @emotion/styled @mui/icons-material`
        2.  Explain: "Installing Material UI (MUI) Core, Emotion dependencies, and Material Icons..."
        3.  Execute: `<execute_command><command>[MUI Install Command]</command><cwd>[projectName]</cwd></execute_command>`
        4.  Await result. Handle errors.

3.  **Basic Theme Setup (Optional Feature/Tasks):**
    *   **Goal:** Configure a basic MUI theme provider and potentially customize default theme settings (e.g., primary color).
    *   **Action:** Define as a Feature (`FEAT-241-mui-basic-theme-setup.md`) or skip if default theme is sufficient initially. Delegate tasks to `design-mui` or `dev-react`.
    *   **Tasks (Examples):**
        *   "Create a theme file (e.g., `src/theme.ts`)."
        *   "In `theme.ts`, import `createTheme` from `@mui/material/styles`."
        *   "Define a basic theme object: `const theme = createTheme({ palette: { /* Optional customizations */ } });`"
        *   "Modify the main application entry point (`src/main.tsx`): Import `ThemeProvider` from `@mui/material/styles` and the created `theme` object."
        *   "Wrap the main `<App />` component with `<ThemeProvider theme={theme}>`."
        *   *(Optional)* "Import and add `<CssBaseline />` component inside the ThemeProvider for consistent baseline styles."
    *   **Process:** Use MDTM workflow.

## Phase 3: Verification & Documentation

1.  **Basic Build/Dev Server Check (Coordinator Task):**
    *   **Goal:** Ensure the setup with MUI doesn't cause immediate build or runtime errors.
    *   **Tool:** `execute_command`
    *   **Procedure:** (Same as previous playbook)
        1.  Try running the dev server: `<execute_command><command>[packageManager] run dev</command><cwd>[projectName]</cwd><timeout_seconds>30</timeout_seconds></execute_command>`. Check `stderr`.
        2.  Try running a build: `<execute_command><command>[packageManager] run build</command><cwd>[projectName]</cwd></execute_command>`. Check `exit_code`.
    *   **Action:** Report success or errors.

2.  **Add Example MUI Component (Task):**
    *   **Goal:** Verify MUI components can be imported and rendered.
    *   **Action:** Define Task (`TASK-ADD-MUI-EXAMPLE-...`). Delegate to `dev-react` or `design-mui`.
    *   **Message:** "Modify `[projectName]/src/App.tsx`. Import a simple MUI component (e.g., `Button` from `@mui/material`) and render it within the `App` component (e.g., `<Button variant='contained'>Hello MUI</Button>`). Verify the application still runs (`[packageManager] run dev`) and the button appears with Material styles."
    *   **Process:** Use MDTM workflow. Specialist verifies locally or reports back success/failure.

3.  **Update README (Task):**
    *   **Goal:** Add notes about MUI setup.
    *   **Action:** Define Task (`TASK-DOC-MUI-...`). Delegate to `util-writer`.
    *   **Message:** "Update `[projectName]/README.md`. Add a section noting that Material UI (`@mui/material`), Emotion (`@emotion/react`, `@emotion/styled`), and Material Icons (`@mui/icons-material`) have been installed. Mention that the app is wrapped in `ThemeProvider` (if theme setup was done) in `src/main.tsx`."
    *   **Process:** Use MDTM workflow.

4.  **Complete Feature:**
    *   **Action:** Mark the Setup Feature (`FEAT-240-...`) as "Done". Inform the user the basic MUI setup is complete.

## Key Considerations:

*   **Styling Engine:** MUI primarily uses Emotion by default, but can be configured with Styled Components or plain CSS/Tailwind (requires more setup). This playbook assumes the default (Emotion).
*   **Theme Customization:** The theme setup here is minimal. Deeper customization (typography, spacing, component overrides) would involve more complex tasks within the theme file.
*   **Font Setup:** MUI relies on specific fonts (like Roboto) for the intended Material Design look. The playbook doesn't explicitly add font loading (e.g., via CDN link in `index.html` or self-hosting). This might be a needed follow-up task. Using `CssBaseline` helps apply font settings.
*   **MUI Packages:** MUI has many packages (`@mui/x-data-grid`, `@mui/x-date-pickers`, etc.). This playbook only covers `@mui/material` (core) and `@mui/icons-material`. Installing other MUI packages would follow Step 2.2.

This playbook guides the setup for a common React UI library, ensuring the core dependencies and provider setup are handled correctly.