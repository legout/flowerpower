# Testing with React Testing Library (RTL)

Writing tests for React components focused on user behavior using React Testing Library.

## Core Concept: Testing User Behavior

React Testing Library (RTL) encourages writing tests that resemble how users interact with your application, rather than focusing on internal implementation details. This leads to more resilient tests that don't break easily during refactoring.

**Guiding Principles:**

*   **Query by Accessibility:** Find elements the way users would (by visible text, label, role, etc.). Avoid querying by implementation details like CSS classes or test IDs unless necessary.
*   **Interact like a User:** Simulate user events (clicks, typing) using the `@testing-library/user-event` library (preferred over `fireEvent`).
*   **Observe the Result:** Assert based on what the user would see or experience (e.g., text appearing/disappearing, elements becoming enabled/disabled).
*   **Accessible Queries:** RTL's preferred queries (`getByRole`, `getByLabelText`, `getByText`, etc.) inherently push you towards writing more accessible components.

**Common Setup:** Often used with a test runner like Jest and `jest-dom` for helpful DOM assertions (`toBeInTheDocument`, `toHaveValue`, etc.). Frameworks like Create React App, Next.js, and Vite often include this setup.

## Key RTL APIs (`@testing-library/react`)

*   **`render(ui)`:** Renders a React element (`ui`) into a container attached to `document.body`. Returns an object with query functions and utilities.
*   **Query Functions:** Used to find elements. Throw errors if elements aren't found as expected (except `queryBy*`).
    *   **`getBy*`:** Finds 1 element. Throws if 0 or >1 found.
    *   **`queryBy*`:** Finds 1 element. Returns `null` if 0 found. Throws if >1 found. (Use to assert absence).
    *   **`findBy*`:** Finds 1 element. Returns a **Promise** resolving when element appears (waits for async changes). Rejects if timeout.
    *   **`getAllBy*`:** Finds 1+ elements. Throws if 0 found.
    *   **`queryAllBy*`:** Finds 0+ elements. Returns `[]` if 0 found.
    *   **`findAllBy*`:** Finds 1+ elements. Returns a **Promise** resolving when at least 1 appears. Rejects if timeout.
*   **Query Priorities (Recommended Order):**
    1.  `*ByRole`: Most accessible (e.g., `getByRole('button', { name: /submit/i })`).
    2.  `*ByLabelText`: For form fields associated with a `<label>`.
    3.  `*ByPlaceholderText`: For inputs with placeholder text.
    4.  `*ByText`: Finds elements by their text content.
    5.  `*ByDisplayValue`: Finds form elements by their current value.
    6.  `*ByAltText`: For images (`<img alt="..." />`).
    7.  `*ByTitle`: For elements with a `title` attribute.
    8.  `*ByTestId`: **Last resort.** Use `data-testid="my-id"` attribute if you cannot query accessibly.
*   **`screen` Object:** A convenient object pre-bound with all query functions applied to `document.body`. Preferred over destructuring from `render`. `import { screen } from '@testing-library/react';`
*   **`waitFor(callback, [options])`:** Waits for assertions within the callback to pass (useful for async updates after interactions).
*   **`within(element)`:** Scopes query functions to search only within a specific parent element.

## User Interactions (`@testing-library/user-event`)

*   **Purpose:** Simulates user interactions more realistically than RTL's built-in `fireEvent`. **Recommended** for triggering events.
*   **Import:** `import userEvent from '@testing-library/user-event';`
*   **Setup (v14+):** `const user = userEvent.setup();` before interactions.
*   **API:** Provides async methods like `user.click(element)`, `user.type(element, text)`, `user.keyboard(text)`, `user.selectOptions(element, value)`, etc. Remember to `await` these calls.

## Example Test (using Jest & RTL)

```typescript
// src/components/Counter.test.tsx
import React from 'react';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom'; // For matchers like toBeInTheDocument

import Counter from './Counter'; // The component to test

describe('Counter Component', () => {
  test('renders initial count and increments on click', async () => {
    // Arrange
    render(<Counter />);
    const user = userEvent.setup();

    // Act & Assert: Initial state
    const countElement = screen.getByText(/Count: 0/i);
    expect(countElement).toBeInTheDocument();

    const incrementButton = screen.getByRole('button', { name: /increment/i });
    expect(incrementButton).toBeInTheDocument();

    // Act: Simulate click
    await user.click(incrementButton);

    // Assert: Updated state
    expect(screen.getByText(/Count: 1/i)).toBeInTheDocument();
    expect(screen.queryByText(/Count: 0/i)).not.toBeInTheDocument();

    // Act: Click again
    await user.click(incrementButton);
    expect(screen.getByText(/Count: 2/i)).toBeInTheDocument();
  });

  test('reset button sets count back to 0', async () => {
    render(<Counter initialCount={5} />); // Test with initial prop
    const user = userEvent.setup();

    expect(screen.getByText(/Count: 5/i)).toBeInTheDocument();

    const resetButton = screen.getByRole('button', { name: /reset/i });
    await user.click(resetButton);

    expect(screen.getByText(/Count: 0/i)).toBeInTheDocument();
    expect(screen.queryByText(/Count: 5/i)).not.toBeInTheDocument();
  });
});
```

Writing tests with RTL focuses on ensuring components work as users expect, leading to more confidence and less brittle tests. Prioritize accessible queries and simulate user interactions with `user-event`.

*(Refer to the official React Testing Library: https://testing-library.com/docs/react-testing-library/intro/ and user-event: https://testing-library.com/docs/user-event/intro documentation.)*