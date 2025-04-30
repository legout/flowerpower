# Hook: `useState`

Managing simple local component state.

## `useState(initialState)`

*   **Purpose:** The most basic hook for adding state to a functional component. Allows the component to "remember" information between renders. Use it for simple state values (strings, numbers, booleans, simple objects/arrays).
*   **Syntax:** `const [state, setState] = useState(initialValue);`
*   **Returns:** An array with two elements:
    1.  `state`: The current state value for this render.
    2.  `setState`: A function to update the state value. Calling `setState` triggers a re-render of the component with the new state value.
*   **Updating State:**
    *   `setState(newValue)`: Replaces the state with `newValue`.
    *   `setState(prevState => newValue)`: **Updater function**. Recommended when the new state depends on the previous state. Receives the pending state and returns the new state. React ensures this uses the correct previous state, even with batching.
*   **Immutability:** **Crucial!** Never mutate state directly. Always use the setter function. For objects and arrays, create *new* objects/arrays with the changes.
    ```jsx
    // Incorrect: Mutating state directly
    // user.name = 'New Name'; setUser(user);
    // list.push('New Item'); setList(list);

    // Correct: Creating new objects/arrays
    setUser(prevUser => ({ ...prevUser, name: 'New Name' }));
    setList(prevList => [...prevList, 'New Item']);
    ```
*   **Updater Function:** When the new state depends on the previous state (like a counter), pass a function to the setter (`setCount(prevCount => prevCount + 1)`). React guarantees `prevCount` will be the correct, up-to-date state value, avoiding potential issues with stale closures in asynchronous updates or when batching multiple updates.

## Example

```jsx
import React, { useState } from 'react';

function Counter() {
  // Initialize state variable 'count' to 0
  const [count, setCount] = useState(0);
  const [user, setUser] = useState({ name: 'Anon', age: 0 });

  const increment = () => {
    // Use updater function when new state depends on previous
    setCount(prevCount => prevCount + 1);
    setCount(prevCount => prevCount + 1); // Correctly increments by 2 due to updater functions
  };

  const setName = (newName) => {
    // Create a new object when updating object state
    setUser(prevUser => ({ ...prevUser, name: newName }));
  };

  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={increment}>Increment</button>
      <button onClick={() => setCount(0)}>Reset</button>

      <p>User: {user.name}</p>
      <button onClick={() => setName('Alice')}>Set Name to Alice</button>
    </div>
  );
}
```

*(Refer to the official React documentation for `useState`: https://react.dev/reference/react/useState)*