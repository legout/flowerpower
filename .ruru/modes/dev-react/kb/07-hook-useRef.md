# Hook: `useRef`, `forwardRef`, `useImperativeHandle`

Accessing DOM nodes directly and managing mutable values that don't trigger re-renders using refs.

## 1. `useRef(initialValue)`

*   **Purpose:** Returns a mutable `ref` object whose `.current` property is initialized to the passed `initialValue`. The returned object persists for the full lifetime of the component.
*   **Two Main Uses:**
    1.  **Accessing DOM Nodes:** Attach the `ref` object to a DOM element's `ref` attribute to get direct access to that node for imperative actions (e.g., managing focus, text selection, media playback, measuring dimensions).
    2.  **Storing Mutable Values:** Keep track of a value that can change over time but whose change **should not** trigger a component re-render (unlike state). Useful for interval IDs, subscription objects, previous state values, etc.
*   **Syntax & Example (DOM Access):**
    ```jsx
    import React, { useRef, useEffect } from 'react';

    function FocusInput() {
      // Initialize ref for DOM node access (initial value is null)
      const inputRef = useRef<HTMLInputElement>(null);

      useEffect(() => {
        // Access the DOM node via inputRef.current after mount
        inputRef.current?.focus(); // Use optional chaining ?.
      }, []); // Run only once on mount

      return (
        <div>
          <label htmlFor="myInput">Focus Me:</label>
          {/* Attach the ref to the input element */}
          <input ref={inputRef} type="text" id="myInput" />
        </div>
      );
    }
    ```
*   **Example (Mutable Value):**
    ```jsx
    import React, { useState, useEffect, useRef } from 'react';

    function IntervalTimer() {
      const [seconds, setSeconds] = useState(0);
      // Use ref to store the interval ID
      const intervalRef = useRef<NodeJS.Timeout | null>(null);

      useEffect(() => {
        // Store the interval ID in ref.current (mutating does NOT re-render)
        intervalRef.current = setInterval(() => {
          setSeconds(prev => prev + 1);
        }, 1000);

        // Cleanup function using the stored ref
        return () => {
          if (intervalRef.current) {
            clearInterval(intervalRef.current);
          }
        };
      }, []);

      // ... render seconds and stop button ...
    }
    ```
*   **Key Points:**
    *   Mutating `ref.current` **does not** cause a re-render.
    *   Changes to `ref.current` are synchronous.
    *   Use refs for imperative actions or persistent mutable values outside React's state system.
    *   Avoid overusing refs for things achievable declaratively with state/props.
    *   Access DOM nodes via `ref.current` inside `useEffect` (or event handlers), not during render.

## 2. `forwardRef(renderFn)`

*   **Purpose:** Lets a component expose a DOM node *within it* to its parent component using `ref`. Necessary when a parent needs direct access to a child's DOM node.
*   **Syntax:** Wrap your component definition in `React.forwardRef`. The component function receives `props` as the first argument and `ref` as the second argument. Forward the `ref` to the desired DOM node inside the component.

```jsx
import React, { useRef, forwardRef } from 'react';

// Child component that forwards the ref to its input element
// Use generic types for ref element and props
const FancyInput = forwardRef<HTMLInputElement, { label: string }>(
  ({ label, ...props }, ref) => { // Receive ref as second argument
    return (
      <div>
        <label>{label}</label>
        {/* Forward the ref to the actual input DOM node */}
        <input ref={ref} {...props} />
      </div>
    );
  }
);
FancyInput.displayName = 'FancyInput'; // For DevTools

// Parent component that uses the ref
function ParentForm() {
  const inputRef = useRef<HTMLInputElement>(null);

  const handleFocus = () => {
    inputRef.current?.focus();
  };

  return (
    <div>
      {/* Pass the ref to the child component */}
      <FancyInput ref={inputRef} label="My Input:" placeholder="Enter text" />
      <button onClick={handleFocus}>Focus Child Input</button>
    </div>
  );
}
```

## 3. `useImperativeHandle(ref, createHandle, dependencies?)`

*   **Purpose:** Customizes the instance value that is exposed when using `ref` with `forwardRef`. Instead of exposing the entire DOM node, you can expose a specific object with imperative functions (e.g., `{ focus: () => ..., clear: () => ... }`).
*   **Usage:** Use inside a component wrapped with `forwardRef`.

```jsx
import React, { useRef, forwardRef, useImperativeHandle } from 'react';

// Define the shape of the exposed handle
interface FancyInputHandle {
  focusInput: () => void;
  clearInput: () => void;
}

const FancyInputWithMethods = forwardRef<FancyInputHandle, { label: string }>(
  (props, ref) => {
    const internalInputRef = useRef<HTMLInputElement>(null);

    // Expose only specific methods to the parent via the ref
    useImperativeHandle(ref, () => ({
      focusInput: () => {
        internalInputRef.current?.focus();
      },
      clearInput: () => {
        if (internalInputRef.current) {
          internalInputRef.current.value = '';
        }
      }
    }), []); // Dependencies if methods rely on props/state

    return (
      <div>
        <label>{props.label}</label>
        <input ref={internalInputRef} {...props} />
      </div>
    );
  }
);
FancyInputWithMethods.displayName = 'FancyInputWithMethods';

// Parent usage
function ParentUsingImperativeHandle() {
  const fancyInputRef = useRef<FancyInputHandle>(null);

  const handleFocus = () => {
    fancyInputRef.current?.focusInput(); // Call the exposed method
  };
  const handleClear = () => {
    fancyInputRef.current?.clearInput(); // Call the exposed method
  };

  return (
    <div>
      <FancyInputWithMethods ref={fancyInputRef} label="Input:" />
      <button onClick={handleFocus}>Focus Child</button>
      <button onClick={handleClear}>Clear Child</button>
    </div>
  );
}
```

*(Refer to the official React documentation for `useRef`, `forwardRef`, and `useImperativeHandle`: https://react.dev/reference/react)*