+++
# --- Basic Metadata (Auto-Generated) ---
id = "kb-dev-react-core-concepts"
title = "KB: Core React Concepts for React Specialist"
context_type = "knowledge_base"
scope = "Fundamental React principles relevant to the dev-react mode"
target_audience = ["dev-react"]
granularity = "concepts"
status = "active"
last_updated = "2025-04-19" # << GENERATED DATE >>
# version = "1.0"
tags = ["react", "core", "concepts", "components", "hooks", "jsx", "props", "state"]
# relevance = "High relevance for foundational understanding"
# related_context = []
# --- Mode-Specific Details ---
target_mode_slug = "dev-react"
+++

# Core React Concepts

This document outlines fundamental React concepts essential for the `dev-react` (React Specialist) mode.

## 1. Components

React applications are built using reusable pieces of UI called components. The `dev-react` mode primarily focuses on **Functional Components**.

*   **Functional Components:** Simple JavaScript functions that accept `props` (properties) as an argument and return React elements describing what should appear on the screen. They are the standard for modern React development.

    ```jsx
    function Welcome(props) {
      return <h1>Hello, {props.name}</h1>;
    }
    ```

## 2. JSX (JavaScript XML)

JSX is a syntax extension for JavaScript that looks similar to XML or HTML. It allows you to write UI structures declaratively within your JavaScript code. Babel compiles JSX down to `React.createElement()` calls.

*   **Embedding Expressions:** Use curly braces `{}` to embed JavaScript expressions within JSX.
*   **Attributes:** Use HTML-like attributes (e.g., `className` instead of `class`, `htmlFor` instead of `for`).

    ```jsx
    const name = 'Roo';
    const element = <h1 className="greeting">Hello, {name}</h1>;
    ```

## 3. Props (Properties)

Props are read-only arguments passed into components, similar to function arguments. They allow components to be configured and customized from their parent components.

*   **Passing Props:** Pass data from parent to child components via attributes in JSX.
*   **Read-Only:** Components should never modify their own props directly.

    ```jsx
    // Parent
    function App() {
      return <Welcome name="React Specialist" />;
    }

    // Child (Welcome component from above)
    // Accesses props.name
    ```

## 4. State

State allows React components to "remember" information and change their output over time in response to user actions, network responses, etc.

*   **`useState` Hook:** The primary way to add state to functional components. It returns a pair: the current state value and a function to update it.

    ```jsx
    import React, { useState } from 'react';

    function Counter() {
      // Declare a state variable 'count' initialized to 0
      const [count, setCount] = useState(0);

      return (
        <div>
          <p>You clicked {count} times</p>
          {/* Call setCount to update the state */}
          <button onClick={() => setCount(count + 1)}>
            Click me
          </button>
        </div>
      );
    }
    ```

## 5. Hooks

Hooks are functions that let you "hook into" React state and lifecycle features from functional components.

*   **`useState`:** (See above) Manages local component state.
*   **`useEffect`:** Lets you perform side effects in functional components (e.g., data fetching, subscriptions, manually changing the DOM). It runs after every render by default, but can be configured to run only when specific dependencies change.

    ```jsx
    import React, { useState, useEffect } from 'react';

    function ExampleComponent({ userId }) {
      const [userData, setUserData] = useState(null);

      useEffect(() => {
        // Fetch data when userId changes
        fetch(`/api/users/${userId}`)
          .then(response => response.json())
          .then(data => setUserData(data));

        // Optional cleanup function
        return () => {
          // Cleanup logic (e.g., cancel subscriptions)
        };
      }, [userId]); // Dependency array: effect runs only if userId changes

      // ... render component using userData ...
    }
    ```

These core concepts form the foundation for building applications with React using the modern functional component and hooks paradigm favored by the `dev-react` mode.