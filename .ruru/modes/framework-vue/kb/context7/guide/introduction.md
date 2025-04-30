# Vue.js Introduction

## Vue Single-File Component (Composition API)

This snippet demonstrates a Vue Single-File Component (SFC) using the Composition API and `<script setup>`. It defines a reactive `count` ref, a template with a button to increment the count, and scoped CSS to style the button.

Dependencies: vue
Input: None
Output: A complete Vue component definition.

Source: https://github.com/vuejs/docs/blob/main/src/guide/introduction.md#_snippet_4

```vue
<script setup>
import { ref } from 'vue'
const count = ref(0)
</script>

<template>
  <button @click="count++">Count is: {{ count }}</button>
</template>

<style scoped>
button {
  font-weight: bold;
}
</style>
```

---

## Vue Component (Options API)

This snippet shows a Vue component implemented using the Options API. It includes reactive data (`count`), a method to increment the count (`increment`), and a lifecycle hook (`mounted`) to log the initial count.

Dependencies: None
Input: None
Output: A Vue component object.

Source: https://github.com/vuejs/docs/blob/main/src/guide/introduction.md#_snippet_5

```vue
<script>
export default {
  // Properties returned from data() become reactive state
  // and will be exposed on `this`.
  data() {
    return {
      count: 0
    }
  },

  // Methods are functions that mutate state and trigger updates.
  // They can be bound as event handlers in templates.
  methods: {
    increment() {
      this.count++
    }
  },

  // Lifecycle hooks are called at different stages
  // of a component's lifecycle.
  // This function will be called when the component is mounted.
  mounted() {
    console.log(`The initial count is ${this.count}.`)
  }
}
</script>

<template>
  <button @click="increment">Count is: {{ count }}</button>
</template>
```

---

## Initializing Vue App (Options API)

This snippet demonstrates how to initialize a Vue application using the Options API. It creates a new Vue app instance, defines a reactive `count` data property, and mounts the app to an HTML element with the ID 'app'.

Dependencies: vue
Input: None
Output: A Vue application instance mounted to the DOM.

Source: https://github.com/vuejs/docs/blob/main/src/guide/introduction.md#_snippet_0

```js
import { createApp } from 'vue'

createApp({
  data() {
    return {
      count: 0
    }
  }
}).mount('#app')
```

---

## Vue Template for Counter

This snippet defines the HTML template for a simple counter component in Vue. It includes a button that increments the `count` property when clicked.  The `count` property is displayed within the button.

Dependencies: None
Input: None
Output: HTML markup for the counter component.

Source: https://github.com/vuejs/docs/blob/main/src/guide/introduction.md#_snippet_2

```vue-html
<div id="app">
  <button @click="count++">
    Count is: {{ count }}
  </button>
</div>
```

