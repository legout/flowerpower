+++
# --- Basic Metadata (Auto-Generated) ---
id = "kb-dev-react-component-practices"
title = "KB: React Component Best Practices for React Specialist"
context_type = "knowledge_base"
scope = "Guidelines for writing effective React components relevant to the dev-react mode"
target_audience = ["dev-react"]
granularity = "best_practices"
status = "active"
last_updated = "2025-04-19" # << GENERATED DATE >>
# version = "1.0"
tags = ["react", "components", "best-practices", "functional-components", "hooks", "props", "state", "composition", "typescript"]
# relevance = "High relevance for code quality and maintainability"
# related_context = ["kb-dev-react-core-concepts"]
# --- Mode-Specific Details ---
target_mode_slug = "dev-react"
+++

# React Component Best Practices

This document outlines key best practices for creating React components, aligned with the capabilities of the `dev-react` (React Specialist) mode.

## 1. Favor Functional Components and Hooks

*   **Standard:** Use functional components with Hooks (`useState`, `useEffect`, `useContext`, etc.) as the default for all new components. They lead to more readable, reusable, and testable code compared to class components.
*   **Avoid Classes:** Only use class components if interacting with legacy codebases or specific libraries that require them.

## 2. Keep Components Small and Focused (Single Responsibility Principle)

*   **Goal:** Each component should ideally do one thing well.
*   **Break Down:** If a component becomes too large, handles too many concerns (e.g., fetching data, managing complex state, rendering multiple distinct UI sections), break it down into smaller, more specialized components.
*   **Benefits:** Improves readability, maintainability, reusability, and testability.

## 3. Effective Prop Handling

*   **Destructuring:** Destructure props at the beginning of the component for clarity.
*   **TypeScript:** Use TypeScript interfaces or types to define the shape of props for type safety and self-documentation.
*   **`propTypes` (JavaScript):** If not using TypeScript, use the `prop-types` library for runtime type checking during development.
*   **Default Props:** Provide default values for non-essential props.

```tsx
// TypeScript Example
interface UserProfileProps {
  userId: string;
  showAvatar?: boolean; // Optional prop
  onUpdate: (data: UserData) => void;
}

function UserProfile({ userId, showAvatar = true, onUpdate }: UserProfileProps) {
  // ... component logic ...
}
```

## 4. Strategic State Management

*   **Local State First:** Use `useState` for state that is local to a single component and doesn't need to be shared.
*   **Lift State Up:** If multiple components need access to the same state, lift it up to their closest common ancestor component and pass it down via props.
*   **Context API:** Use `useContext` for state that needs to be accessed by many components at different nesting levels (e.g., theme, user authentication) without excessive prop drilling. Use it judiciously, as overuse can make component reuse harder.
*   **`useReducer`:** Consider `useReducer` for managing complex state logic involving multiple sub-values or when the next state depends on the previous one.
*   **External Libraries:** Integrate with libraries like Redux, Zustand, or Jotai when directed for complex global state management scenarios, but prefer React's built-in solutions where appropriate.

## 5. Leverage Component Composition

*   **Children Prop:** Use the `children` prop to create generic container components (e.g., `Card`, `Modal`, `Layout`) that can render arbitrary content passed into them.
*   **Render Props:** While less common with Hooks, understand the render prop pattern for sharing code between components using a prop whose value is a function.
*   **Higher-Order Components (HOCs):** Understand HOCs for reusing component logic, but often custom Hooks provide a simpler alternative.

```jsx
// Example using children prop
function Card({ children }) {
  return <div className="card">{children}</div>;
}

// Usage
<Card>
  <h2>Card Title</h2>
  <p>Some content inside the card.</p>
</Card>
```

## 6. Immutability

*   **Never Mutate State/Props Directly:** Always use the setter function from `useState` or `useReducer` to update state. Treat props as read-only.
*   **Arrays/Objects:** When updating state based on previous arrays or objects, create new instances instead of modifying the existing ones (e.g., use spread syntax `...` or methods like `.map()`, `.filter()`). This is crucial for React's change detection mechanism.

## 7. TypeScript Integration

*   **Type Everything:** Define types/interfaces for props, state, function arguments, and return values.
*   **Utility Types:** Leverage TypeScript's utility types (e.g., `Partial`, `Required`, `Readonly`) where applicable.
*   **Event Handling:** Use React's synthetic event types (e.g., `React.ChangeEvent<HTMLInputElement>`, `React.MouseEvent<HTMLButtonElement>`).

Adhering to these practices helps the `dev-react` mode produce high-quality, maintainable, and performant React applications.