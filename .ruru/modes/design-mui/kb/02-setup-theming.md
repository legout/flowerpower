# Material UI: Setup & Theming (MUI Core & Joy UI)

Customizing the look and feel of MUI components using themes.

## Core Concept: Theming

MUI theming allows you to define a consistent design language (colors, typography, spacing, component styles) across your application.

*   **MUI Core:** Uses `createTheme` and `<ThemeProvider>`. Based on Material Design principles but highly customizable.
*   **Joy UI:** Uses `extendTheme` and `<CssVarsProvider>`. Has its own design system and relies heavily on CSS variables for theming and mode switching (light/dark).

## MUI Core Theming (`@mui/material`)

1.  **Create Theme:** Use `createTheme` from `@mui/material/styles` to define your theme object. You can customize various keys:
    *   `palette`: Define primary, secondary, error, warning, info, success colors, background colors, text colors. Each color object has `main`, `light`, `dark`, `contrastText`.
    *   `typography`: Define font family, sizes (`h1`-`h6`, `body1`, `button`, etc.), weights.
    *   `spacing`: Base spacing unit (default 8px). Use `theme.spacing(multiplier)` in styles.
    *   `breakpoints`: Customize screen size breakpoints (`xs`, `sm`, `md`, `lg`, `xl`).
    *   `shape`: Border radius values.
    *   `components`: Override default props and styles for specific MUI components globally.
    *   `zIndex`: Manage z-index values.

    ```typescript
    // src/theme.ts (Example)
    import { createTheme, responsiveFontSizes } from '@mui/material/styles';
    import { red } from '@mui/material/colors';

    // Create a theme instance.
    let theme = createTheme({
      palette: {
        primary: {
          main: '#556cd6', // Custom primary color
        },
        secondary: {
          main: '#19857b',
        },
        error: {
          main: red.A400,
        },
        background: {
          default: '#f4f6f8',
        }
        // mode: 'light', // Can set default mode here
      },
      typography: {
        fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
        fontSize: 14,
        h1: {
          fontSize: '2.5rem',
          fontWeight: 500,
        },
        // ... other typography variants
      },
      spacing: 8, // Base spacing unit (8px)
      shape: {
        borderRadius: 4,
      },
      components: {
        // Example: Override default props for MuiButton
        MuiButton: {
          defaultProps: {
            disableElevation: true, // Disable shadow by default
            variant: 'contained', // Default variant
          },
          styleOverrides: {
            // Example: Apply styles to the root element of contained buttons
            root: ({ ownerState, theme }) => ({
              ...(ownerState.variant === 'contained' &&
                ownerState.color === 'primary' && {
                  // Custom styles for primary contained buttons
                  // backgroundColor: theme.palette.primary.dark,
                  // '&:hover': {
                  //   backgroundColor: theme.palette.primary.main,
                  // },
              }),
              textTransform: 'none', // No uppercase text
              padding: theme.spacing(1, 3), // Use theme spacing
            }),
            containedPrimary: { // Style specific variant/color
              '&:hover': {
                backgroundColor: '#3e52a3',
              },
            },
          },
          variants: [ // Define custom variants
            {
              props: { variant: 'dashed', color: 'secondary' },
              style: {
                border: `2px dashed ${red[500]}`,
              },
            },
          ],
        },
        // Override other components... MuiTextField, MuiAppBar, etc.
      },
    });

    // Optional: Make typography responsive
    theme = responsiveFontSizes(theme);

    export default theme;
    ```

2.  **Apply Theme:** Wrap your application's root component (e.g., in `_app.tsx` for Next.js Pages Router, `layout.tsx` for App Router, `main.tsx` for Vite) with `<ThemeProvider>` from `@mui/material/styles` and pass your created `theme` object. Add `<CssBaseline />` to apply baseline styles (like background color, box-sizing).

    ```typescript
    // Example: src/app/layout.tsx (Next.js App Router with ThemeRegistry)
    // See MUI docs for full ThemeRegistry implementation for SSR/caching
    import ThemeRegistry from './ThemeRegistry'; // Your custom registry component

    export default function RootLayout({ children }) {
      return (
        <html lang="en">
          <body>
            <ThemeRegistry options={{ key: 'mui' }}> {/* Wraps ThemeProvider & CssBaseline */}
              {children}
            </ThemeRegistry>
          </body>
        </html>
      );
    }

    // Example: src/main.tsx (Vite)
    // import React from 'react';
    // import ReactDOM from 'react-dom/client';
    // import { ThemeProvider } from '@mui/material/styles';
    // import CssBaseline from '@mui/material/CssBaseline';
    // import theme from './theme';
    // import App from './App';

    // ReactDOM.createRoot(document.getElementById('root')!).render(
    //   <React.StrictMode>
    //     <ThemeProvider theme={theme}>
    //       <CssBaseline /> {/* Apply baseline styles */}
    //       <App />
    //     </ThemeProvider>
    //   </React.StrictMode>,
    // );
    ```

## Joy UI Theming (`@mui/joy`)

1.  **Create Theme:** Use `extendTheme` from `@mui/joy/styles`. Joy UI uses CSS variables extensively. Customizations often involve defining `colorSchemes` (for light/dark modes) and overriding tokens.
    ```javascript
    // src/theme.js (or .ts)
    import { extendTheme } from '@mui/joy/styles';

    const theme = extendTheme({
      colorSchemes: {
        light: {
          palette: {
            primary: {
              solidBg: '#0B6BCB', // Main solid background for primary
              solidHoverBg: '#0959A9',
              // ... other shades: solidActiveBg, outlinedColor, outlinedBorder, etc.
              50: '#E3F2FD', // Lightest shade
              // ... 100, 200, ..., 900 (Darkest shade)
            },
            // Define neutral, danger, success, warning palettes similarly
            background: {
              body: 'var(--joy-palette-neutral-50)', // Example using another token
              surface: '#fff',
            },
          },
        },
        dark: {
          palette: {
            primary: {
              solidBg: '#65B3F0',
              solidHoverBg: '#7CC0F3',
              // ... other shades
            },
            background: {
              body: 'var(--joy-palette-common-black)',
              surface: 'var(--joy-palette-neutral-900)',
            },
          },
        },
      },
      fontFamily: {
        body: '"Inter", var(--joy-fontFamily-fallback)', // Example font stack
        display: '"Poppins", var(--joy-fontFamily-fallback)',
      },
      typography: {
        h1: {
          fontSize: '3rem',
        },
      },
      radius: { // Border radius tokens
        sm: '4px',
        md: '8px',
        lg: '12px',
      },
      shadow: { // Shadow tokens
        sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
        md: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
      },
      // Component overrides (less common than Core, often done via sx or styled)
      // components: {
      //   JoyButton: {
      //     styleOverrides: {
      //       root: ({ ownerState, theme }) => ({
      //         ...(ownerState.size === 'lg' && {
      //           padding: '12px 24px',
      //         }),
      //       }),
      //     },
      //   },
      // },
    });

    export default theme;
    ```
2.  **Apply Theme:** Wrap your application root with `<CssVarsProvider>` from `@mui/joy/styles`. Add `<CssBaseline />` from `@mui/joy`.
    ```jsx
    // src/App.js (or equivalent root)
    import * as React from 'react';
    import { CssVarsProvider } from '@mui/joy/styles';
    import CssBaseline from '@mui/joy/CssBaseline';
    import theme from './theme';
    // ... other imports

    function App() {
      return (
        <CssVarsProvider theme={theme} defaultMode="system"> {/* Handles light/dark mode */}
          <CssBaseline />
          {/* Rest of your application */}
        </CssVarsProvider>
      );
    }
    ```

Theming is central to customizing MUI. Define your design tokens (colors, typography, spacing) in the theme object for application-wide consistency.

*(Refer to the official MUI Theming documentation for Core and Joy UI for comprehensive details.)*