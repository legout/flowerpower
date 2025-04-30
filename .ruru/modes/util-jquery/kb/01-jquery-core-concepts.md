+++
id = "jquery-core-concepts"
title = "jQuery: Core Concepts & Selectors"
tags = ["jquery", "core", "selectors", "caching"]
+++

# jQuery: Core Concepts & Selectors

This document covers fundamental jQuery concepts relevant to the `util-jquery` mode.

## The jQuery Object: `$` or `jQuery`

The core of jQuery is the `jQuery` function, typically accessed via the alias `$`. It's used to select DOM elements and create jQuery objects, which provide jQuery methods.

```javascript
// Select an element by ID
const myElement = $('#myElementId');

// Select elements by class
const items = $('.item-class');

// Select elements by tag name
const paragraphs = $('p');
```

## Selectors

jQuery uses CSS-style selectors to find elements. Efficiency matters:

1.  **ID Selector (`#id`):** Fastest. Use whenever possible for unique elements.
2.  **Class Selector (`.class`):** Efficient for selecting groups of elements.
3.  **Tag Selector (`tag`):** Less efficient than ID or class, especially in large documents.
4.  **Attribute Selectors (`[attribute=value]`):** Useful but can be slower.
5.  **Hierarchy & Filtering:** Combine selectors (`$('ul.nav > li')`, `.find()`, `.filter()`, `.closest()`). Be specific but avoid overly complex selectors.

## Caching jQuery Objects

Repeatedly selecting the same element(s) is inefficient. Store the result of a selection in a variable if you need to use it multiple times.

```javascript
// Inefficient: Selects the element twice
$('#myButton').text('Submit');
$('#myButton').addClass('active');

// Efficient: Selects the element once and caches it
const $myButton = $('#myButton'); // Convention: prefix jQuery object variables with $
$myButton.text('Submit');
$myButton.addClass('active');
```

**Key Takeaway:** Use specific selectors (prefer IDs) and cache jQuery objects for better performance and cleaner code.