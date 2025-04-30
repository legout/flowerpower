# Hooks Overview & Rules

Hooks are functions that let you "hook into" React state and lifecycle features from functional components.

## Rules of Hooks

These rules are essential for Hooks to work correctly:

1.  **Only Call Hooks at the Top Level:**
    *   Do **not** call Hooks inside loops, conditions, or nested functions.
    *   Always use Hooks at the top level of your React function, before any early returns.
    *   This ensures Hooks are called in the same order each time the component renders, which is crucial for React to preserve state between calls.
2.  **Only Call Hooks from React Functions:**
    *   Do **not** call Hooks from regular JavaScript functions.
    *   Call Hooks from:
        *   ✅ React Functional Components
        *   ✅ Custom Hooks (functions whose names start with `use`)

*(Use the `eslint-plugin-react-hooks` ESLint plugin to enforce these rules automatically.)*

## Common Built-in Hooks Summary

*   **State Hooks:**
    *   `useState`: Manage simple local component state. (See `03-hook-useState.md`)
    *   `useReducer`: Manage complex local component state with a reducer function. (See `06-hook-useReducer.md`)
*   **Context Hook:**
    *   `useContext`: Subscribe to context provided by a `Context.Provider`. (See `05-hook-useContext.md`)
*   **Ref Hooks:**
    *   `useRef`: Access DOM nodes or store mutable values that don't trigger re-renders. (See `07-hook-useRef.md`)
    *   `forwardRef`: Forward a ref from a parent to a DOM node inside a child component. (See `07-hook-useRef.md`)
    *   `useImperativeHandle`: Customize the instance value exposed when using `ref` with `forwardRef`. (See `07-hook-useRef.md`)
*   **Effect Hooks:**
    *   `useEffect`: Perform side effects (data fetching, subscriptions, manual DOM changes) after rendering. (See `04-hook-useEffect.md`)
    *   `useLayoutEffect`: Similar to `useEffect`, but fires synchronously after all DOM mutations. Use less often, mainly for measuring DOM layout.
*   **Performance Hooks:**
    *   `useMemo`: Memoize the result of an expensive calculation. (See `08-hooks-performance.md`)
    *   `useCallback`: Memoize a callback function itself, preserving its identity. (See `08-hooks-performance.md`)
    *   `React.memo`: Higher-Order Component to memoize a functional component based on props. (See `08-hooks-performance.md`)
*   **Other Hooks:**
    *   `useId`: Generate unique IDs stable across server/client (useful for accessibility attributes).
    *   `useTransition`: Mark state updates as non-urgent transitions to avoid blocking UI.
    *   `useDeferredValue`: Defer updating a part of the UI.

## Custom Hooks

*   **Concept:** A JavaScript function whose name starts with `use` and that *may* call other Hooks.
*   **Purpose:** Extract component logic into reusable functions. Share stateful logic between components without repeating code or complex patterns like HOCs/render props.
*   **Example:**
    ```jsx
    import { useState, useEffect } from 'react';

    // Custom Hook to fetch data
    function useDataFetcher(url) {
      const [data, setData] = useState(null);
      const [loading, setLoading] = useState(true);
      const [error, setError] = useState(null);

      useEffect(() => {
        setLoading(true);
        fetch(url)
          .then(res => { if (!res.ok) throw new Error('Fetch failed'); return res.json(); })
          .then(setData)
          .catch(setError)
          .finally(() => setLoading(false));
      }, [url]); // Dependency: re-fetch if URL changes

      return { data, loading, error };
    }

    // Usage in a component
    function MyComponent({ userId }) {
      const { data: user, loading, error } = useDataFetcher(`/api/users/${userId}`);

      if (loading) return <p>Loading...</p>;
      if (error) return <p>Error loading user.</p>;

      return <h1>Welcome, {user.name}</h1>;
    }
    ```

*(Refer to the official React Hooks API Reference: https://react.dev/reference/react)*