# Error Boundaries

Catching JavaScript errors in component trees and displaying fallback UI.

## Core Concept: Error Boundaries

Error Boundaries are React components that **catch JavaScript errors** anywhere in their child component tree, log those errors, and display a **fallback UI** instead of the component tree that crashed.

**Key Features:**

*   **Catch Runtime Errors:** They catch errors during rendering, in lifecycle methods, and in constructors of the whole tree below them.
*   **Do Not Catch:**
    *   Errors inside event handlers (use regular `try...catch`).
    *   Asynchronous code (e.g., `setTimeout`, network request callbacks).
    *   Errors thrown in the error boundary component itself (error propagates upwards).
    *   Server-side rendering errors (handled differently by frameworks like Next.js via `error.tsx`).
*   **Fallback UI:** Allow you to show a user-friendly message instead of a broken UI.
*   **Logging:** Provide a place (`componentDidCatch`) to log error information to reporting services.
*   **Granularity:** Can be placed at different levels to provide specific fallbacks for different sections.

## Implementation (Class Component)

As of React 18, Error Boundaries can **only** be implemented as **class components** defining one or both of these lifecycle methods:

1.  **`static getDerivedStateFromError(error)`:**
    *   A static method called during the "render" phase after a descendant throws an error.
    *   Receives the `error` object.
    *   Should return an object to update the boundary's state (e.g., `{ hasError: true }`) to trigger rendering the fallback UI.
    *   **Do not** cause side effects here.
2.  **`componentDidCatch(error, errorInfo)`:**
    *   Called during the "commit" phase after an error is caught.
    *   Receives the `error` object and an `errorInfo` object (with `componentStack`).
    *   Use this method for **side effects** like logging the error.

```typescript
import React, { Component, ErrorInfo, ReactNode } from 'react';

interface Props {
  children?: ReactNode;
  fallback?: ReactNode; // Optional custom fallback UI prop
}

interface State {
  hasError: boolean;
  error?: Error;
}

class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
  };

  // Update state to render fallback UI
  public static getDerivedStateFromError(error: Error): State {
    console.log("getDerivedStateFromError caught:", error);
    return { hasError: true, error: error };
  }

  // Log the error
  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error("ErrorBoundary caught an error:", error, errorInfo.componentStack);
    // logErrorToReportingService(error, errorInfo.componentStack);
  }

  public render() {
    if (this.state.hasError) {
      // Render custom fallback or default
      return this.props.fallback || (
        <div>
          <h2>Something went wrong.</h2>
          <p>Please try refreshing the page.</p>
          {/* Optionally display error details during development */}
          {process.env.NODE_ENV === 'development' && this.state.error && (
            <pre style={{ whiteSpace: 'pre-wrap', fontSize: '0.8em' }}>
              {this.state.error.toString()}
              {/* componentStack is available in componentDidCatch */}
            </pre>
          )}
        </div>
      );
    }

    // Render children normally if no error
    return this.props.children;
  }
}

export default ErrorBoundary;
```

## Usage

Wrap parts of your UI that might throw rendering errors.

```jsx
import React from 'react';
import ErrorBoundary from './ErrorBoundary';
import MyWidget from './MyWidget';
import AnotherSection from './AnotherSection';

function App() {
  return (
    <div>
      <h1>My Application</h1>
      <ErrorBoundary fallback={<p>Widget failed to load.</p>}>
        <MyWidget />
      </ErrorBoundary>
      <hr />
      <ErrorBoundary> {/* Uses default fallback */}
        <AnotherSection />
      </ErrorBoundary>
    </div>
  );
}
```

**Note on Hooks:** While you cannot *create* an error boundary using only hooks, libraries like `react-error-boundary` provide hook-based APIs (`useErrorHandler`) and components (`<ErrorBoundary>`) that simplify usage within functional components, often wrapping a class-based boundary internally.

*(Refer to the official React documentation on Error Boundaries: https://react.dev/reference/react/Component#catching-rendering-errors-with-an-error-boundary)*