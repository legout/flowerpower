# Selectors & DOM Manipulation

Using jQuery to efficiently select and modify HTML elements.

## Core Concept: The jQuery Object `$()`

*   **Selecting:** Pass a CSS selector string to `$()` (e.g., `$('#myId')`, `$('.myClass')`, `$('div p')`). Returns a jQuery object containing *all* matched elements.
*   **Wrapping:** Pass a DOM element or array of elements to `$()` to wrap them in a jQuery object.
*   **Creating:** Pass an HTML string to `$()` to create new elements (e.g., `$('<p>New paragraph</p>')`).

## Selecting Elements

jQuery supports most CSS selectors, plus some custom ones.

*   **Basic:** `#myId`, `.myClass`, `tagName`, `*`
*   **Hierarchy:** `parent > child`, `ancestor descendant`, `prev + next`, `prev ~ siblings`
*   **Attribute:** `[attribute]`, `[attribute="value"]`, `[attribute^="value"]` (starts with), `[attribute$="value"]` (ends with), `[attribute*="value"]` (contains)
*   **Form:** `:input`, `:text`, `:password`, `:radio`, `:checkbox`, `:submit`, `:button`, `:checked`, `:selected`, `:disabled`, `:enabled`
*   **Positional/Filtering:** `:first`, `:last`, `:even`, `:odd`, `:eq(index)`, `:gt(index)`, `:lt(index)`, `:not(selector)`, `:has(selector)`, `:parent` (elements with children), `:empty` (elements with no children)

**Best Practices for Selectors:**

*   **Specificity:** Be as specific as possible. IDs (`#myId`) are fastest.
*   **Caching:** Store frequently used selections in variables (e.g., `const $myElement = $('#myElement');`). See `06-performance.md`.
*   **Context:** Limit the scope of your search: `$parentElement.find('.child')` or `$('.child', $parentElement)`.

```javascript
// Examples
const $mainTitle = $('#main-title');
const $buttons = $('.btn');
const $firstParagraph = $('article p:first');
const $emailInput = $('input[type="email"]');
const $navLinks = $('#main-nav a'); // Cache this selection
```

## DOM Manipulation Methods

Most methods operate on *all* elements in the jQuery object.

*   **Content:**
    *   `.html('<strong>New</strong>')`: Get or set inner HTML. **Caution with untrusted content (XSS).**
    *   `.text('New text')`: Get or set text content (safer, HTML is encoded).
    *   `.val()`: Get or set the value of form elements (`input`, `textarea`, `select`).
*   **Attributes & Properties:**
    *   `.attr('href', 'new-url')`: Get or set HTML attributes.
    *   `.removeAttr('disabled')`: Remove an attribute.
    *   `.prop('checked', true)`: Get or set element properties (like `checked`, `disabled`, `selectedIndex`). **Use `.prop()` for boolean attributes/properties.**
*   **CSS Classes:**
    *   `.addClass('active')`
    *   `.removeClass('old')`
    *   `.toggleClass('highlight')`
    *   `.hasClass('some-class')`: Returns boolean.
*   **CSS Styles:**
    *   `.css('color', 'red')`: Get or set a single CSS property.
    *   `.css({ color: 'blue', fontWeight: 'bold' })`: Set multiple properties (use camelCase for property names).
*   **Dimensions & Position:**
    *   `.width()`, `.height()`: Get/set CSS width/height (content box).
    *   `.innerWidth()`, `.innerHeight()`: Includes padding.
    *   `.outerWidth()`, `.outerHeight()`: Includes padding & border. `outerWidth(true)` includes margin.
    *   `.offset()`: Get position relative to the document.
    *   `.position()`: Get position relative to the offset parent.
*   **Adding Elements:**
    *   `.append('<span>More</span>')`: Insert content/elements at the end of each selected element.
    *   `.prepend('<span>Start</span>')`: Insert at the beginning.
    *   `.after('<hr>')`: Insert after each selected element.
    *   `.before('<hr>')`: Insert before each selected element.
    *   `$('content').appendTo('#target')`, `$('content').prependTo('#target')`, etc.
    *   *(Content can be HTML string, DOM element, or jQuery object)*
*   **Removing Elements:**
    *   `.remove()`: Remove selected elements (and their data/events).
    *   `.empty()`: Remove all child elements from selected elements.
    *   `.detach()`: Removes elements but keeps data/event handlers (useful for re-inserting later).
*   **Wrapping:**
    *   `.wrap('<div class="wrapper"></div>')`: Wraps each matched element individually.
    *   `.wrapAll('<div class="wrapper"></div>')`: Wraps all matched elements with a single wrapper.
    *   `.wrapInner('<div class="inner"></div>')`: Wraps the inner content of each matched element.
    *   `.unwrap()`: Removes the parent of the selected elements.

## DOM Traversal Methods

Navigate the DOM tree relative to the selected elements.

*   **Upward:** `.parent()`, `.parents([selector])`, `.closest(selector)`
*   **Downward:** `.children([selector])`, `.find(selector)`
*   **Sideways:** `.siblings([selector])`, `.next()`, `.prev()`, `.nextAll()`, `.prevAll()`
*   **Filtering:** `.filter(selector)`, `.not(selector)`, `.has(selector)`, `.first()`, `.last()`, `.eq(index)`

```javascript
// Example Manipulations & Traversal
$('#user-greeting').text('Welcome Back!');
$('.product-image').attr('alt', 'Updated alt text');
$('input[name="subscribe"]').prop('checked', true);
$('#error-message').addClass('alert alert-danger').text('Invalid input.').show();
$('.item-list').append('<li>New Item</li>');
$('.old-section').remove();
const $listItem = $('.item-list li:first');
$listItem.next().addClass('second-item'); // Add class to the second li