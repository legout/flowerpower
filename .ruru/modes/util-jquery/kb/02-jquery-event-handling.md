+++
# Basic KB Metadata (Optional)
# id = "jquery-event-handling"
# title = "jQuery Event Handling"
# tags = ["jquery", "events", "dom", "interaction", "delegation"]
+++

# jQuery Event Handling

This document outlines key concepts and best practices for handling DOM events using jQuery.

## 1. Attaching Event Handlers: `.on()`

The primary method for attaching event handlers is `.on()`.

```javascript
// Basic syntax
$('#myButton').on('click', function(event) {
  console.log('Button clicked!');
  // 'this' refers to the DOM element clicked
  // 'event' is the jQuery Event object
});

// Attaching multiple events
$('#myInput').on('focus blur', function(event) {
  console.log(`Input event: ${event.type}`); // Logs 'focus' or 'blur'
});

// Passing data to the handler
$('#myLink').on('click', { user: 'Admin' }, function(event) {
  console.log(`Link clicked by ${event.data.user}`);
});
```

## 2. Event Delegation

Event delegation is crucial for performance, especially with dynamic content or many elements. Attach the handler to a static parent element and filter by the target selector.

```javascript
// Less efficient: Attaches handler to each existing/future '.list-item'
// $('.list-item').on('click', function() { ... }); // Avoid if possible

// More efficient: Attaches one handler to the static parent '#myList'
$('#myList').on('click', '.list-item', function(event) {
  console.log(`Clicked item: ${$(this).text()}`);
  // 'this' refers to the '.list-item' that was clicked
});
```

**Benefits of Delegation:**
-   Fewer event handlers attached to the DOM.
-   Automatically handles events for elements added *after* the handler was attached.

## 3. The Event Object

The handler function receives a jQuery `Event` object with useful properties and methods:

-   `event.type`: The type of event (e.g., "click", "mouseover").
-   `event.target`: The original DOM element that triggered the event.
-   `event.currentTarget`: The DOM element the handler is attached to (useful in delegation).
-   `event.preventDefault()`: Prevents the browser's default action (e.g., following a link, submitting a form).
-   `event.stopPropagation()`: Stops the event from bubbling up the DOM tree to parent handlers.
-   `event.data`: Any data passed when attaching the handler using `.on()`.
-   `event.pageX`, `event.pageY`: Mouse coordinates relative to the page.
-   `event.which`: Key code for keyboard events.

## 4. Removing Event Handlers: `.off()`

Remove handlers previously attached with `.on()`.

```javascript
// Remove a specific handler
const myClickHandler = function() { console.log('Clicked!'); };
$('#myButton').on('click', myClickHandler);
// ... later ...
$('#myButton').off('click', myClickHandler);

// Remove all 'click' handlers from the button
$('#myButton').off('click');

// Remove all handlers from the button
$('#myButton').off();

// Remove delegated handlers
$('#myList').off('click', '.list-item');
```

## 5. Shorthand Methods

jQuery provides shorthand methods for common events (e.g., `.click()`, `.hover()`, `.submit()`). While convenient, `.on()` is generally preferred for consistency and its ability to handle delegation.

```javascript
// Shorthand
$('#myButton').click(function() { /* ... */ });

// Equivalent using .on()
$('#myButton').on('click', function() { /* ... */ });