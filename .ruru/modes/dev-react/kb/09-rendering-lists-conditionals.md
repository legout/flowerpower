# Conditional Rendering & Lists

Displaying UI elements conditionally and rendering dynamic lists of components.

## 1. Conditional Rendering

React allows you to render different JSX based on conditions using standard JavaScript syntax within your components.

**Common Techniques:**

*   **`if`/`else` Statements:** Use standard `if` statements outside the JSX return block to determine which component or JSX structure to render.

    ```jsx
    function Greeting({ isLoggedIn }) {
      if (isLoggedIn) {
        return <h1>Welcome back!</h1>;
      } else {
        return <h1>Please sign up.</h1>;
      }
    }
    ```

*   **Ternary Operator (`condition ? exprIfTrue : exprIfFalse`):** Embed conditional logic directly within JSX. Useful for simple inline conditions.

    ```jsx
    function LoginButton({ isLoggedIn, onLogin, onLogout }) {
      return (
        isLoggedIn
          ? <button onClick={onLogout}>Logout</button>
          : <button onClick={onLogin}>Login</button>
      );
    }
    ```

*   **Logical `&&` Operator (`condition && expression`):** Renders the `expression` only if the `condition` is truthy. If the condition is falsy, it renders nothing (`null`). Useful for optionally rendering an element.

    ```jsx
    function Mailbox({ unreadMessages }) {
      const count = unreadMessages.length;
      return (
        <div>
          <h1>Hello!</h1>
          {/* Only render if there are unread messages */}
          {count > 0 &&
            <h2>
              You have {count} unread messages.
            </h2>
          }
        </div>
      );
    }
    ```
    *Caution: Avoid using `0` as the condition, as React will render `0`. Use `count > 0 && ...` instead of `count && ...`.*

*   **Returning `null`:** A component can return `null` to render nothing.

    ```jsx
    function WarningBanner({ showWarning }) {
      if (!showWarning) {
        return null; // Render nothing if showWarning is false
      }
      return <div className="warning">Warning!</div>;
    }
    ```

Choose the method that makes your code most readable for the specific condition.

## 2. Rendering Lists

Use JavaScript's `.map()` array method to transform an array of data into an array of React elements.

**Key Requirement: The `key` Prop**

*   When rendering a list of elements using `.map()`, React needs a way to identify each specific item across re-renders to efficiently update the DOM (adding, removing, or reordering items).
*   You **must** provide a unique and stable `key` prop to the top-level element returned within the `.map()` callback.
*   **Keys should be:**
    *   **Unique:** Among siblings in the list.
    *   **Stable:** Should not change between renders for the same logical item.
*   **Best Practice:** Use unique IDs from your data (e.g., `item.id`) as keys. This is the most reliable approach.
    ```jsx
    users.map(user => <UserComponent key={user.id} user={user} />)
    ```
*   **Avoid Using Index:** Using the array index (`(item, index) => <li key={index}>`) is generally **strongly discouraged** if the list order can change, items can be added/removed from the middle, or the list is filtered. This can lead to performance issues and bugs with component state (state might be associated with the wrong item after reordering). Use index only as a last resort if the list is static and items have no stable IDs.

**Example:**

```jsx
import React from 'react';

function TodoItem({ todo }) {
  return <li>{todo.text}</li>;
}

function TodoList({ todos }) {
  // todos is an array like: [{ id: 1, text: 'Learn React' }, { id: 2, text: 'Build App' }]

  if (!todos || todos.length === 0) {
    return <p>No tasks today!</p>; // Conditional rendering for empty list
  }

  // Use .map() to create an array of elements
  const listItems = todos.map((todo) =>
    // Assign a unique and stable key from the data (todo.id)
    <TodoItem key={todo.id} todo={todo} />
    // Or directly: <li key={todo.id}>{todo.text}</li>
  );

  return (
    <div>
      <h2>Todo List</h2>
      <ul>
        {listItems} {/* Render the array of elements */}
      </ul>
    </div>
  );
}

export default TodoList;
```

Mastering conditional rendering and list rendering with unique keys is essential for building dynamic React interfaces.

*(Refer to the official React documentation on Conditional Rendering: https://react.dev/learn/conditional-rendering and Lists and Keys: https://react.dev/learn/rendering-lists)*