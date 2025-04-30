# --- Basic Metadata ---
id = "KB-COREWEB-VANILLAJS-V1"
title = "KB: Core Web Developer - Vanilla JavaScript Practices"
context_type = "best_practices"
scope = "Guidelines for writing modern, efficient Vanilla JavaScript"
target_audience = ["dev-core-web"]
granularity = "guideline"
status = "active"
last_updated = "2025-04-22"
tags = ["kb", "javascript", "vanilla-js", "es6", "dom", "events", "fetch", "async", "best-practices", "dev-core-web"]
related_context = [".ruru/modes/dev-core-web/kb/01-principles.md"]
template_schema_doc = ".ruru/templates/toml-md/08_ai_context_source.README.md"
relevance = "High: Core skill for implementing client-side interactivity"
+++

# KB: Vanilla JavaScript Practices (ES6+)

Guidelines for implementing client-side logic using modern, standard JavaScript.

## 1. Selecting DOM Elements

*   **Prefer `querySelector` & `querySelectorAll`:** Use standard DOM APIs for selecting elements.
    *   `document.querySelector(cssSelector)`: Returns the *first* element matching the CSS selector, or `null`.
    *   `document.querySelectorAll(cssSelector)`: Returns a static `NodeList` (array-like) of *all* elements matching the selector. You can iterate over it using `forEach` or convert to an array (`Array.from()`).
    *   `parentElement.querySelector(...)`: Search within a specific element.
*   **`getElementById(id)`:** Still efficient for selecting unique elements by ID.

```javascript
const mainTitle = document.getElementById('main-title');
const submitButton = document.querySelector('button.submit-btn');
const listItems = document.querySelectorAll('#user-list li');

if (submitButton) {
  submitButton.disabled = true;
}

listItems.forEach(item => {
  item.classList.add('processed');
});
```

## 2. Manipulating the DOM

*   **Content:**
    *   `element.textContent`: Get/set text content (safer).
    *   `element.innerHTML`: Get/set HTML content (**Caution:** XSS risk if setting untrusted content).
    *   `inputElement.value`: Get/set value of form inputs.
*   **Attributes:**
    *   `element.getAttribute(name)`, `element.setAttribute(name, value)`, `element.removeAttribute(name)`.
    *   `element.dataset.yourName`: Access `data-your-name` attributes.
*   **Classes:**
    *   `element.classList.add('class')`, `element.classList.remove('class')`, `element.classList.toggle('class')`, `element.classList.contains('class')`.
*   **Styles:**
    *   `element.style.property = 'value'` (e.g., `element.style.color = 'red'`, `element.style.marginLeft = '10px'`). Use camelCase for CSS properties. Less preferred than using classes for significant styling.
*   **Creating & Adding Elements:**
    *   `document.createElement('tagName')`: Create a new element.
    *   `parentElement.appendChild(newChild)`: Add element as the last child.
    *   `parentElement.insertBefore(newChild, referenceNode)`: Insert before another child.
    *   `parentElement.append(nodeOrString, ...)` / `parentElement.prepend(...)`: Modern methods to add nodes or strings.
*   **Removing Elements:**
    *   `element.remove()`: Remove the element itself.
    *   `parentElement.removeChild(childElement)`: Remove a specific child.

## 3. Handling Events

*   **`element.addEventListener(eventName, handlerFn, [options])`:** The standard method.
    *   `eventName`: Event type string (e.g., `'click'`, `'submit'`, `'input'`, `'keydown'`).
    *   `handlerFn(event)`: Callback function receiving the `Event` object.
    *   `options`: Optional object (e.g., `{ once: true, capture: false }`).
*   **`element.removeEventListener(eventName, handlerFn, [options])`:** Remove the listener. Requires a reference to the *exact same* handler function.
*   **Event Object (`event`):** Access properties like `event.target`, `event.currentTarget`, `event.key`, `event.preventDefault()`, `event.stopPropagation()`.
*   **`this` inside Handlers:** By default, `this` refers to `event.currentTarget`. Arrow functions (`=>`) do *not* rebind `this`.

```javascript
const button = document.querySelector('#myButton');
const form = document.querySelector('#myForm');

function handleButtonClick(event) {
  console.log('Button clicked!', event.target);
  this.textContent = 'Clicked!'; // 'this' is the button
}

if (button) {
  button.addEventListener('click', handleButtonClick);
}

if (form) {
  form.addEventListener('submit', (event) => { // Arrow function example
    event.preventDefault();
    console.log('Form submitted');
    // Access form via event.currentTarget or closure
    const formData = new FormData(form);
    console.log(Object.fromEntries(formData.entries()));
  });
}

// Example removing listener (needs named function)
// button.removeEventListener('click', handleButtonClick);
```
*   **Event Delegation:** Attach listeners to a common ancestor element for better performance, especially for lists or dynamic content. Check `event.target` within the handler to identify the originating element.

## 4. Asynchronous Operations (`fetch`, `async`/`await`)

*   **`fetch(url, [options])`:** Standard API for making network requests. Returns a Promise resolving to the `Response` object.
    *   Requires chaining `.then()` or using `async/await`.
    *   Call `.json()`, `.text()`, `.blob()` etc., on the `Response` object (these also return Promises).
    *   Check `response.ok` status. `fetch` doesn't reject on HTTP errors (4xx, 5xx) by default.
*   **`async/await`:** Preferred syntax for handling Promises returned by `fetch` and other async operations. Use within `async function`.

```javascript
const apiUrl = '/api/data';

async function fetchData() {
  console.log('Fetching data...');
  try {
    const response = await fetch(apiUrl); // await the fetch promise

    if (!response.ok) { // Check for HTTP errors
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json(); // await the .json() promise
    console.log('Data received:', data);
    // Update DOM with data
    document.querySelector('#output').textContent = JSON.stringify(data, null, 2);

  } catch (error) {
    console.error('Error fetching data:', error);
    document.querySelector('#output').textContent = 'Error loading data.';
  } finally {
    console.log('Fetch attempt finished.');
  }
}

// Call the async function
// fetchData();
```

## 5. Basic State Management (Conceptual)

*   For simple UI state (e.g., toggling a class, tracking input value), directly manipulate DOM attributes/classes or store values in JavaScript variables within the appropriate scope.
*   For more complex state shared across multiple components or involving intricate logic, consider simple state objects/functions or escalate to the `frontend-lead` to discuss using a dedicated state management pattern or library if appropriate for the project context (though this mode primarily sticks to vanilla JS).

Write clean, modern vanilla JS. Use standard DOM APIs for selection and manipulation. Handle events with `addEventListener`. Use `fetch` and `async/await` for asynchronous operations.