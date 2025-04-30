+++
# --- Basic Metadata (Auto-Generated) ---
id = "kb-dev-react-performance"
title = "KB: React Performance Optimization for React Specialist"
context_type = "knowledge_base"
scope = "Techniques for optimizing React application performance relevant to the dev-react mode"
target_audience = ["dev-react"]
granularity = "techniques"
status = "active"
last_updated = "2025-04-19" # << GENERATED DATE >>
# version = "1.0"
tags = ["react", "performance", "optimization", "memoization", "code-splitting", "profiling", "hooks"]
# relevance = "High relevance for building efficient applications"
# related_context = ["kb-dev-react-core-concepts", "kb-dev-react-component-practices"]
# --- Mode-Specific Details ---
target_mode_slug = "dev-react"
+++

# React Performance Optimization Techniques

This document covers key performance optimization techniques that the `dev-react` (React Specialist) mode should employ to build efficient React applications.

## 1. Understanding React's Rendering Behavior

React components re-render when their state or props change. Unnecessary re-renders are a common source of performance issues. The goal is to ensure components only re-render when absolutely necessary.

## 2. Memoization

Memoization is an optimization technique used primarily to speed up function calls by caching their results and returning the cached result when the same inputs occur again. In React, it helps prevent unnecessary re-renders.

*   **`React.memo`:** A Higher-Order Component (HOC) that memoizes functional components. It performs a shallow comparison of the component's props. If the props haven't changed, React skips re-rendering the component and reuses the last rendered result.

    ```jsx
    import React from 'react';

    function MyComponent({ value }) {
      // Expensive calculation or rendering logic
      return <div>{value}</div>;
    }

    // Memoized version: only re-renders if 'value' prop changes
    const MemoizedComponent = React.memo(MyComponent);
    ```

*   **`useCallback`:** A Hook that returns a memoized version of a callback function. It's useful when passing callbacks to optimized child components that rely on reference equality to prevent unnecessary renders (e.g., when used with `React.memo`).

    ```jsx
    import React, { useState, useCallback } from 'react';
    import MemoizedComponent from './MemoizedComponent';

    function ParentComponent() {
      const [count, setCount] = useState(0);
      const [otherState, setOtherState] = useState(false);

      // Without useCallback, handleClick would get a new reference on every ParentComponent render,
      // potentially causing MemoizedComponent to re-render even if count hasn't changed.
      const handleClick = useCallback(() => {
        setCount(prevCount => prevCount + 1);
      }, []); // Empty dependency array: function reference never changes

      return (
        <div>
          <button onClick={() => setOtherState(!otherState)}>Toggle Other State</button>
          {/* Pass the memoized callback */}
          <MemoizedComponent onButtonClick={handleClick} />
          <p>Count: {count}</p>
        </div>
      );
    }
    ```

*   **`useMemo`:** A Hook that returns a memoized value. Pass a "create" function and an array of dependencies. `useMemo` will only recompute the memoized value when one of the dependencies has changed. Useful for expensive calculations within a component.

    ```jsx
    import React, { useState, useMemo } from 'react';

    function ExpensiveCalculationComponent({ list }) {
      const [filter, setFilter] = useState('');

      // Expensive calculation: only re-runs if 'list' or 'filter' changes
      const filteredList = useMemo(() => {
        console.log('Filtering list...');
        return list.filter(item => item.includes(filter));
      }, [list, filter]);

      return (
        <div>
          <input type="text" value={filter} onChange={e => setFilter(e.target.value)} />
          <ul>
            {filteredList.map(item => <li key={item}>{item}</li>)}
          </ul>
        </div>
      );
    }
    ```

## 3. Code Splitting

Code splitting is a technique supported by bundlers like Webpack, Rollup, and Parcel, which can create multiple bundles that can be dynamically loaded at runtime. This allows you to "lazy load" just the code that is needed for the initial render, improving load times.

*   **`React.lazy`:** A function that lets you render a dynamic import as a regular component. It takes a function that must call a dynamic `import()`. This must return a Promise which resolves to a module with a `default` export containing a React component.
*   **`Suspense`:** A component that lets you specify loading indicators (like a spinner) if the components in the tree below it are not yet ready to render (e.g., while waiting for a `React.lazy` component to load).

    ```jsx
    import React, { Suspense, lazy } from 'react';

    // Dynamically import OtherComponent
    const OtherComponent = lazy(() => import('./OtherComponent'));

    function MyComponent() {
      return (
        <div>
          <h1>My App</h1>
          {/* Display fallback while OtherComponent is loading */}
          <Suspense fallback={<div>Loading...</div>}>
            <OtherComponent />
          </Suspense>
        </div>
      );
    }
    ```

## 4. Windowing / Virtualization

For rendering large lists or tables, rendering every item can be very slow and consume significant memory. Windowing libraries (like `react-window` or `react-virtualized`) only render the items currently visible within the viewport (the "window"), dramatically improving performance for long lists.

## 5. Profiling

*   **React DevTools Profiler:** Use the Profiler tab in the React DevTools browser extension to record rendering performance, identify components that render unnecessarily, and measure the cost of rendering.
*   **Browser Performance Tools:** Utilize the browser's built-in performance profiling tools to analyze JavaScript execution time, layout shifts, and painting.

By applying these techniques judiciously, the `dev-react` mode can significantly improve the performance and user experience of React applications. Remember to profile before and after optimizations to measure their impact.