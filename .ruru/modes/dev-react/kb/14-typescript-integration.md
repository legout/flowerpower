# TypeScript Integration

Leveraging TypeScript for type safety in React applications.

## Core Concept: Type Safety in React

TypeScript adds static typing to JavaScript, catching potential errors during development. When used with React, it helps define the expected shapes of props, state, event handlers, and refs, improving code reliability, maintainability, and developer experience (autocompletion, refactoring).

**Key Benefits:**

*   **Error Prevention:** Catches type mismatches, undefined properties, incorrect argument types, etc., before runtime.
*   **Improved Readability:** Explicit types make component APIs (props) clearer.
*   **Enhanced Refactoring:** Type checking helps ensure changes don't break other parts.
*   **Better Autocompletion:** IDEs provide more accurate suggestions.

## Setting Up

Most modern React frameworks/tools offer TypeScript templates:

*   **Create React App:** `npx create-react-app my-app --template typescript`
*   **Next.js:** Supported out-of-the-box (`.ts`/`.tsx` files). Install types: `npm install --save-dev @types/react @types/node`
*   **Vite:** `npm create vite@latest my-app -- --template react-ts`
*   **Manual:** Install `typescript`, `@types/react`, `@types/react-dom` and configure `tsconfig.json` (set `"jsx": "react-jsx"` or similar).

## Typing Common React Patterns

**1. Functional Components & Props:**

*   Define an `interface` or `type` alias for props.
*   Type the props argument directly (preferred) or use `React.FC<PropsType>`.

```typescript
import React from 'react';

// Define prop types
interface GreetingProps {
  name: string;
  messageCount?: number; // Optional
  children?: React.ReactNode; // Type for children
}

// Type props argument directly (preferred)
const Greeting = ({ name, messageCount = 0, children }: GreetingProps) => {
  return (
    <div>
      <h1>Hello, {name}!</h1>
      {messageCount > 0 && <p>You have {messageCount} messages.</p>}
      {children}
    </div>
  );
};

export default Greeting;
```

**2. `useState` Hook:**

*   Type is often inferred from the initial value.
*   Provide an explicit type argument (`useState<Type>`) if the initial value is `null`/`undefined` or ambiguous.

```typescript
import React, { useState } from 'react';

interface User { id: number; name: string; }

function UserProfile() {
  // Type inferred as number
  const [count, setCount] = useState(0);

  // Explicit type needed if initial value is null or could be User
  const [user, setUser] = useState<User | null>(null);

  const loadUser = () => { setUser({ id: 1, name: 'Alice' }); };

  return (
    <div>
      {/* ... */}
      {user ? <p>User: {user.name}</p> : <p>No user loaded.</p>}
      <button onClick={loadUser}>Load User</button>
    </div>
  );
}
```

**3. `useReducer` Hook:**

*   Define types/interfaces for the `state` and `action` objects. Use discriminated unions for actions.

```typescript
import React, { useReducer } from 'react';

interface CounterState { count: number; step: number; }
type CounterAction =
  | { type: 'INCREMENT' } | { type: 'DECREMENT' }
  | { type: 'SET_STEP'; payload: number } | { type: 'RESET' };

const initialState: CounterState = { count: 0, step: 1 };

function counterReducer(state: CounterState, action: CounterAction): CounterState {
  // ... reducer logic based on action.type ...
  return state; // Placeholder
}

function TypedReducerCounter() {
  const [state, dispatch] = useReducer(counterReducer, initialState);
  // ... component logic ...
  return <div>Count: {state.count}</div>;
}
```

**4. `useRef` Hook:**

*   Provide a type argument for the expected ref value (e.g., `HTMLInputElement`).
*   Initialize DOM refs with `null`.

```typescript
import React, { useRef, useEffect } from 'react';

function TypedFocusInput() {
  // Type the ref for an HTMLInputElement, initialize with null
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  return <input ref={inputRef} type="text" />;
}
```

**5. Event Handling:**

*   TypeScript often infers event types (`e`) based on the handler (e.g., `onClick` gets `React.MouseEvent`).
*   Provide explicit types if needed (e.g., `React.ChangeEvent<HTMLInputElement>`).

```typescript
import React, { useState } from 'react';

function TypedForm() {
  const [value, setValue] = useState('');

  // Explicitly type the event for input onChange
  const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setValue(event.target.value);
  };

  // Type often inferred correctly for form onSubmit
  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    console.log('Submitted:', value);
  };

  return (
    <form onSubmit={handleSubmit}>
      <input type="text" value={value} onChange={handleChange} />
      <button type="submit">Submit</button>
    </form>
  );
}
```

**Utility Types:** React (`@types/react`) provides useful utility types: `React.ReactNode` (anything renderable), `React.ReactElement`, `React.ComponentPropsWithoutRef`, `React.CSSProperties`, etc.

Using TypeScript with React enhances development by adding static type checking, making code more robust and easier to manage, especially in larger projects.

*(Refer to the React TypeScript Cheatsheet: https://react-typescript-cheatsheet.netlify.app/ and the official React documentation on TypeScript: https://react.dev/learn/typescript)*