# Hook: `useEffect`

Performing side effects in functional components.

## `useEffect(setupFn, dependencies?)`

*   **Purpose:** Performs **side effects** in functional components. Side effects are operations that interact with the "outside world" beyond rendering the UI, such as:
    *   Data fetching (APIs)
    *   Setting up subscriptions (timers, WebSockets, event listeners)
    *   Manually changing the DOM (less common, usually use state/props or refs)
*   **Syntax:** `useEffect(setupFunction, dependencyArray?)`
*   **`setupFunction`:** The function containing the side effect code. It runs *after* React commits changes to the DOM.
*   **`dependencyArray` (Optional):** Controls when the effect re-runs. **Crucial** for correctness and performance.
    *   **Omitted:** Effect runs after *every* render. (Use with caution, often indicates a potential issue or need for refinement. Can cause infinite loops if the effect itself triggers a re-render).
    *   **`[]` (Empty Array):** Effect runs only *once* after the initial render (component mount). The cleanup function runs only once when the component unmounts. Useful for setting up subscriptions or initial data fetching that doesn't depend on props/state.
    *   **`[prop1, state1]` (Array with values):** Effect runs after the initial render *and* whenever any value in the dependency array has changed between renders. Include **all reactive values** (props, state, functions defined inside the component) that are read inside the effect's setup function. Omitting dependencies can lead to **stale closures**.
*   **Cleanup Function (Optional):** The `setupFunction` can optionally return a cleanup function. This function runs:
    *   Before the component unmounts.
    *   Before the effect runs again (due to a dependency change) to clean up the *previous* effect.
    *   Use this to clean up resources like timers (`clearInterval`), subscriptions, event listeners (`removeEventListener`), or abort fetch requests (`AbortController`) to prevent memory leaks.

## Examples

**1. Timer with Cleanup:**

```jsx
import React, { useState, useEffect } from 'react';

function Timer() {
  const [seconds, setSeconds] = useState(0);

  useEffect(() => {
    // Runs once on mount
    console.log('Setting up interval...');
    const intervalId = setInterval(() => {
      setSeconds(prevSeconds => prevSeconds + 1);
    }, 1000);

    // Cleanup: Runs on unmount
    return () => {
      console.log('Cleaning up interval...');
      clearInterval(intervalId);
    };
  }, []); // Empty dependency array

  return <div>Timer: {seconds} seconds</div>;
}
```

**2. Data Fetching based on Prop:**

```jsx
function UserData({ userId }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Runs on mount AND when userId changes
    setLoading(true);
    console.log(`Fetching data for user ${userId}...`);
    let isCancelled = false;
    const controller = new AbortController(); // For fetch cancellation

    fetch(`/api/users/${userId}`, { signal: controller.signal })
      .then(res => res.ok ? res.json() : Promise.reject(new Error('Fetch failed')))
      .then(data => {
        if (!isCancelled) setUser(data);
      })
      .catch(error => {
        if (error.name !== 'AbortError') { // Ignore abort errors
          console.error(error);
        }
      })
      .finally(() => {
        if (!isCancelled) setLoading(false);
      });

    // Cleanup: Runs if userId changes before fetch completes, or on unmount
    return () => {
      isCancelled = true;
      controller.abort(); // Abort the fetch request
      console.log(`Cleaning up fetch for user ${userId}`);
    };
  }, [userId]); // Dependency array includes userId

  if (loading) return <p>Loading user data...</p>;
  // ... render user data or error ...
  return <div>User Name: {user?.name}</div>;
}
```

## Key Considerations

*   **Side Effects Only:** Use `useEffect` for interactions with the outside world. Avoid using it for calculations based purely on props and state (use regular component logic or `useMemo`).
*   **Dependency Rules:** Always include all reactive values read inside the effect in the dependency array. Use the `eslint-plugin-react-hooks` `exhaustive-deps` rule to help enforce this.
*   **Data Fetching Libraries:** For more complex data fetching scenarios (caching, revalidation, mutations), consider libraries like React Query (TanStack Query) or SWR, which handle many effect-related concerns internally.

*(Refer to the official React documentation for `useEffect`: https://react.dev/reference/react/useEffect)*