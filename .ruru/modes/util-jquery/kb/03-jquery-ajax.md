+++
id = "jquery-ajax"
title = "jQuery: AJAX Operations"
tags = ["jquery", "ajax", "async", "fetch", "api"]
+++

# jQuery: AJAX Operations

This document covers making asynchronous HTTP requests (AJAX) using jQuery.

## Core AJAX Method: `$.ajax()`

The `$.ajax()` method is the foundation for all jQuery AJAX requests. It offers extensive configuration options.

```javascript
$.ajax({
  url: '/api/data', // The URL to request
  method: 'GET', // HTTP method (GET, POST, PUT, DELETE, etc.)
  dataType: 'json', // Expected data type from the server (e.g., 'json', 'html', 'text')
  data: { // Data to send (for POST/PUT requests)
    id: 123,
    category: 'example'
  },
  beforeSend: function() {
    // Code to run before sending the request (e.g., show loading indicator)
    $('#loading').show();
  },
  success: function(data, textStatus, jqXHR) {
    // Code to run on successful response
    console.log('Data received:', data);
    // Process the data (e.g., update the DOM)
    $('#results').html('Success: ' + data.message);
  },
  error: function(jqXHR, textStatus, errorThrown) {
    // Code to run if the request fails
    console.error('AJAX Error:', textStatus, errorThrown);
    $('#results').html('Error: ' + errorThrown);
  },
  complete: function() {
    // Code to run after success or error (e.g., hide loading indicator)
    $('#loading').hide();
  }
});
```

## Shorthand Methods

jQuery provides convenient shorthand methods for common AJAX scenarios:

*   **`$.get(url, [data], [successCallback], [dataType])`**: Performs a GET request.
*   **`$.post(url, [data], [successCallback], [dataType])`**: Performs a POST request.
*   **`$.getJSON(url, [data], [successCallback])`**: Performs a GET request and expects JSON data.
*   **`$(selector).load(url, [data], [completeCallback])`**: Loads HTML from a URL and inserts it into the selected element(s).

```javascript
// Example using $.get()
$.get('/api/items', { category: 'books' }, function(items) {
  // Process the received 'items' array (assumed JSON)
  items.forEach(item => {
    $('#item-list').append(`<li>${item.title}</li>`);
  });
});

// Example using $.post()
$.post('/api/users', { name: 'Roo', role: 'Specialist' }, function(response) {
  console.log('User created:', response);
});
```

## Promises (`.done()`, `.fail()`, `.always()`)

`$.ajax()` (and its shorthand methods) return a `jqXHR` object, which implements the Promise interface. This allows for cleaner handling of asynchronous operations.

```javascript
$.ajax({
  url: '/api/status',
  method: 'GET'
})
.done(function(data) {
  // Success handler
  console.log('Status:', data.status);
})
.fail(function(jqXHR, textStatus, errorThrown) {
  // Error handler
  console.error('Failed to get status:', errorThrown);
})
.always(function() {
  // Completion handler (runs after done or fail)
  console.log('Status request finished.');
});
```

**Key Takeaways:** Use `$.ajax()` for complex requests or `.get()`, `.post()`, `$.getJSON()` for simpler cases. Handle success, error, and completion using callbacks or the Promise interface (`.done()`, `.fail()`, `.always()`).