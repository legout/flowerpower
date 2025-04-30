# Vue Composition API FAQ

## Vue Composition API Example

Demonstrates a basic Vue component using Composition API with `<script setup>`. It defines a reactive `count` state, an `increment` function to update the state, and a `onMounted` lifecycle hook to log the initial count.  The template renders a button that increments the count when clicked.

Source: https://github.com/vuejs/docs/blob/main/src/guide/extras/composition-api-faq.md#_snippet_0

```vue
<script setup>
import { ref, onMounted } from 'vue'

// reactive state
const count = ref(0)

// functions that mutate state and trigger updates
function increment() {
  count.value++
}

// lifecycle hooks
onMounted(() => {
  console.log(`The initial count is ${count.value}.`)
})
</script>

<template>
  <button @click="increment">Count is: {{ count }}</button>
</template>
```

