+++
id = "jquery-dom-manipulation-events"
title = "jQuery: DOM Manipulation & Event Handling"
tags = ["jquery", "dom", "events", "manipulation", "delegation"]
+++

# jQuery: DOM Manipulation & Event Handling

This document covers common DOM manipulation techniques and event handling best practices in jQuery.

## DOM Manipulation

jQuery simplifies changing the structure and content of the HTML document.

*   **Getting/Setting Content:**
    *   `.html()`: Get or set the inner HTML content.
    *   `.text()`: Get or set the text content (HTML tags are stripped/encoded).
    *   `.val()`: Get or set the value of form elements (input, select, textarea).
*   **Adding/Removing Elements:**
    *   `.append()`, `.prepend()`: Add content inside selected element(s) at the end/beginning.
    *   `.after()`, `.before()`: Add content after/before selected element(s).
    *   `.remove()`: Remove selected element(s) from the DOM.
    *   `.empty()`: Remove all child nodes from selected element(s).
*   **Attributes & Properties:**
    *   `.attr()`: Get or set HTML attributes.
    *   `.prop()`: Get or set DOM properties (preferred for boolean attributes like `checked`, `disabled`).
    *   `.addClass()`, `.removeClass()`, `.toggleClass()`: Manage CSS classes.
*   **CSS:**
    *   `.css()`: Get or set CSS properties.

```javascript
// Example: Update content and add a class
const $container = $('#data-container');
$container.html('<p>New content loaded!</p>');
$container.addClass('loaded');

// Example: Append a new list item
$('#item-list').append('<li>New Item</li>');
```

## Event Handling

jQuery provides a robust way to handle user interactions.

*   **Binding Events:** Use `.on()` for attaching event handlers. It's the recommended method.
    ```javascript
    $('#myButton').on('click', function(event) {
      console.log('Button clicked!');
      // 'this' refers to the button element
      $(this).prop('disabled', true);
      // 'event' object contains event details
      event.preventDefault(); // Prevent default action (e.g., form submission)
    });
    ```
*   **Event Delegation:** Attach a single event listener to a parent element to handle events for current *and future* child elements matching a selector. This is more efficient than attaching many individual handlers, especially for dynamic content.
    ```javascript
    // Efficient: Handles clicks on any '.list-item' inside '#item-list',
    // even if items are added later.
    $('#item-list').on('click', '.list-item', function() {
      console.log('List item clicked:', $(this).text());
    });
    ```
*   **Removing Events:** Use `.off()` to detach event handlers previously attached with `.on()`.

**Key Takeaways:** Use appropriate methods for DOM manipulation. Prefer `.on()` for event binding and leverage event delegation for performance and dynamic content.