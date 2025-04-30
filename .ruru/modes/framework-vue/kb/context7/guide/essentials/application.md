# Creating Vue Applications

## Mounting a Vue App in JavaScript

This code demonstrates how to mount a Vue application to a DOM element using its ID. The `app.mount()` function is called with the CSS selector of the container element, which will be replaced by the application's root component.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/application.md#_snippet_2

```JavaScript
app.mount('#app')
```

---

## Configuring Error Handler in JavaScript

This code demonstrates how to configure a global error handler for a Vue application. The `app.config.errorHandler` function is set to a callback that will be called whenever an error occurs in any descendant component.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/application.md#_snippet_6

```JavaScript
app.config.errorHandler = (err) => {
  /* handle error */
}
```

---

## Vue App with In-DOM Template in JavaScript

This JavaScript code creates a Vue application instance that uses the `innerHTML` of the mounting point as the component's template.  The component defines a `data` property called `count` initialized to 0.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/application.md#_snippet_5

```JavaScript
import { createApp } from 'vue'

const app = createApp({
  data() {
    return {
      count: 0
    }
  }
})

app.mount('#app')
```

---

## Initializing a Vue Application Instance in JavaScript

This code snippet demonstrates how to create a new Vue application instance using the `createApp` function from the 'vue' library. It imports the function and creates an application instance with a root component (represented by the options object).

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/application.md#_snippet_0

```JavaScript
import { createApp } from 'vue'

const app = createApp({
  /* root component options */
})
```

---

## In-DOM Template for Vue Component (HTML)

This HTML code provides a template directly within the mount container. The template contains a button that increments a counter when clicked.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/application.md#_snippet_4

```HTML
<div id="app">
  <button @click="count++">{{ count }}</button>
</div>
```

---

## Creating Multiple Application Instances in JavaScript

This code shows how to create and mount multiple Vue application instances on the same page. Each instance is created using `createApp` and mounted to a different container element, allowing them to operate independently.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/application.md#_snippet_8

```JavaScript
const app1 = createApp({
  /* ... */
})
app1.mount('#container-1')

const app2 = createApp({
  /* ... */
})
app2.mount('#container-2')
```

---

## HTML Container for Vue Application

This HTML snippet defines a container element with the ID 'app'. The Vue application will be mounted to this element, and the application's root component will be rendered inside it.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/application.md#_snippet_3

```HTML
<div id="app"></div>
```

