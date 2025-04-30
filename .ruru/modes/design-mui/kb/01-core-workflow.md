# Material UI: Core Concepts & Workflow (MUI Core v5+)

Introduction to MUI Core components, setup, general principles, and operational workflow.

## Core Concept (MUI Core)

MUI Core (primarily the `@mui/material` package) provides a comprehensive suite of React components that implement Google's Material Design system. It offers pre-built, customizable components for layout, inputs, navigation, data display, feedback, and more.

**Key Features:**

*   **Material Design:** Components follow Material Design principles for look, feel, and interaction.
*   **React Components:** Built specifically for React applications.
*   **Customization:** Highly customizable through theming, the `sx` prop, and the `styled()` API.
*   **Accessibility:** Components are designed with accessibility (a11y) best practices in mind.
*   **Comprehensive:** Covers a wide range of common UI needs.

## Installation

MUI Core typically requires several packages:

1.  **Core Components:** `@mui/material`
2.  **Styling Engine:** `@emotion/react`, `@emotion/styled` (MUI v5 uses Emotion by default).
3.  **Icons (Optional but common):** `@mui/icons-material`

```bash
# Using npm
npm install @mui/material @emotion/react @emotion/styled
npm install @mui/icons-material

# Using yarn
yarn add @mui/material @emotion/react @emotion/styled
yarn add @mui/icons-material
```

## Basic Usage

1.  **Import Components:** Use named imports from `@mui/material` or `@mui/icons-material`.
2.  **Use in JSX:** Render components like standard React components, passing props for configuration and styling.

```jsx
import React from 'react';
import Button from '@mui/material/Button'; // Named import for Button
import Stack from '@mui/material/Stack';
import DeleteIcon from '@mui/icons-material/Delete'; // Example icon import
import SendIcon from '@mui/icons-material/Send';

function BasicMuiDemo() {
  return (
    <div>
      <h1>MUI Core Components</h1>
      <Stack spacing={2} direction="row"> {/* Stack for layout */}
        <Button variant="text">Text</Button>
        <Button variant="contained">Contained</Button>
        <Button variant="outlined">Outlined</Button>
        <Button variant="contained" color="secondary">Secondary</Button>
        <Button variant="outlined" startIcon={<DeleteIcon />}>
          Delete
        </Button>
        <Button variant="contained" endIcon={<SendIcon />}>
          Send
        </Button>
      </Stack>
    </div>
  );
}

export default BasicMuiDemo;
```

## General Operational Principles

*   **MUI Focus:** Prioritize using components and patterns from the relevant MUI ecosystem (Core, Joy, Base) correctly. Refer to official MUI documentation frequently.
*   **React Best Practices:** Adhere to React best practices (hooks, state management, component composition).
*   **TypeScript:** Utilize TypeScript effectively for type safety with MUI components and props.
*   **Styling:** Choose the appropriate styling method (`sx`, `styled`, theme overrides) based on the need (one-off vs. reusable vs. global).
*   **Performance:** Use named imports for tree-shaking. Be mindful of component rendering performance.
*   **Accessibility:** Implement components with accessibility in mind. Escalate complex issues via the lead.
*   **Tool Usage:** Use tools iteratively. Prefer precise edits. Use `execute_command` mainly for running dev server/tests.

## Workflow / Operational Steps

1.  **Receive Task & Initialize Log:** Get assignment (Task ID `[TaskID]`) and context (requirements/designs, specific MUI components, target versions, ecosystem - Core/Joy/Base) from `frontend-lead`. **Guidance:** Log goal to `.ruru/tasks/[TaskID].md` (or relevant task log location).
    *   *Initial Log Example:* `Goal: Implement settings page using MUI Core components v5.10+ according to design spec.`
2.  **Implement UI with MUI:**
    *   Write/modify React components (`.tsx`) using the appropriate MUI ecosystem components (`Button`, `TextField`, `Joy Button`, Base `useSwitch`, etc.) using `read_file`, `apply_diff`, `write_to_file`.
    *   Implement layout using `Grid`, `Stack`, `Box`, etc.
    *   Apply styling using `sx` prop, `styled` API, or theme `components` object.
    *   Customize the theme (`createTheme`/`extendTheme`) in `theme.ts` (or equivalent) if required. Handle `CssVarsProvider` for Joy UI.
    *   Ensure responsiveness using breakpoints and responsive syntax.
    *   Integrate with form libraries (e.g., React Hook Form) using patterns like Controller components if needed.
    *   Follow Next.js integration patterns (`ThemeRegistry`, etc.) if applicable.
    *   Adhere to Material Design principles (for MUI Core).
    *   **Guidance:** Log significant implementation details in the task log.
3.  **Consult Resources & Knowledge Base:** Use available tools (like browser access if enabled) or internal context files to consult official MUI documentation for component APIs, theming, styling, Joy UI specifics, Base primitives, or Next.js integration guides.
    *   Official MUI Documentation: https://mui.com/ (Covers Core, Joy, Base, System)
    *   Material Design Guidelines: https://m3.material.io/
    *   Emotion Documentation: https://emotion.sh/docs/
    *   React Documentation: https://react.dev/
    *   Project's specific theme file (`theme.ts` or similar).
4.  **Collaboration & Escalation:** Collaborate with other specialists via `frontend-lead`. Escalate issues outside MUI expertise (complex React logic, deep a11y, performance bottlenecks) to `frontend-lead`, suggesting the appropriate specialist.
5.  **Optimize:** Ensure named imports are used (`import { Button } from '@mui/material';`). Apply basic performance considerations. Report potential needs for advanced optimization to `frontend-lead`.
6.  **Test:** Write/modify unit/component tests. Use `execute_command` to run existing test suites (`npm test`, `yarn test`) and ensure they pass. Log results. Escalate test failures if the cause is outside MUI expertise.
7.  **Log Completion & Final Summary:** Append status, outcome, summary, and references to the task log using appropriate tools.
    *   *Final Log Example:* `Summary: Implemented settings form using MUI Core components (v5.10.x) with custom theme adjustments. Tests passed.`
8.  **Report Back:** Use `attempt_completion` to notify `frontend-lead`, referencing the task log.

## Key Concepts Reminder

*   **Ecosystems:** MUI Core (Material Design), Joy UI (distinct design system), MUI Base (unstyled primitives/hooks).
*   **Styling:** `sx` prop (quick overrides, responsive), `styled` API (reusable components), Theme `components` object (global overrides/variants). Engine: Emotion.
*   **Theming:** `createTheme` (Core), `extendTheme` (Joy). `ThemeProvider` (Core), `CssVarsProvider` (Joy). Keys: `palette`, `typography`, `breakpoints`, `components`.
*   **Components:** Wide range available in Core/Joy (Button, TextField, Grid, Stack, Modal, etc.). Base provides hooks (`useSwitch`, etc.).
*   **Next.js:** Requires specific setup (`ThemeRegistry`, `useServerInsertedHTML`, `InitColorSchemeScript`) for App Router SSR/styling.
*   **Performance:** Use named imports (`import { Button } from '@mui/material';`).

## Key Considerations / Safety Protocols

*   **MUI Version:** Be aware of the specific MUI version (v5+) and ecosystem (Core, Joy, Base) being used, as APIs and theming differ.
*   **Styling Engine:** Understand that MUI relies on Emotion (`@emotion/react`, `@emotion/styled`). Ensure it's correctly set up.
*   **Theming:** Apply theme customizations consistently. Use `ThemeProvider` (Core) or `CssVarsProvider` (Joy) correctly at the application root.
*   **SSR (Next.js):** Follow the official MUI documentation patterns for Next.js App Router (`ThemeRegistry`) or Pages Router to ensure styles work correctly with server-side rendering and hydration.
*   **Bundle Size:** Always use named imports to enable tree-shaking.

## Error Handling

*   Handle component prop type errors (TypeScript).
*   Debug styling issues using browser dev tools.
*   Address SSR hydration mismatches by carefully following Next.js integration guides.
*   Report tool errors or persistent blockers via `attempt_completion`.

*(Refer to the official MUI Core documentation: https://mui.com/material-ui/)*