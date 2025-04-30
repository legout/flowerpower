# Hook: `useReducer`

Managing complex component state logic with the `useReducer` hook.

## Core Concept: `useReducer` vs `useState`

`useReducer` is an alternative to `useState` for managing component state. It's generally preferred when:

*   You have complex state logic involving multiple sub-values.
*   The next state depends frequently on the previous one.
*   Updating state logic becomes difficult to manage within event handlers using `useState`.

It borrows concepts from Redux (but is built into React) by centralizing state update logic into a **reducer function**.

**Key Parts:**

1.  **Reducer Function:** `(state, action) => newState`
    *   A pure function that takes the current `state` and an `action` object as arguments.
    *   It determines how the state should change based on the `action.type` and returns the **new state**.
    *   **Must be pure:** Should not mutate the existing `state` object directly; always return a new state object/value. Should not perform side effects (like API calls).
2.  **`useReducer(reducer, initialArg, [init])` Hook:**
    *   Called within your functional component.
    *   `reducer`: Your reducer function defined above.
    *   `initialArg`: The initial state value, or an argument passed to the `init` function.
    *   `init` (Optional): An initializer function to compute the initial state lazily. `init(initialArg)` is called to get the initial state.
    *   **Returns:** An array with two elements:
        *   `state`: The current state value for this render.
        *   `dispatch`: A function used to send ("dispatch") actions to the reducer function. Calling `dispatch(action)` triggers a re-render if the reducer returns a new state.
3.  **Action Object:** A plain JavaScript object describing the state change. Conventionally has a `type` property (string) and optionally a `payload` property with data needed for the update. Example: `{ type: 'INCREMENT', payload: 1 }`, `{ type: 'SET_NAME', payload: 'Alice' }`.

## Implementation Steps

**1. Define Initial State, Action Types, & Reducer:**

```typescript
// Define the shape of the state
interface CounterState {
  count: number;
  step: number;
}

// Define the possible actions using a discriminated union
type CounterAction =
  | { type: 'INCREMENT' }
  | { type: 'DECREMENT' }
  | { type: 'SET_STEP'; payload: number }
  | { type: 'RESET' };

// Initial state value
const initialState: CounterState = { count: 0, step: 1 };

// Reducer function: takes current state and action, returns new state
function counterReducer(state: CounterState, action: CounterAction): CounterState {
  console.log('Reducer called with state:', state, 'and action:', action);
  switch (action.type) {
    case 'INCREMENT':
      // Return NEW state object
      return { ...state, count: state.count + state.step };
    case 'DECREMENT':
      return { ...state, count: state.count - state.step };
    case 'SET_STEP':
      // Ensure payload is a valid number
      const newStep = Number(action.payload) || 1;
      return { ...state, step: newStep };
    case 'RESET':
      return initialState; // Return the initial state object
    default:
      // Optional: Handle exhaustive check for action types
      // const _exhaustiveCheck: never = action;
      // return _exhaustiveCheck;
      // Or simply return state for unhandled actions
      console.warn('Unhandled action type');
      return state;
  }
}
```

**2. Use `useReducer` in Component:**

```jsx
import React, { useReducer } from 'react';
// Import state, action types, reducer, and initial state from where they are defined

function CounterWithReducer() {
  // Initialize the reducer hook
  const [state, dispatch] = useReducer(counterReducer, initialState);

  // Event handlers dispatch actions
  const handleIncrement = () => {
    dispatch({ type: 'INCREMENT' });
  };

  const handleDecrement = () => {
    dispatch({ type: 'DECREMENT' });
  };

  const handleStepChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    dispatch({ type: 'SET_STEP', payload: Number(event.target.value) });
  };

  const handleReset = () => {
    dispatch({ type: 'RESET' });
  };

  return (
    <div>
      <h2>Counter (useReducer)</h2>
      <p>Count: {state.count}</p>
      <div>
        <label>
          Step:
          <input
            type="number"
            value={state.step}
            onChange={handleStepChange}
            style={{ marginLeft: '8px', width: '60px' }}
          />
        </label>
      </div>
      <button onClick={handleIncrement}>Increment by {state.step}</button>
      <button onClick={handleDecrement}>Decrement by {state.step}</button>
      <button onClick={handleReset}>Reset</button>
    </div>
  );
}

export default CounterWithReducer;
```

## Benefits

*   **Centralized Logic:** State update logic is contained within the reducer, making components cleaner and logic easier to test independently.
*   **Predictability:** Given the same state and action, the reducer always produces the same new state.
*   **Easier Complex Updates:** Managing transitions between multiple related state values becomes more structured.
*   **Performance:** Can optimize dispatches in some cases (React might bail out of re-renders if the reducer returns the exact same state object). Passing `dispatch` down to child components is often more performant than passing multiple individual callback setters from `useState`.

While `useState` is sufficient for simple state, `useReducer` provides a more scalable and maintainable pattern for managing complex state logic within React components.

*(Refer to the official React documentation on `useReducer`: https://react.dev/reference/react/useReducer)*