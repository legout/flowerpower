# Hook: `useContext` & Context API

Sharing state across the component tree without prop drilling using `createContext`, `Provider`, and `useContext`.

## Core Concept: Prop Drilling Problem & Context Solution

*   **Prop Drilling:** Passing data down through multiple layers of nested components via props, even if intermediate components don't need the data themselves. This can become cumbersome and make refactoring difficult.
*   **Context API:** Provides a way to pass data through the component tree without having to pass props down manually at every level. It allows components to "subscribe" to changes in a shared context value.

**Use Cases:**

*   Global state like theme (dark/light mode), user authentication status, language preference.
*   Data that needs to be accessible by many components at different nesting levels.

**Key Parts:**

1.  **`React.createContext(defaultValue)`:**
    *   Creates a Context object. Takes an optional `defaultValue` used only when a component tries to consume the context without a matching Provider higher up the tree.
    *   Returns an object with two components: `Provider` and `Consumer` (though `useContext` hook is preferred over `<Consumer>`).
2.  **`<MyContext.Provider value={sharedValue}>`:**
    *   A component that wraps the part of the component tree that needs access to the context data.
    *   Accepts a `value` prop. All descendant components that consume this context will receive this `value`.
    *   Whenever the `value` prop of the Provider changes, all consuming components below it will re-render.
3.  **`useContext(MyContext)`:**
    *   A hook used within a functional component to *consume* the context value.
    *   Accepts the Context object created by `createContext`.
    *   Returns the current context `value` determined by the *nearest* matching `<MyContext.Provider>` above it in the tree.
    *   Causes the component to re-render whenever the Provider's `value` prop changes.

## Implementation Steps

**1. Create the Context & Provider:**

```typescript
// src/context/ThemeContext.tsx
import React, { createContext, useState, useMemo, useContext } from 'react';

// Define the shape of the context data and methods
interface ThemeContextType {
  theme: 'light' | 'dark';
  toggleTheme: () => void;
}

// Create the context with a default value (used if no Provider is found)
export const ThemeContext = createContext<ThemeContextType | null>(null);

// Create a Provider component to wrap your app or part of it
export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setTheme] = useState<'light' | 'dark'>('light');

  const toggleTheme = () => {
    setTheme(prevTheme => (prevTheme === 'light' ? 'dark' : 'light'));
  };

  // Memoize the context value to prevent unnecessary re-renders of consumers
  const value = useMemo(() => ({ theme, toggleTheme }), [theme]);

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
}

// Optional: Custom hook for consuming the context (provides better error handling)
export function useTheme() {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
}
```

**2. Provide the Context:**

Wrap the relevant part of your application tree with the custom Provider component.

```typescript
// src/app/layout.tsx (Next.js App Router Example)
import { ThemeProvider } from '@/context/ThemeContext';

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        <ThemeProvider> {/* Wrap the part needing the theme context */}
          {children}
        </ThemeProvider>
      </body>
    </html>
  );
}
```

**3. Consume the Context:**

Use the `useContext` hook (or the custom `useTheme` hook) in any functional component *within* the Provider tree.

```typescript
// src/components/ThemedButton.tsx
import React from 'react';
import { useTheme } from '@/context/ThemeContext'; // Use custom hook
import Button from '@mui/material/Button';

function ThemedButton() {
  // Consume context using the custom hook
  const { theme, toggleTheme } = useTheme();

  return (
    <Button
      variant="contained"
      onClick={toggleTheme}
      sx={{
        bgcolor: theme === 'light' ? 'primary.main' : 'secondary.main',
        color: 'white',
      }}
    >
      Toggle Theme (Current: {theme})
    </Button>
  );
}

export default ThemedButton;
```

## Considerations

*   **Performance:** Context causes re-renders. If the `value` provided changes, *all* components consuming that context will re-render.
    *   **Memoize Value:** Always memoize the `value` object/array passed to the Provider using `useMemo` (or `useCallback` for functions) to prevent unnecessary re-renders if the Provider re-renders but the value identity changes without content change.
    *   **Split Contexts:** For unrelated state values, create multiple, smaller contexts instead of one large context object to limit re-renders.
*   **Use Sparingly:** Context is primarily for "global" data needed by many components at different nesting levels (themes, auth). For passing data a few levels down, prop drilling is often simpler.
*   **Alternatives:** For complex global state management with frequent updates, consider dedicated libraries like Zustand, Jotai, Redux, or Recoil, which offer more fine-grained update control.

*(Refer to the official React documentation on Context: https://react.dev/learn/passing-data-deeply-with-context and API reference: https://react.dev/reference/react/useContext)*