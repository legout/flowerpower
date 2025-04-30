# Material UI: Styling Solutions (`sx` Prop, `styled`)

Applying custom styles to MUI components using the `sx` prop and `styled` API.

## Core Concept: Styling Approaches

MUI provides several ways to apply custom styles, leveraging the underlying Emotion styling engine.

1.  **`sx` Prop (Recommended for One-Off Styles):**
    *   A prop available on most MUI components (`@mui/material`, `@mui/joy`).
    *   Allows writing CSS directly as a JavaScript object, with access to theme values.
    *   Supports responsive values, shorthand properties, and pseudo-classes.
    *   Ideal for applying instance-specific overrides or minor adjustments without creating new components.
2.  **`styled()` API (Recommended for Reusable Styled Components):**
    *   A function (imported from `@mui/material/styles` or `@mui/joy/styles`) similar to Emotion's or styled-components' API.
    *   Creates a *new* React component with baked-in styles.
    *   Accepts an MUI component (or HTML tag) and applies styles defined in a template literal or object.
    *   Can access theme values and component props within the styles.
    *   Ideal for creating reusable, custom-styled versions of MUI components or entirely new styled elements.
3.  **Theme Overrides (`components` Key):**
    *   Define default props and global style overrides for specific components within the `createTheme` options. (See `02-setup-theming.md`).
    *   Best for applying consistent modifications to a component across the entire application.
4.  **Plain CSS / CSS Modules / Other Libraries:** You can still use traditional CSS, CSS Modules, Tailwind, etc., alongside MUI, but MUI's built-in solutions offer better integration with the theme.

## 1. `sx` Prop

*   **Syntax:** `sx={ { cssProperty: value, ... } }`
*   **Theme Access:** Access theme values directly (e.g., `primary.main`, `spacing(2)`) or using a callback function: `theme => ({...})`.
*   **Shorthand:** Uses MUI System properties for common CSS rules (e.g., `p` for padding, `m` for margin, `bgcolor` for background-color, `color` for text color). Values often map to `theme.spacing()` or `theme.palette`.
*   **Responsiveness:** Use arrays or objects for breakpoint-specific styles.
    *   Array: `[defaultValue, smValue, mdValue, ...]` (maps to theme breakpoints `xs`, `sm`, `md`, ...). `null` skips a breakpoint.
    *   Object: `{ xs: value, sm: value, md: value, ... }`.
*   **Pseudo-Selectors & Nested Selectors:** Target pseudo-classes (`:hover`, `:focus`, etc.) and child elements using the `&` symbol.

```jsx
import React from 'react';
import Box from '@mui/material/Box'; // Or '@mui/joy/Box'
import Button from '@mui/material/Button';
import Typography from '@mui/material/Typography';

function SxPropDemo() {
  return (
    <Box
      sx={{
        p: 2, // Padding using theme spacing (p: 2 = theme.spacing(2) = 16px by default)
        m: 1, // Margin
        bgcolor: 'background.paper', // Background color from theme palette
        boxShadow: 1, // Box shadow level from theme
        borderRadius: 1, // Border radius from theme.shape
        width: '100%',
        maxWidth: 500,
        // Responsive width using object syntax
        width: { xs: '90%', sm: '80%', md: '70%' },
        // Responsive padding using array syntax
        padding: [1, 2, 3], // p: 8px (xs), 16px (sm), 24px (md and up)
        // Access theme directly for complex values
        border: theme => `1px solid ${theme.palette.divider}`,
        // Pseudo-classes
        '&:hover': {
          bgcolor: 'primary.light',
          boxShadow: 4,
        },
        // Nested selectors
        '& .child-element': {
          fontWeight: 'bold',
        },
      }}
    >
      <Typography variant="h6" sx={{ mb: 2 }}> {/* Margin bottom */}
        Styled Box
      </Typography>
      <span className="child-element">Child</span>
      <Button
        variant="contained"
        sx={{
          bgcolor: 'secondary.main', // Override button background
          color: 'white',
          '&:hover': { bgcolor: 'secondary.dark' },
        }}
      >
        Custom Button
      </Button>
    </Box>
  );
}

export default SxPropDemo;
```

## 2. `styled()` API

*   **Syntax:** `const MyStyledComponent = styled(BaseComponent | 'htmlTag', [options])(styles)`
*   **`BaseComponent`:** An MUI component or any valid React component.
*   **`'htmlTag'`:** A string like `'div'`, `'button'`, etc.
*   **`options` (Optional):** `{ shouldForwardProp: (prop) => boolean, label: 'MyComponent', ... }`. Controls which props are passed to the underlying component.
*   **`styles`:** Can be:
    *   A tagged template literal (using backticks `` ` ``) with CSS strings. Can interpolate theme/props via `${props => ...}`.
    *   An object similar to the `sx` prop.
    *   A callback function `(props) => ({...})` receiving component props (including `theme`). For MUI components, custom props are often nested under `ownerState`.

```jsx
import React from 'react';
import { styled } from '@mui/material/styles'; // Or @mui/joy/styles
import Button from '@mui/material/Button';
import Box from '@mui/material/Box';

// Example 1: Styling an MUI Component using object/callback syntax
const CustomButton = styled(Button, {
  shouldForwardProp: (prop) => prop !== 'variantColor', // Don't pass custom 'variantColor' prop to DOM
  label: 'CustomButton', // For debugging/dev tools
})(({ theme, variantColor = 'primary' }) => ({ // Access theme and props
  padding: theme.spacing(1, 4),
  backgroundColor: theme.palette[variantColor]?.main || theme.palette.primary.main,
  color: theme.palette.getContrastText(theme.palette[variantColor]?.main || theme.palette.primary.main),
  '&:hover': {
    backgroundColor: theme.palette[variantColor]?.dark || theme.palette.primary.dark,
  },
  // Responsive styles
  [theme.breakpoints.down('sm')]: {
    padding: theme.spacing(0.5, 2),
    fontSize: '0.8rem',
  },
}));

// Example 2: Styling an HTML tag using template literal
const StyledCard = styled('div')`
  padding: ${({ theme }) => theme.spacing(2)}; /* Access theme in template literal */
  border-radius: ${({ theme }) => theme.shape.borderRadius}px;
  box-shadow: ${({ theme }) => theme.shadows[3]};
  background-color: ${({ theme }) => theme.palette.background.paper};
  margin-bottom: ${({ theme }) => theme.spacing(2)};

  h3 {
    margin-top: 0;
    color: ${({ theme }) => theme.palette.secondary.main};
  }
`;

function StyledApiDemo() {
  return (
    <Box>
      <CustomButton variantColor="secondary">Styled MUI Button</CustomButton>
      <CustomButton sx={{ ml: 2 }}>Default Primary</CustomButton> {/* Can still use sx */}

      <StyledCard>
        <h3>Styled HTML Div</h3>
        <p>This div is styled using the styled() API.</p>
      </StyledCard>
    </Box>
  );
}

export default StyledApiDemo;
```

## `sx` Prop vs. `styled()` API

*   **`sx` Prop:**
    *   **Use Case:** One-off styles, quick overrides, responsive adjustments on a single component instance.
    *   **Pros:** Concise, easy for simple overrides, direct theme access.
    *   **Cons:** Styles are applied inline (less performant for many instances), less reusable for complex style sets.
*   **`styled()` API:**
    *   **Use Case:** Creating reusable components with encapsulated styles, complex conditional styling based on props, defining component variants.
    *   **Pros:** Highly reusable, better performance (styles are generated as classes), clean separation of style logic.
    *   **Cons:** Slightly more verbose for simple overrides, requires creating a new component definition.

**General Guideline:** Use `sx` for quick, instance-specific tweaks and responsive adjustments. Use `styled()` for defining reusable styled components or components with complex, prop-driven style logic. Combine these with global theme overrides for a comprehensive styling strategy.

*(Refer to the official MUI documentation on Styling, the `sx` prop, and the `styled()` API.)*