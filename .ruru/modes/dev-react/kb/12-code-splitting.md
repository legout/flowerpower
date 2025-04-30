# Code Splitting (`React.lazy`, `Suspense`)

Improving initial load performance by splitting code into smaller chunks and loading them on demand.

## Core Concept: Code Splitting

By default, build tools bundle all application JavaScript into one large file. **Code Splitting** breaks this bundle into smaller chunks loaded dynamically, improving initial load time. React supports this via dynamic `import()` with `React.lazy` and `React.Suspense`.

**Benefits:**

*   **Faster Initial Load:** Reduces the initial JavaScript bundle size.
*   **Improved Performance:** Less JavaScript to parse and execute upfront.
*   **On-Demand Loading:** Load code for features/routes only when needed.

## Implementation

**1. Dynamic `import()`:**
*   Use `import('./MyComponent')` instead of `import MyComponent from './MyComponent'`.
*   Tells the bundler (Webpack, Vite) to create a separate chunk.
*   Returns a **Promise** resolving to the module (usually with a `default` export).

**2. `React.lazy(loadFn)`:**
*   A function that renders a dynamically imported component.
*   Takes a function `loadFn` that **must** call a dynamic `import()`. The imported module **must** have a `default` export containing the React component.
*   Returns a special component that loads the chunk on first render.

**3. `<Suspense fallback={...}>`:**
*   Specifies a **loading indicator** (the `fallback` prop, e.g., `<LoadingSpinner />`) shown while lazy components load.
*   Wrap `React.lazy` components with `<Suspense>`. Multiple lazy components can share one boundary.

## Example

```jsx
import React, { Suspense, useState, lazy } from 'react';

// Static imports
import LoadingSpinner from './LoadingSpinner';
import Header from './Header';

// --- Dynamic Import using React.lazy ---
const AdminPanel = lazy(() => import('./components/AdminPanel'));
const UserProfile = lazy(() => import('./components/UserProfile'));

function App() {
  const [showAdmin, setShowAdmin] = useState(false);
  const [showProfile, setShowProfile] = useState(false);

  return (
    <div>
      <Header />
      <h1>Code Splitting Demo</h1>

      <button onClick={() => setShowAdmin(prev => !prev)}>Toggle Admin Panel</button>
      <button onClick={() => setShowProfile(prev => !prev)}>Toggle User Profile</button>

      <hr />

      {/* --- Use Suspense for fallback UI --- */}
      <Suspense fallback={<LoadingSpinner />}>
        {/* AdminPanel code loaded only when showAdmin is true */}
        {showAdmin && <AdminPanel />}
      </Suspense>

      <hr />

      <Suspense fallback={<p>Loading profile...</p>}>
        {/* UserProfile code loaded only when showProfile is true */}
        {showProfile && <UserProfile userId={123} />}
      </Suspense>
    </div>
  );
}

export default App;

// --- Example components (in separate files) ---
// components/AdminPanel.tsx
// export default function AdminPanel() { return <div>Admin Section</div>; }
// components/UserProfile.tsx
// export default function UserProfile({ userId }) { return <div>Profile for User {userId}</div>; }
// components/LoadingSpinner.tsx
// export default function LoadingSpinner() { return <div>Loading...</div>; }
```

## Route-Based Code Splitting

Applying code splitting at the route level is highly effective. Frameworks often handle this automatically:

*   **Next.js (App Router):** Automatic based on `page.tsx`. `loading.tsx` integrates with `Suspense`.
*   **Next.js (Pages Router):** Use `next/dynamic`.
*   **React Router:** Use `React.lazy` and `Suspense` in route configuration.

```jsx
// Example with React Router v6
import React, { Suspense, lazy } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';

const HomePage = lazy(() => import('./routes/Home'));
const AboutPage = lazy(() => import('./routes/About'));

function App() {
  return (
    <Router>
      <nav>...</nav>
      <Suspense fallback={<div>Loading page...</div>}>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/about" element={<AboutPage />} />
        </Routes>
      </Suspense>
    </Router>
  );
}
```

## Considerations

*   **Loading States:** Provide meaningful `fallback` UIs in `Suspense`.
*   **Error Handling:** Wrap `Suspense` boundaries with React Error Boundaries (`11-error-boundaries.md`) to catch potential dynamic import errors.
*   **SSR:** Works with Server-Side Rendering frameworks.

*(Refer to the official React documentation on Code Splitting: https://react.dev/reference/react/lazy)*