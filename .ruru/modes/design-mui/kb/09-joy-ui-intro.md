# Material UI: Introduction to Joy UI & Components

Overview of Joy UI, MUI's library for custom design systems, and its common components.

## Core Concept: Joy UI

Joy UI is a library of beautifully designed React UI components, part of the MUI ecosystem but distinct from MUI Core (Material Design). It's designed to be a great starting point for building **custom design systems** quickly, offering a different aesthetic and more direct customization via CSS variables.

**Key Differences from MUI Core:**

*   **Design System:** Implements its own flexible, modern design system, not strictly Material Design. Has a distinct, often more "playful" or "modern" default aesthetic.
*   **Styling:** Primarily customized using **CSS variables**. Uses `<CssVarsProvider>` instead of `<ThemeProvider>`.
*   **Component Set:** Offers a similar range of components (buttons, inputs, cards, etc.) but with potentially different APIs and styling approaches compared to MUI Core.
*   **`sx` Prop:** Widely used for component customization and responsive styles, similar to MUI Core.
*   **Typography:** Uses `level` prop instead of `variant`.

## Installation

Joy UI components and styling utilities are in the `@mui/joy` package. It still relies on Emotion.

```bash
# Using npm
npm install @mui/joy @emotion/react @emotion/styled

# Using yarn
yarn add @mui/joy @emotion/react @emotion/styled
```

## Setup (`<CssVarsProvider>`)

Joy UI requires wrapping your application with `<CssVarsProvider>` from `@mui/joy/styles` to enable its CSS variable-based theming and automatic dark/light mode switching.

1.  **Create Theme (Optional):** Use `extendTheme` from `@mui/joy/styles` to customize the default Joy theme (palette, typography, variants, etc.). Define customizations within `colorSchemes.light` and `colorSchemes.dark`.
2.  **Provide Theme:** Wrap your app root with `<CssVarsProvider>` and pass your custom `theme`. Use `<CssBaseline />` from `@mui/joy` to apply base styling.

```typescript
// src/joyTheme.ts (Optional theme customization)
import { extendTheme } from '@mui/joy/styles';

const joyTheme = extendTheme({
  fontFamily: {
    body: '"Inter", sans-serif', // Example: Set custom font
  },
  colorSchemes: {
    light: {
      palette: {
        primary: {
          solidBg: '#007FFF', // Example: Set primary button background for light mode
          // ... other variants 50, 100, ..., 900
        },
      },
    },
    dark: {
      palette: {
        primary: {
          solidBg: '#3399FF', // Example: Set primary button background for dark mode
        },
        background: {
          body: '#1A1A1A', // Example: Dark background
        }
      },
    },
  },
  // Add component overrides if needed
  // components: { ... }
});

export default joyTheme;

// src/main.tsx (Vite example)
import React from 'react';
import ReactDOM from 'react-dom/client';
import { CssVarsProvider, extendTheme } from '@mui/joy/styles';
import CssBaseline from '@mui/joy/CssBaseline';
// import joyTheme from './joyTheme'; // Import custom theme if created
import App from './App'; // Your app using Joy components
import { getInitColorSchemeScript } from '@mui/joy/styles'; // Optional: for preventing FOUC

// const theme = extendTheme(); // Or use default theme
// const theme = joyTheme; // Or use custom theme

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    {/* defaultMode="system" enables auto dark/light mode based on OS preference */}
    <CssVarsProvider
      // theme={theme} // Provide custom theme if you have one
      defaultMode="system"
    >
      <CssBaseline /> {/* Joy UI's baseline */}
      {getInitColorSchemeScript()} {/* Optional: for preventing FOUC with dark/system mode */}
      <App />
    </CssVarsProvider>
  </React.StrictMode>,
);
```

## Using Joy UI Components

Import components from `@mui/joy` and use them similarly to MUI Core components. Styling often relies more heavily on the `variant` (`solid`, `soft`, `outlined`, `plain`) and `color` props, which map directly to theme CSS variables. The `sx` prop is also available for overrides.

## Common Components (Examples)

*   **Button:**
    ```jsx
    import Button from '@mui/joy/Button';
    import SomeIcon from '@mui/icons-material/Favorite'; // Example icon

    <Button variant="solid" color="primary" size="lg">Solid Button</Button>
    <Button variant="outlined" color="neutral">Outlined</Button>
    <Button variant="soft" loading>Loading</Button>
    <Button startDecorator={<SomeIcon />}>With Icon</Button>
    ```
*   **Input:**
    ```jsx
    import Input from '@mui/joy/Input';
    import FormControl from '@mui/joy/FormControl';
    import FormLabel from '@mui/joy/FormLabel';
    import FormHelperText from '@mui/joy/FormHelperText';

    <FormControl error={/* condition */}>
      <FormLabel>Email</FormLabel>
      <Input type="email" placeholder="Enter email" required />
      <FormHelperText>This is required.</FormHelperText>
    </FormControl>
    ```
*   **Card:**
    ```jsx
    import Card from '@mui/joy/Card';
    import CardContent from '@mui/joy/CardContent';
    import CardOverflow from '@mui/joy/CardOverflow'; // For images/media
    import Typography from '@mui/joy/Typography';
    import AspectRatio from '@mui/joy/AspectRatio'; // For images

    <Card variant="outlined" sx={{ width: 320 }}>
      <CardOverflow>
        <AspectRatio ratio="2">
          <img src="..." alt="" />
        </AspectRatio>
      </CardOverflow>
      <CardContent>
        <Typography level="title-lg">Card Title</Typography>
        <Typography level="body-sm">Card description goes here.</Typography>
      </CardContent>
    </Card>
    ```
*   **Layout (`Box`, `Stack`, `Grid`):** Similar concepts to MUI Core, but import from `@mui/joy`.
    ```jsx
    import Box from '@mui/joy/Box';
    import Stack from '@mui/joy/Stack';
    import Grid from '@mui/joy/Grid'; // Note: Joy UI Grid might be less feature-rich than Core's

    <Stack direction="row" spacing={2}>
      <Button>One</Button>
      <Button>Two</Button>
    </Stack>
    ```
*   **Typography:** Uses `level` prop instead of `variant`.
    ```jsx
    import Typography from '@mui/joy/Typography';
    <Typography level="h1">Heading 1</Typography>
    <Typography level="body-md">Body text</Typography>
    ```
*   **Other Components:** `Sheet` (general purpose container), `Select`, `Checkbox`, `Radio`, `Switch`, `Textarea`, `Modal`, `Drawer`, `Menu`, `List`, `Table`, etc.
*   **Mode Toggle:** Use `useColorScheme` hook.
    ```jsx
    import DarkModeIcon from '@mui/icons-material/DarkMode';
    import { useColorScheme } from '@mui/joy/styles';

    function ModeToggle() {
      const { mode, setMode } = useColorScheme();
      return (
        <Button onClick={() => setMode(mode === 'dark' ? 'light' : 'dark')}>
          <DarkModeIcon /> Toggle Mode
        </Button>
      );
    }
    ```

## Styling with `sx` Prop

Works similarly to MUI Core, allowing direct access to theme tokens (CSS variables in Joy UI) and responsive styles.

```jsx
<Box
  sx={{
    p: 2, // theme.spacing(2)
    bgcolor: 'background.surface', // var(--joy-palette-background-surface)
    borderRadius: 'sm', // var(--joy-radius-sm)
    boxShadow: 'md', // var(--joy-shadow-md)
    mt: { xs: 1, md: 2 }, // Responsive margin-top
    '&:hover': { // Pseudo-selector
      bgcolor: 'primary.softHoverBg', // var(--joy-palette-primary-softHoverBg)
    }
  }}
>
  Styled Box
</Box>
```

Joy UI offers a distinct alternative to MUI Core, particularly well-suited for projects needing a unique design system or leveraging CSS variables extensively, especially for features like dark/light mode toggling.

*(Refer to the official Joy UI documentation: https://mui.com/joy-ui/getting-started/)*