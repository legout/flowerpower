# Performance Patterns & Best Practices

Writing more efficient jQuery code to avoid bottlenecks.

## 1. Cache jQuery Selections

*   **Problem:** Repeatedly selecting the same element(s) (e.g., `$('#myElement')`) forces jQuery to re-query the DOM each time.
*   **Solution:** Store the result of a selection in a variable (conventionally prefixed with `$`) and reuse it.

```javascript
// Inefficient:
// $('#myList').append('<li>Item 1</li>');
// $('#myList').addClass('updated');

// Efficient:
const $myList = $('#myList'); // Cache the selection
$myList.append('<li>Item 1</li>');
$myList.addClass('updated');
```

## 2. Use Efficient & Specific Selectors

*   **Order of Efficiency (Fastest to Slowest, Generally):**
    1.  ID Selector: `$('#myId')`
    2.  Tag Selector: `$('div')`
    3.  Class Selector: `$('.myClass')`
    4.  Attribute Selectors: `$('input[type="text"]')`
    5.  Pseudo-selectors / Complex Combinators: `:visible`, `ancestor descendant`
*   **Be Specific:** Avoid overly broad selectors. `$('#mainContent p')` is better than `$('p')`.
*   **Use Context:** When searching within a known element, provide context: `$parentElement.find('.child')` or `$('.child', $parentElement)`.

## 3. Use Event Delegation

*   **Problem:** Attaching handlers to many individual elements consumes memory and is slow, especially for dynamic content.
*   **Solution:** Attach a single handler to a static parent element using `.on()` with a child selector.

```javascript
// Inefficient (attaches handler to potentially many LIs):
// $('#myList li').on('click', function() { ... });

// Efficient (attaches single handler to UL):
$('#myList').on('click', 'li', function(event) {
  // 'this' refers to the clicked LI element
  const $clickedItem = $(this);
  console.log('Clicked:', $clickedItem.text());
});
```
*   **Benefits:** Fewer handlers, automatically works for elements added later.

## 4. Minimize DOM Manipulation in Loops

*   **Problem:** Modifying the DOM (appending, changing attributes/styles) inside a loop is often slow due to browser reflows/repaints.
*   **Solution:** Build HTML strings or create DOM elements/fragments in memory within the loop, then append/update the DOM *once* after the loop.

```javascript
const data = [/* ... large array ... */];
const $list = $('#targetList');

// Efficient (String building):
let listHtml = '';
data.forEach(item => {
  listHtml += `<li>${item.name}</li>`;
});
$list.html(listHtml); // Single DOM update

// Efficient (Document Fragment):
const fragment = document.createDocumentFragment();
data.forEach(item => {
  const $li = $('<li>').text(item.name); // Create element in memory
  fragment.appendChild($li[0]); // Append raw DOM node to fragment
});
$list.append(fragment); // Single DOM append
```

## 5. Detach Elements for Complex Updates (Advanced)

*   For very complex manipulations on a large DOM subtree, consider detaching it (`.detach()`), performing updates, and then re-appending it to minimize reflows during the updates. Use with caution.

```javascript
const $container = $('#complexContainer').detach(); // Detach

// ... Perform multiple updates on $container ...

$container.appendTo('#originalParent'); // Re-append
```

## 6. Debounce/Throttle Frequent Events

*   **Problem:** Handlers for frequent events (`scroll`, `resize`, `mousemove`, `keyup`) can fire excessively.
*   **Solution:** Use **debouncing** (wait until events stop firing for a period) or **throttling** (execute at most once per interval) utility functions (e.g., from Lodash/Underscore, or simple implementations) to limit handler execution.

```javascript
// Conceptual example using a hypothetical debounce function
// $(window).on('resize', debounce(function() {
//   // Perform expensive layout calculations here
// }, 250)); // Execute 250ms after the last resize event
```

*(Profile your code using browser developer tools to identify actual bottlenecks.)*