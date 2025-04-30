+++
# --- Metadata ---
id = "PLAYBOOK-SETUP-RN-EXPO-GO-V1"
title = "Project Playbook: Setup React Native Project (Expo Go)"
status = "published"
created_date = "2025-04-24"
updated_date = "2025-04-24"
version = "1.0"
tags = ["playbook", "documentation", "project-management", "setup", "react-native", "expo", "expo-go", "mobile", "epic", "feature", "task"]
related_docs = [
    ".ruru/docs/standards/project-management-strategy-v1.md",
    ".ruru/planning/project-structure/00-epic-feature-task-plan.md"
    # Add links to relevant RN modes when created
]
objective = "Guide the setup of a new React Native project using the Expo Go workflow, suitable for rapid development and testing on physical devices without native builds."
scope = "Covers project initialization using `create-expo-app`, dependency installation, and basic verification by starting the development server."
target_audience = ["Users", "Mobile Developers", "AI Modes"]
# --- Document Specific Fields ---
example_project_type = "New Mobile Application (iOS/Android) using Expo Go"
project_name_placeholder = "[projectName]" # e.g., "my-expo-app"
package_manager_placeholder = "[npm|yarn|pnpm]" # User choice or default
template_placeholder = "[blank|tabs|navigation]" # e.g., blank (TypeScript), tabs (TypeScript)
+++

# Project Playbook: Setup React Native Project (Expo Go)

This playbook outlines the steps to initialize a new React Native project using the Expo Go workflow, which allows running the app on a physical device via the Expo Go app without needing Xcode or Android Studio installed locally.

**Scenario:** You are starting a new mobile app project and want the quickest setup using Expo and TypeScript.

## Phase 1: Project Initialization

1.  **Define the Setup Goal (Epic/Feature):**
    *   **Goal:** Create a new Expo React Native project suitable for Expo Go.
    *   **Action:** Create a Feature (e.g., `.ruru/features/FEAT-280-setup-expo-go-project.md`). If part of a larger app, link to its Epic.
    *   **Content:** Define `objective`, specify target stack (React Native, Expo Go, TypeScript). Set `status` to "Planned".

2.  **Get Project Name, Package Manager & Template (Coordinator Task):**
    *   **Goal:** Obtain necessary details from the user.
    *   **Tool:** `ask_followup_question`
    *   **Procedure:**
        ```xml
        <ask_followup_question>
         <question>Let's set up your React Native project using Expo Go.
         1. What do you want to name the project directory? (e.g., my-expo-app)
         2. Which package manager do you prefer? (npm, yarn, pnpm)
         3. Choose a starting template (blank includes TypeScript):
         </question>
         <follow_up>
           <suggest>Project Name: [Suggest name], PM: npm, Template: blank</suggest>
           <suggest>Project Name: [Suggest name], PM: pnpm, Template: blank</suggest>
           <suggest>Project Name: [Suggest name], PM: npm, Template: tabs</suggest> <!-- Example with tabs -->
           <suggest>Cancel Setup</suggest>
         </follow_up>
        </ask_followup_question>
        ```
    *   Store user input as `[projectName]`, `[packageManager]`, and `[template]`. Handle cancellation.

3.  **Initialize Expo Project (Coordinator Task):**
    *   **Goal:** Create the base project using the `create-expo-app` CLI.
    *   **Tool:** `execute_command`
    *   **Prerequisite Note:** The user needs Node.js installed. `create-expo-app` is typically run via `npx`.
    *   **Procedure:**
        1.  Construct the command: `npx create-expo-app [projectName] --template [template-slug]` (e.g., `npx create-expo-app my-expo-app --template blank-typescript` or `npx create-expo-app my-expo-app --template expo-template-tabs` - need to verify exact template slugs from Expo docs if defaulting to TS isn't automatic). *Correction: Expo templates often infer TS/JS, let's stick to `blank` or `tabs` for simplicity in the prompt and let the CLI handle specifics, or clarify TS choice separately if needed.* For this example, assume `blank` implies TS: `npx create-expo-app [projectName] --template [template]`
        2.  Explain: "Initializing Expo project `[projectName]` with the `[template]` template..."
        3.  Execute: `<execute_command><command>[Expo Init Command]</command></execute_command>` (Run in parent directory). This command might install dependencies automatically depending on the version/template.
        4.  Await result. `create-expo-app` can take some time.
    *   **Error Handling:** Report command execution errors (e.g., tool not found, network issues, template name invalid).

## Phase 2: Dependency Verification (Often Included in Init)

1.  **Check Dependency Installation (Optional Coordinator Task):**
    *   **Goal:** Verify dependencies were installed by `create-expo-app`. If not, install them.
    *   **Tool:** `list_files`, `execute_command`
    *   **Procedure:**
        1.  Check if `node_modules` directory exists in `[projectName]` using `<list_files>`.
        2.  **If** `node_modules` does NOT exist:
            *   Construct install command: `[packageManager] install`
            *   Explain: "`create-expo-app` didn't install dependencies, running install command..."
            *   Execute: `<execute_command><command>[packageManager] install</command><cwd>[projectName]</cwd></execute_command>`
            *   Await result. Handle errors.
        3.  **Else:** Log that dependencies appear to be installed by the init command.

## Phase 3: Verification & Documentation

1.  **Start Development Server (Coordinator Task):**
    *   **Goal:** Ensure the Expo development server starts without immediate errors.
    *   **Tool:** `execute_command`
    *   **Procedure:**
        1.  Construct command: `[packageManager] start` (or `npx expo start`).
        2.  Explain: "Attempting to start the Expo development server... You can scan the QR code displayed in the terminal using the Expo Go app on your phone (iOS/Android). Press Ctrl+C in the terminal to stop the server."
        3.  Execute: `<execute_command><command>[packageManager] start</command><cwd>[projectName]</cwd><timeout_seconds>60</timeout_seconds></execute_command>` (Use timeout as `start` runs continuously). Check `stderr` for immediate errors *before* the QR code stage.
    *   **Action:** Report success (server started, QR code expected) or any initial errors found in `stderr`. *Note: Roo Commander cannot interact with the QR code or the running app.*

2.  **Update README (Task):**
    *   **Goal:** Add notes about the Expo Go setup.
    *   **Action:** Define Task (`TASK-DOC-EXPO-GO-...`). Delegate to `util-writer`.
    *   **Message:** "Update `[projectName]/README.md`. Add a section explaining that this project is set up using Expo Go. Include instructions on how to start the development server (`[packageManager] start`) and how to run the app on a physical device using the Expo Go app and the QR code."
    *   **Process:** Use MDTM workflow.

3.  **Complete Feature:**
    *   **Action:** Mark the Setup Feature (`FEAT-280-...`) as "Done". Inform the user the basic Expo Go project setup is complete and ready for development.

## Key Considerations:

*   **Expo Go App:** This workflow relies on the user having the Expo Go app installed on their physical iOS or Android device.
*   **Native Code:** The Expo Go workflow does *not* support projects with custom native code (Java/Kotlin/Swift/Objective-C). If native modules are needed later, the project needs to be "prebuilt" or ejected, which requires a different setup (Xcode/Android Studio).
*   **`create-expo-app` Behavior:** The exact command and its behavior (automatic dependency installation) might change slightly between versions. The `npx` approach is generally reliable.
*   **TypeScript Templates:** Verify the correct template name for TypeScript versions (e.g., `blank-typescript` or if `blank` automatically includes TS).
*   **Verification:** The verification step only checks if the server starts. Running the app on a device via Expo Go is a manual step for the user.

This playbook provides the initial steps for getting started quickly with React Native development using the convenient Expo Go workflow.