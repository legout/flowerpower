# Event Handling

Responding to user interactions like clicks, input changes, and form submissions in React.

## Core Concept: Synthetic Events

React normalizes the browser's native event system into a cross-browser compatible wrapper called the **SyntheticEvent**. When you attach event handlers in JSX, you receive an instance of this synthetic event.

**Key Differences from DOM Events:**

*   **CamelCase Naming:** Event names are camelCased (e.g., `onClick`, `onChange`, `onSubmit`) instead of lowercase (`onclick`, `onchange`).
*   **Function Values:** You pass a function reference as the event handler, not a string (`onClick={handleClick}` instead of `onclick="handleClick()"`).
*   **Preventing Default:** Call `event.preventDefault()` explicitly within your handler to stop the default browser action (e.g., stopping form submission page reload). Returning `false` does *not* work like in traditional HTML event attributes.

## Attaching Event Handlers

Pass the handler function directly to the appropriate prop on the JSX element.

```jsx
import React, { useState } from 'react';

function EventDemo() {
  const [inputValue, setInputValue] = useState('');

  // Define handler functions
  const handleClick = (event: React.MouseEvent<HTMLButtonElement>) => {
    // 'event' is the SyntheticEvent
    console.log('Button clicked!', event.target); // event.target is the DOM node
    alert('Clicked!');
  };

  const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    console.log('Input changed:', event.target.value);
    setInputValue(event.target.value); // Update state based on input value
  };

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault(); // Prevent default form submission (page reload)
    console.log('Form submitted with value:', inputValue);
    alert(`Submitting: ${inputValue}`);
    // Perform actions like sending data to an API
  };

  return (
    <form onSubmit={handleSubmit}> {/* Attach handler to form */}
      <label htmlFor="myInput">Input:</label>
      <input
        type="text"
        id="myInput"
        value={inputValue}
        onChange={handleChange} {/* Attach handler to input */}
      />

      {/* Attach handler directly inline (less common for complex logic) */}
      <button type="button" onClick={() => alert('Inline handler clicked!')}>
        Inline Alert
      </button>

      {/* Attach handler via function reference */}
      <button type="button" onClick={handleClick}>
        Click Me
      </button>

      <button type="submit">Submit</button>
    </form>
  );
}

export default EventDemo;
```

## The `event` Object (SyntheticEvent)

The event handler function receives a `SyntheticEvent` object. Key properties:

*   `event.target`: The DOM element that triggered the event (e.g., the specific button clicked).
*   `event.currentTarget`: The DOM element the event listener is attached to (useful in event delegation scenarios, though less common with direct React handlers).
*   `event.preventDefault()`: Stops the browser's default action.
*   `event.stopPropagation()`: Stops the event from bubbling up to parent elements.
*   `event.type`: String representing the event type (e.g., `'click'`).
*   `event.nativeEvent`: Access to the underlying browser native event object if needed.
*   Specific event properties (e.g., `event.key`, `event.keyCode` for keyboard events; `event.clientX`, `event.clientY` for mouse events; `event.target.value` for input/change events).

## Passing Arguments to Handlers

If you need to pass extra arguments (like an item ID) to an event handler:

1.  **Inline Arrow Function:** Wrap the handler call in an inline arrow function. This is the most common approach.
    ```jsx
    <button onClick={() => handleDelete(itemId)}>Delete Item {itemId}</button>
    ```
2.  **`.bind()` (Less Common):** Use `Function.prototype.bind`.
    ```jsx
    <button onClick={handleDelete.bind(this, itemId)}>Delete Item {itemId}</button>
    ```

React's event handling system provides a consistent and cross-browser way to respond to user interactions using familiar JavaScript functions and event objects. Remember to use camelCase props and call `event.preventDefault()` explicitly when needed.

*(Refer to the official React documentation on Handling Events: https://react.dev/learn/responding-to-events)*