# Vue.js State Management

## Component A - Composition API - Vue

This Vue component (ComponentA.vue) imports the shared `store` and displays the `count` property. It utilizes the Composition API and assumes the `store` module exports a reactive object.

Source: https://github.com/vuejs/docs/blob/main/src/guide/scaling-up/state-management.md#_snippet_3

```Vue
<!-- ComponentA.vue -->
<script setup>
import { store } from './store.js'
</script>

<template>From A: {{ store.count }}</template>
```

---

## Creating a Reactive Store - JavaScript

This JavaScript module creates a reactive store using Vue's `reactive` API.  The store contains a `count` property initialized to 0. It is designed to be imported and used across multiple components to share state.

Source: https://github.com/vuejs/docs/blob/main/src/guide/scaling-up/state-management.md#_snippet_2

```JavaScript
// store.js
import { reactive } from 'vue'

export const store = reactive({
  count: 0
})
```

---

## Counter Component - Options API - Vue

This Vue component implements a simple counter using the Options API. It defines the `count` state in the `data` option and an `increment` method to update the count. The template displays the current count.

Source: https://github.com/vuejs/docs/blob/main/src/guide/scaling-up/state-management.md#_snippet_1

```Vue
<script>
export default {
  // state
  data() {
    return {
      count: 0
    }
  },
  // actions
  methods: {
    increment() {
      this.count++
    }
  }
}
</script>

<!-- view -->
<template>{{ count }}</template>
```

---

## Centralizing Mutations with Methods - JavaScript

This JavaScript module defines an `increment` method within the reactive store.  This method is intended to be the sole way to update the `count` property, centralizing mutation logic and improving maintainability.

Source: https://github.com/vuejs/docs/blob/main/src/guide/scaling-up/state-management.md#_snippet_8

```JavaScript
// store.js
import { reactive } from 'vue'

export const store = reactive({
  count: 0,
  increment() {
    this.count++
  }
})
```

---

## Component A - Options API - Vue

This Vue component (ComponentA.vue) imports the shared `store` and makes it available as a data property.  It utilizes the Options API to achieve this. The template displays the `count` property from the store.

Source: https://github.com/vuejs/docs/blob/main/src/guide/scaling-up/state-management.md#_snippet_5

```Vue
<!-- ComponentA.vue -->
<script>
import { store } from './store.js'

export default {
  data() {
    return {
      store
    }
  }
}
</script>

<template>From A: {{ store.count }}</template>
```

---

## Counter Component - Composition API - Vue

This Vue component demonstrates a simple counter using the Composition API. It initializes a reactive `count` variable using `ref` and provides an `increment` function to update the count. The template displays the current count.

Source: https://github.com/vuejs/docs/blob/main/src/guide/scaling-up/state-management.md#_snippet_0

```Vue
<script setup>
import { ref } from 'vue'

// state
const count = ref(0)

// actions
function increment() {
  count.value++
}
</script>

<!-- view -->
<template>{{ count }}</template>
```

---

## Component B - Composition API - Vue

This Vue component (ComponentB.vue) imports the shared `store` and displays the `count` property.  It utilizes the Composition API and assumes the `store` module exports a reactive object. Similar to ComponentA, it reflects the state in the shared store.

Source: https://github.com/vuejs/docs/blob/main/src/guide/scaling-up/state-management.md#_snippet_4

```Vue
<!-- ComponentB.vue -->
<script setup>
import { store } from './store.js'
</script>

<template>From B: {{ store.count }}</template>
```

---

## Composable with Global and Local State - JavaScript

This JavaScript module demonstrates a composable function (`useCount`) that returns both global and local reactive state using Vue's `ref` API.  `globalCount` is shared across all components using the composable, while `localCount` is unique to each component instance.

Source: https://github.com/vuejs/docs/blob/main/src/guide/scaling-up/state-management.md#_snippet_10

```JavaScript
import { ref } from 'vue'

// global state, created in module scope
const globalCount = ref(1)

export function useCount() {
  // local state, created per-component
  const localCount = ref(1)

  return {
    globalCount,
    localCount
  }
}
```

---

## Calling Store Method from Template - Vue

This Vue template demonstrates calling the `increment` method on the shared store when a button is clicked.  This approach centralizes the mutation logic within the store, enhancing maintainability.

Source: https://github.com/vuejs/docs/blob/main/src/guide/scaling-up/state-management.md#_snippet_9

```Vue
<template>
  <button @click="store.increment()">
    From B: {{ store.count }}
  </button>
</template>
```

