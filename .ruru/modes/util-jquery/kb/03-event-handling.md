# Event Handling

Responding to user interactions and browser events using jQuery.

## Core Method: `.on()`

The primary method for attaching event handlers in modern jQuery is `.on()`.

**Syntax:**

*   **Direct Binding:** `$(selector).on(eventName, handlerFn);`
    *   Attaches the handler directly to the selected element(s).
*   **Delegated Binding:** `$(ancestorSelector).on(eventName, childSelector, handlerFn);`
    *   Attaches the handler to the ancestor.
    *   Executes only if the event originated from a matching `childSelector` within the ancestor.
    *   **Performance Benefit:** Generally preferred for lists, tables, or containers with many interactive children, or dynamically added elements. See `06-performance.md`.

**Common Event Names (`eventName`):**

*   **Mouse:** `click`, `dblclick`, `mouseenter`, `mouseleave`, `mouseover`, `mouseout`, `mousemove`, `mousedown`, `mouseup`
*   **Keyboard:** `keydown`, `keyup`, `keypress`
*   **Form:** `submit`, `change` (on blur for inputs/selects/textareas), `input` (immediate value change), `focus`, `blur`
*   **Document/Window:** `load` (often on `window`), `ready` (jQuery specific), `scroll`, `resize`

**Event Handler Function (`handlerFn(event)`):**

*   Receives a normalized jQuery `event` object.
*   `event.target`: The DOM element where the event originated.
*   `event.currentTarget`: The DOM element the handler is attached to (same as `this` in direct binding, ancestor in delegation).
*   `this`: Inside the handler, `this` refers to `event.currentTarget`. **Use traditional `function() { ... }` for handlers if you need `this` to be the element.** Arrow functions (`=>`) inherit `this` lexically. See `08-modern-js-interaction.md`.
*   `event.preventDefault()`: Stops the browser's default action (e.g., form submission, link navigation).
*   `event.stopPropagation()`: Stops the event from bubbling up the DOM tree.
*   `event.pageX`, `event.pageY`: Mouse coordinates relative to the document.
*   `event.which`: Key code for keyboard events or mouse button.

## Document Ready

Ensure the DOM is fully loaded before attaching handlers using `$(document).ready()` or its shorthand `$(function() { ... });`.

```javascript
// Shorthand
$(function() {
  // Your jQuery code here...
  console.log('DOM is ready!');

  // --- Direct Binding ---
  $('#myButton').on('click', function(event) {
    console.log('Button clicked!');
    $(this).text('Clicked!'); // 'this' is the button
  });

  // --- Event Delegation ---
  $('#myList').on('click', '.list-item', function(event) {
    const $item = $(this); // 'this' is the clicked .list-item
    console.log('List item clicked:', $item.text());
    $item.toggleClass('selected');
  });

  // --- Form Submission ---
  $('#myForm').on('submit', function(event) {
    event.preventDefault(); // IMPORTANT: Prevent default page reload
    console.log('Form submitting via jQuery...');
    // Perform validation or AJAX submission here
  });

  // --- Namespaced Events (for easier removal) ---
  $(window).on('scroll.myFeature', function() {
    // ... handle scroll ...
  });

}); // End document ready
```

## Removing Event Handlers (`.off()`)

*   Remove specific handler: `$('#myButton').off('click', specificHandlerFunction);`
*   Remove all click handlers: `$('#myButton').off('click');`
*   Remove namespaced event: `$(window).off('scroll.myFeature');` or `$(window).off('.myFeature');`
*   Remove delegated handler: `$('#myList').off('click', '.list-item');`
*   Remove all handlers: `$('#myElement').off();`

Use `.on()` for attaching events and prefer delegation for performance when dealing with multiple or dynamic child elements. Always wrap event binding code in `$(document).ready()` or `$(function() { ... });`.