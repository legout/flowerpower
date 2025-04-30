# Material UI: Introduction to MUI Base (Unstyled Components & Hooks)

Using MUI Base for unstyled components and hooks.

## Core Concept

MUI Base is the foundation upon which MUI Core (Material Design) and Joy UI are built. It provides a set of **unstyled** ("headless") React components and low-level hooks for building custom design systems from scratch or creating highly customized components without inheriting Material Design or Joy UI styles.

**Key Features:**

*   **Unstyled Components:** Components like `<Button>`, `<Input>`, `<Select>`, `<Slider>`, `<Switch>` are provided without any default visual styles. You apply all styling yourself (using CSS, Tailwind, Emotion, styled-components, etc.).
*   **Accessibility Included:** Components handle essential accessibility features (ARIA attributes, keyboard navigation, focus management) out-of-the-box.
*   **Functionality Hooks:** Low-level hooks (e.g., `useButton`, `useSwitch`, `useSelect`) provide the state management and accessibility logic, allowing you to build completely custom component structures around them.
*   **Design System Agnostic:** Not tied to Material Design or Joy UI aesthetics. Build *your* design system.
*   **Smaller Bundle Size:** Using only MUI Base results in a smaller bundle size compared to including the full MUI Core or Joy UI libraries if you don't need their pre-styled components.

## Installation

MUI Base components are available in the `@mui/base` package.

```bash
# Using npm
npm install @mui/base

# Using yarn
yarn add @mui/base
```

## Using Unstyled Components

Import components from `@mui/base` and apply your own classes or styling solution. Target the component itself and the state classes provided by MUI Base (e.g., `.base--focusVisible`, `.base--disabled`, `.base--active`, `.base--expanded`).

```jsx
import React from 'react';
import { Button as BaseButton } from '@mui/base/Button'; // Import unstyled Button
import { Input as BaseInput } from '@mui/base/Input';   // Import unstyled Input
import { styled } from '@mui/system'; // Or your preferred styling solution
import clsx from 'clsx'; // Utility for conditional classes (optional)

// Example custom styles using styled()
const CustomButton = styled(BaseButton)(({ theme }) => `
  font-family: IBM Plex Sans, sans-serif;
  font-size: 0.875rem;
  line-height: 1.5;
  background-color: #007bff;
  color: white;
  border-radius: 8px;
  font-weight: 600;
  padding: 8px 16px;
  cursor: pointer;
  transition: all 150ms ease;
  border: none;

  &:hover {
    background-color: #0056b3;
  }

  &.base--active { // Class applied by BaseButton on active state
    background-color: #004085;
  }

  &.base--focusVisible { // Class applied for keyboard focus
    outline: 3px solid #a0cfff;
    outline-offset: 2px;
  }

  &.base--disabled { // Class applied when disabled
    background-color: #e0e0e0;
    color: #a0a0a0;
    cursor: not-allowed;
  }
`);

// Example custom styles using CSS Modules
// Assume styles.myInput, styles.myInputInner exist in MyComponent.module.css
// import styles from './MyComponent.module.css';

function BaseComponentsDemo() {
  return (
    <div>
      <h1>MUI Base Unstyled Components</h1>

      {/* Using styled() component */}
      <CustomButton onClick={() => console.log('Clicked!')}>
        Custom Styled Button
      </CustomButton>

      {/* Using CSS Modules (example) */}
      {/*
      <BaseInput
        className={styles.myInput}
        placeholder="Enter text..."
        slotProps={{ // Customize internal slots if needed
          input: {
            className: styles.myInputInner, // Style the actual <input> element
          }
        }}
      />
      */}
    </div>
  );
}

export default BaseComponentsDemo;
```

## Using Functionality Hooks

Hooks provide the logic (state, event handlers, accessibility props) without rendering any DOM elements. You use these hooks in your own components to build the structure and apply the returned props.

```jsx
import React from 'react';
import { useSwitch, UseSwitchParameters } from '@mui/base/useSwitch'; // Import hook and types
import { styled } from '@mui/system'; // Example using MUI System for styling
import clsx from 'clsx';

// Custom styling for the switch elements
const SwitchRoot = styled('span')`/* ... styles ... */`;
const SwitchInput = styled('input')`/* ... styles ... */`;
const SwitchThumb = styled('span')`/* ... styles ... */`;
const SwitchTrack = styled('span')`/* ... styles ... */`;

// Custom Switch component built using the hook
function MyCustomSwitch(props: UseSwitchParameters) {
  const { getInputProps, checked, disabled, focusVisible, readOnly } = useSwitch(props);

  const stateClasses = {
    'base--checked': checked,
    'base--disabled': disabled,
    'base--focusVisible': focusVisible,
    'base--readOnly': readOnly,
  };

  return (
    <SwitchRoot className={clsx(stateClasses)}>
      <SwitchTrack>
        <SwitchThumb className={clsx(stateClasses)} />
      </SwitchTrack>
      <SwitchInput {...getInputProps()} aria-label="Demo switch" /> {/* Spread accessibility props */}
    </SwitchRoot>
  );
}

function BaseHooksDemo() {
  return (
    <div>
      <h1>MUI Base Hooks</h1>
      <MyCustomSwitch defaultChecked />
      <MyCustomSwitch />
      <MyCustomSwitch disabled />
    </div>
  );
}

export default BaseHooksDemo;
```
*   **Key Idea:** Import the hook (e.g., `useSwitch`, `useButton`, `useSlider`, `useTabsList`, etc.) from `@mui/base/*`. Call the hook with necessary parameters. Spread the returned props (`getInputProps`, `getRootProps`, etc.) onto your custom DOM elements. Use the returned state (`checked`, `disabled`, `focusVisible`) to apply conditional styles or classes.

## Common Unstyled Components & Hooks

*   **Button:** `<Button>`, `useButton`
*   **Input:** `<Input>`, `useInput`
*   **Slider:** `<Slider>`, `useSlider`
*   **Switch:** `<Switch>`, `useSwitch`
*   **Select:** `<Select>`, `useSelect`, `<Option>`, `useOption`
*   **Tabs:** `<Tabs>`, `useTabs`, `<TabsList>`, `useTabsList`, `<Tab>`, `useTab`, `<TabPanel>`, `useTabPanel`
*   **Menu:** `<Menu>`, `useMenu`, `<MenuItem>`, `useMenuItem` (often used with Popper)
*   **Popper:** `<Popper>`, `usePopper` (for positioning floating elements)
*   ... and many others.

## When to Use MUI Base

*   When building a completely custom design system not based on Material Design or Joy UI.
*   When you need full control over the HTML structure and styling of components.
*   When you want the accessibility and state logic provided by MUI but without the associated styles.
*   When minimizing bundle size is a critical requirement and you don't need the full styled component libraries.

MUI Base offers a powerful, flexible foundation for building accessible and functional React components with any styling approach.

*(Refer to the official MUI Base documentation: https://mui.com/base-ui/)*