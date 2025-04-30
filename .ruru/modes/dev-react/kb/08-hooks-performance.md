# Performance Hooks: `useMemo`, `useCallback`, & `React.memo`

Optimizing React component performance by preventing unnecessary re-renders and calculations.

## Core Concept: Preventing Unnecessary Work

React components re-render when their state or props change. Sometimes, components re-render even if their output would be the same, or expensive calculations run on every render even if inputs haven't changed. React provides hooks and utilities to **memoize** (cache) values, functions, or component outputs to skip unnecessary work.

**Key Tools:**

1.  **`React.memo(Component)`:**
    *   A higher-order component (HOC) that wraps a functional component.
    *   It memoizes the wrapped component. React will skip re-rendering the component if its **props** have not changed (shallow comparison by default).
    *   Useful for components that render often with the same props, especially if they are computationally expensive or deep in the tree.
2.  **`useMemo(computeFn, dependencies)`:**
    *   A hook that memoizes the **result** of an expensive calculation (`computeFn`).
    *   `computeFn` is only re-executed if one of the `dependencies` has changed.
    *   Returns the cached result from the previous render if dependencies are the same.
    *   Use this to avoid re-computing complex values on every render or to memoize object/array references passed as props to memoized children.
3.  **`useCallback(callbackFn, dependencies)`:**
    *   A hook that memoizes a **callback function** itself.
    *   Returns the same function instance between renders as long as its `dependencies` haven't changed.
    *   Crucial when passing callbacks as props to memoized child components (`React.memo`) to prevent them from re-rendering unnecessarily just because the parent created a new function instance on each render.

## Implementation

**1. `React.memo`:**

Wrap functional components that might receive the same props frequently.

```jsx
import React from 'react';

// Assume this component is expensive to render
function UserDetails({ user }) {
  console.log(`Rendering UserDetails for ${user.name}`);
  return (
    <div>
      <p>Name: {user.name}</p>
      <p>Age: {user.age}</p>
    </div>
  );
}

// Wrap the component with React.memo
const MemoizedUserDetails = React.memo(UserDetails);

// Parent component
function UserList({ users }) {
  return (
    <div>
      {users.map(user => (
        // MemoizedUserDetails will only re-render if the specific 'user' prop object changes reference
        <MemoizedUserDetails key={user.id} user={user} />
      ))}
    </div>
  );
}
```
*Note: `React.memo` only does a shallow comparison. If object/array props change identity on every parent render, `React.memo` won't help unless you also memoize the prop creation using `useMemo` or provide a custom comparison function.*

**2. `useMemo`:**

Memoize the result of expensive calculations or object/array references.

```jsx
import React, { useState, useMemo } from 'react';

function calculateExpensiveValue(a, b) {
  console.log('Calculating expensive value...');
  // ... complex logic ...
  return a + b;
}

function Calculator({ numA, numB }) {
  // Re-calculate only when numA or numB changes
  const expensiveResult = useMemo(() => {
    return calculateExpensiveValue(numA, numB);
  }, [numA, numB]); // Dependency array

  // Memoize an object prop for a child component
  const styleOptions = useMemo(() => ({
    color: numA > 10 ? 'red' : 'blue',
    fontWeight: 'bold'
  }), [numA]);

  return (
    <div>
      <p>Expensive Result: {expensiveResult}</p>
      {/* <MemoizedChildComponent options={styleOptions} /> */}
    </div>
  );
}
```

**3. `useCallback`:**

Memoize callback functions, especially when passing them to memoized children.

```jsx
import React, { useState, useCallback } from 'react';

// Assume ListItem is wrapped in React.memo
const MemoizedListItem = React.memo(function ListItem({ item, onRemove }) {
  console.log(`Rendering item ${item.id}`);
  return (
    <li>
      {item.name} <button onClick={() => onRemove(item.id)}>Remove</button>
    </li>
  );
});

function TodoList() {
  const [items, setItems] = useState([{ id: 1, name: 'Task 1' }, { id: 2, name: 'Task 2' }]);
  const [filter, setFilter] = useState(''); // Example other state causing re-renders

  // Without useCallback, a new handleRemove function instance is created on every TodoList render,
  // causing MemoizedListItem to re-render unnecessarily.
  const handleRemove = useCallback((idToRemove) => {
    setItems(prevItems => prevItems.filter(item => item.id !== idToRemove));
  }, []); // Empty dependency array: function identity is stable

  return (
    <div>
      <input type="text" value={filter} onChange={e => setFilter(e.target.value)} placeholder="Filter..." />
      <ul>
        {items.map(item => (
          <MemoizedListItem
            key={item.id}
            item={item}
            onRemove={handleRemove} // Pass the memoized callback
          />
        ))}
      </ul>
    </div>
  );
}
```

## Considerations

*   **Don't Memoize Everything:** Memoization has a cost (memory, comparison). Only apply it where necessary – profile your application first to identify actual bottlenecks.
*   **Dependency Arrays:** Correct dependency arrays are crucial for `useMemo` and `useCallback`. Omitting a dependency leads to stale values/functions. Including unnecessary dependencies negates the optimization. Use the `eslint-plugin-react-hooks` `exhaustive-deps` rule.
*   **Referential Equality:** These optimizations rely on referential equality for non-primitive dependencies (objects, arrays, functions). Ensure dependencies don't change identity unnecessarily on parent renders.

*(Refer to the official React documentation on `React.memo`, `useMemo`, and `useCallback`: https://react.dev/reference/react)*