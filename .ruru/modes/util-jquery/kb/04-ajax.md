# AJAX (Asynchronous JavaScript and XML)

Making asynchronous HTTP requests using jQuery's AJAX methods.

## Core Concept

jQuery simplifies making asynchronous requests to a server without reloading the page, commonly used for fetching data, submitting forms, or updating page sections dynamically. It wraps the browser's native `XMLHttpRequest` and provides a simpler, cross-browser interface, often returning Promise-like objects (Deferred objects).

## Key AJAX Methods

*   **`$.ajax(url, [settings])` or `$.ajax([settings])`:**
    *   The core, most configurable method. All others are shorthands.
    *   **Common Settings:**
        *   `url`: Request URL.
        *   `method` or `type`: HTTP method (`'GET'`, `'POST'`, `'PUT'`, `'DELETE'`, etc. Default: `'GET'`).
        *   `data`: Data to send (Object, String, Array). Automatically processed.
        *   `dataType`: Expected data type from server (`'json'`, `'xml'`, `'html'`, `'text'`, `'script'`). jQuery attempts inference.
        *   `contentType`: Type of data being sent (e.g., `'application/json; charset=utf-8'` for JSON POST. Default: `'application/x-www-form-urlencoded; charset=UTF-8'`).
        *   `headers`: Object of additional request headers.
        *   `success(data, textStatus, jqXHR)`: Callback on success.
        *   `error(jqXHR, textStatus, errorThrown)`: Callback on error.
        *   `complete(jqXHR, textStatus)`: Callback after success or error.
        *   `beforeSend(jqXHR, settings)`: Pre-request callback. Return `false` to cancel.
    *   **Returns:** A `jqXHR` object (jQuery Deferred), which is Promise-like. Use `.done()`, `.fail()`, `.always()`.

*   **`$.get(url, [data], [successCallback], [dataType])`:**
    *   Shorthand for GET. `data` appended as query parameters.

*   **`$.post(url, [data], [successCallback], [dataType])`:**
    *   Shorthand for POST. `data` sent in request body.

*   **`$.getJSON(url, [data], [successCallback])`:**
    *   Shorthand for GET with `dataType: 'json'`.

*   **`$(selector).load(url, [data], [completeCallback])`:**
    *   Fetches HTML from `url` and inserts into selected element(s).
    *   POST if `data` provided, otherwise GET.
    *   Can load fragments: `$(selector).load('page.html #content')`.

## Promise Interface (`.done()`, `.fail()`, `.always()`)

Prefer the Promise interface over `success`/`error`/`complete` callbacks for cleaner asynchronous code.

```javascript
// Example using Promises with $.ajax
$.ajax({
  url: '/api/items/123',
  method: 'GET',
  dataType: 'json'
})
.done(function(data) {
  console.log('Item data:', data);
  // Process success
})
.fail(function(jqXHR, textStatus, errorThrown) {
  console.error('Error fetching item:', textStatus, errorThrown);
  // Handle error - jqXHR contains details like status, responseText
})
.always(function() {
  console.log('GET request finished.');
  // Cleanup, hide loading indicator, etc.
});
```

## Error Handling

*   Use the `error` callback or the `.fail()` promise method.
*   The `jqXHR` object provides details: `status`, `statusText`, `responseText`, `responseJSON` (if applicable).
*   `textStatus` indicates error type (e.g., "timeout", "error", "abort", "parsererror").
*   `errorThrown` provides the textual portion of the HTTP status (e.g., "Not Found", "Internal Server Error").

## Example: POSTing JSON Data

```javascript
$(function() {
  $('#addItemForm').on('submit', function(event) {
    event.preventDefault();

    const newItem = {
      name: $('#itemNameInput').val(),
      quantity: parseInt($('#itemQuantityInput').val(), 10) || 0
    };

    $.ajax({
      url: '/api/items',
      method: 'POST',
      contentType: 'application/json; charset=utf-8', // Specify JSON
      data: JSON.stringify(newItem), // Stringify the object
      dataType: 'json' // Expect JSON response
    })
    .done(function(createdItem) {
      console.log('Item created:', createdItem);
      alert('Item added successfully!');
      $('#addItemForm')[0].reset();
    })
    .fail(function(jqXHR, textStatus, errorThrown) {
      console.error('Error creating item:', textStatus, errorThrown);
      alert(`Error: ${jqXHR.responseJSON?.message || textStatus}`);
    });
  });
});
```

*(Refer to the jQuery AJAX documentation for full details: https://api.jquery.com/category/ajax/)*