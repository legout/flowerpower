# Material UI: React & Next.js Integration Patterns

Using MUI components effectively with React state management, hooks, and Next.js SSR.

## Core Concept: React Integration

MUI components are standard React components. Integrating them involves managing component state (like input values, open/close status for modals/drawers) using React hooks (`useState`, `useReducer`) and handling events with standard React event handlers.

## Common React Integration Patterns

**1. Controlled Components:**

*   Many MUI input components (`TextField`, `Select`, `Checkbox`, `RadioGroup`, `Switch`, `Slider`, `Autocomplete`) are designed to be **controlled components**.
*   Their value is controlled by React state. You need:
    *   A state variable (e.g., using `useState`) to hold the component's current value.
    *   To pass this state variable to the component's `value` (or `checked`) prop.
    *   An `onChange` handler function that updates the state variable.

```jsx
import React, { useState } from 'react';
import TextField from '@mui/material/TextField';
import Select, { SelectChangeEvent } from '@mui/material/Select';
import MenuItem from '@mui/material/MenuItem';
import Checkbox from '@mui/material/Checkbox';
import FormControlLabel from '@mui/material/FormControlLabel';
import Box from '@mui/material/Box';
import InputLabel from '@mui/material/InputLabel';
import FormControl from '@mui/material/FormControl';

function ControlledInputs() {
  const [name, setName] = useState('');
  const [age, setAge] = useState('');
  const [agreed, setAgreed] = useState(false);

  const handleNameChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setName(event.target.value);
  };

  const handleAgeChange = (event: SelectChangeEvent) => {
    setAge(event.target.value);
  };

   const handleAgreeChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setAgreed(event.target.checked);
  };

  return (
    <Box component="form" noValidate autoComplete="off">
      <TextField
        label="Name"
        variant="outlined"
        value={name} // Controlled by state
        onChange={handleNameChange} // Update state on change
        margin="normal"
      />

      <FormControl fullWidth margin="normal">
        <InputLabel id="age-label">Age</InputLabel>
        <Select
          labelId="age-label"
          value={age} // Controlled by state
          label="Age"
          onChange={handleAgeChange} // Update state on change
        >
          <MenuItem value={10}>Ten</MenuItem>
          <MenuItem value={20}>Twenty</MenuItem>
          <MenuItem value={30}>Thirty</MenuItem>
        </Select>
      </FormControl>

       <FormControlLabel
         control={
           <Checkbox
             checked={agreed} // Controlled by state
             onChange={handleAgreeChange} // Update state on change
           />
          }
         label="Agree to terms"
       />

      <p>Current Name: {name}</p>
      <p>Current Age: {age}</p>
      <p>Agreed: {agreed ? 'Yes' : 'No'}</p>
    </Box>
  );
}
```
*   **Integration with Form Libraries:** For complex forms, use libraries like React Hook Form or Formik. They often provide wrappers or `Controller` components to integrate controlled MUI inputs smoothly with the form state and validation.

**2. Managing Open/Close State:**

*   Components like `<Dialog>`, `<Drawer>`, `<Menu>`, `<Snackbar>`, `<Popover>` require their visibility to be controlled via an `open` prop managed by React state (`useState`).
*   Provide an `onClose` handler prop to update the state and close the component.

```jsx
import React, { useState } from 'react';
import Button from '@mui/material/Button';
import Dialog from '@mui/material/Dialog';
import DialogTitle from '@mui/material/DialogTitle';
import DialogActions from '@mui/material/DialogActions';

function DialogControlDemo() {
  const [open, setOpen] = useState(false); // State to control dialog visibility

  const handleClickOpen = () => {
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
  };

  return (
    <div>
      <Button onClick={handleClickOpen}>Open Dialog</Button>
      <Dialog open={open} onClose={handleClose}> {/* Pass state and handler */}
        <DialogTitle>Dialog Title</DialogTitle>
        {/* ... DialogContent ... */}
        <DialogActions>
          <Button onClick={handleClose}>Close</Button>
        </DialogActions>
      </Dialog>
    </div>
  );
}
```

**3. Handling Component Callbacks:**

*   Use standard React event handlers (`onClick`, `onChange`, `onSubmit`, etc.) on MUI components.
*   Access event data through the `event` object passed to your handler function.

**4. Conditional Rendering:**

*   Use standard React conditional rendering (e.g., `&&`, ternary operators, `if` statements) to show/hide MUI components based on state or props.

```jsx
import React, { useState } from 'react';
import Button from '@mui/material/Button';
import CircularProgress from '@mui/material/CircularProgress';
import Alert from '@mui/material/Alert';

function ConditionalDemo() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleClick = () => {
    setIsLoading(true);
    setError(null);
    // Simulate API call
    setTimeout(() => {
      // Simulate error or success
      if (Math.random() > 0.5) {
        setError('Failed to load data!');
      }
      setIsLoading(false);
    }, 1500);
  };

  return (
    <div>
      <Button onClick={handleClick} disabled={isLoading}>
        {isLoading ? <CircularProgress size={24} /> : 'Load Data'}
      </Button>

      {error && <Alert severity="error" sx={{ mt: 2 }}>{error}</Alert>}
    </div>
  );
}
```

**5. Refs:**

*   While less common due to the controlled nature of most components, you might occasionally need a ref (`useRef`) to access the underlying DOM node of an MUI component for specific measurements or imperative actions not covered by the component's API. Access the node via `ref.current`.

## Next.js Integration

Patterns for setting up MUI (v5+) with Next.js App Router and Pages Router, ensuring compatibility with Server-Side Rendering (SSR) and styling.

### 1. Next.js App Router (Recommended)

*   **Key Challenge:** Ensuring styles generated by Emotion (MUI's default engine) on the server are correctly injected and hydrated on the client without mismatches.
*   **Solution:** Use a client component (`ThemeRegistry`) to configure the theme provider and handle style injection during SSR.

**Steps:**

1.  **Install Dependencies:**
    ```bash
    npm install @mui/material @emotion/react @emotion/styled
    # Or for Joy UI:
    # npm install @mui/joy @emotion/react @emotion/styled
    ```
2.  **Create `ThemeRegistry.tsx`:** Create a client component to manage theme setup and style injection.
    ```tsx
    // src/components/ThemeRegistry/ThemeRegistry.tsx
    'use client'; // Mark as a Client Component

    import * as React from 'react';
    import { ThemeProvider } from '@mui/material/styles';
    import CssBaseline from '@mui/material/CssBaseline';
    import NextAppDirEmotionCacheProvider from './EmotionCache';
    import theme from './theme'; // Your custom theme (createTheme)

    // Or for Joy UI:
    // import { CssVarsProvider, extendTheme } from '@mui/joy/styles';
    // import CssBaseline from '@mui/joy/CssBaseline';
    // import NextAppDirEmotionCacheProvider from './EmotionCache';
    // import theme from './theme'; // Your custom theme (extendTheme)
    // import { getInitColorSchemeScript } from '@mui/joy/styles';


    export default function ThemeRegistry({ children }: { children: React.ReactNode }) {
      return (
        <NextAppDirEmotionCacheProvider options={{ key: 'mui' }}> {/* or 'joy' */}
          {/* --- MUI Core Setup --- */}
          <ThemeProvider theme={theme}>
            {/* CssBaseline kickstarts an elegant, consistent, and simple baseline to build upon. */}
            <CssBaseline />
            {children}
          </ThemeProvider>

          {/* --- Joy UI Setup --- */}
          {/* <CssVarsProvider theme={theme} defaultMode="system"> */}
            {/* CssBaseline kickstarts an elegant, consistent, and simple baseline to build upon. */}
            {/* <CssBaseline /> */}
            {/* {getInitColorSchemeScript()} {/* Optional: for preventing FOUC with dark/system mode */}
            {/* {children} */}
          {/* </CssVarsProvider> */}
        </NextAppDirEmotionCacheProvider>
      );
    }
    ```
3.  **Create `EmotionCache.tsx`:** Helper component for managing Emotion's cache during SSR. (Copy implementation from official MUI docs or previous examples).
4.  **Create `theme.ts`:** Define your custom theme using `createTheme` (Core) or `extendTheme` (Joy).
5.  **Apply in Root Layout:** Import and use `ThemeRegistry` in your root layout (`src/app/layout.tsx`).
    ```tsx
    // src/app/layout.tsx
    import * as React from 'react';
    import ThemeRegistry from '@/components/ThemeRegistry/ThemeRegistry'; // Adjust path

    export default function RootLayout({ children }: { children: React.ReactNode }) {
      return (
        <html lang="en">
          <body>
            <ThemeRegistry>{children}</ThemeRegistry>
          </body>
        </html>
      );
    }
    ```

### 2. Next.js Pages Router

*   **Key Challenge:** Similar to App Router, ensuring server-rendered styles match client-side hydration.
*   **Solution:** Override `_app.js` and `_document.js`.

**Steps:**

1.  **Install Dependencies:** (Same as App Router)
2.  **Create `theme.ts`:** (Same as App Router)
3.  **Modify `_app.js` (or `.tsx`):** Wrap the `Component` with `ThemeProvider` and `CssBaseline`. Inject Emotion's cache.
    ```jsx
    // pages/_app.js
    import * as React from 'react';
    import PropTypes from 'prop-types';
    import Head from 'next/head';
    import { ThemeProvider } from '@mui/material/styles';
    import CssBaseline from '@mui/material/CssBaseline';
    import { CacheProvider } from '@emotion/react';
    import theme from '../src/theme'; // Adjust path
    import createEmotionCache from '../src/createEmotionCache'; // Helper function

    // Client-side cache, shared for the whole session of the user in the browser.
    const clientSideEmotionCache = createEmotionCache();

    export default function MyApp(props) {
      const { Component, emotionCache = clientSideEmotionCache, pageProps } = props;

      return (
        <CacheProvider value={emotionCache}>
          <Head>
            <meta name="viewport" content="initial-scale=1, width=device-width" />
          </Head>
          <ThemeProvider theme={theme}>
            {/* CssBaseline kickstarts an elegant, consistent, and simple baseline to build upon. */}
            <CssBaseline />
            <Component {...pageProps} />
          </ThemeProvider>
        </CacheProvider>
      );
    }
    // ... PropTypes definition ...
    ```
4.  **Create `createEmotionCache.js`:** Helper to create Emotion cache.
    ```javascript
    // src/createEmotionCache.js
    import createCache from '@emotion/cache';

    export default function createEmotionCache() {
      return createCache({ key: 'css', prepend: true });
    }
    ```
5.  **Modify `_document.js` (or `.tsx`):** Inject server-side generated styles into the `<head>`. (Copy standard MUI `_document.js` setup from official docs).

Integrate MUI components into your React application using standard React patterns. For Next.js, follow the specific setup for your chosen router (App or Pages) to ensure correct SSR and styling.

*(Always refer to the latest official MUI documentation for React and Next.js integration, as patterns can evolve.)*