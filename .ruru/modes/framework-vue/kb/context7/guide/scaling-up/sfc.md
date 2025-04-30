# Vue Single-File Components (SFC)

## Vue SFC Example (Options API)

This is an example of a Vue Single-File Component using the Options API. It demonstrates the basic structure of an SFC with a script section defining data, a template section rendering the data, and a style section for component-scoped CSS.

Source: https://github.com/vuejs/docs/blob/main/src/guide/scaling-up/sfc.md#_snippet_0

```vue
<script>
export default {
  data() {
    return {
      greeting: 'Hello World!'
    }
  }
}
</script>

<template>
  <p class="greeting">{{ greeting }}</p>
</template>

<style>
.greeting {
  color: red;
  font-weight: bold;
}
</style>
```

---

## Vue SFC Example (Composition API)

This is an example of a Vue Single-File Component using the Composition API. It showcases the `script setup` syntax for a more concise component definition with reactive data and a template section rendering that data, along with component-scoped CSS.

Source: https://github.com/vuejs/docs/blob/main/src/guide/scaling-up/sfc.md#_snippet_1

```vue
<script setup>
import { ref } from 'vue'
const greeting = ref('Hello World!')
</script>

<template>
  <p class="greeting">{{ greeting }}</p>
</template>

<style>
.greeting {
  color: red;
  font-weight: bold;
}
</style>
```

---

## Importing Vue SFC

This example shows how to import a Vue Single-File Component into another component using standard JavaScript module syntax. This requires a build setup with a compiler that can handle `.vue` files.

Source: https://github.com/vuejs/docs/blob/main/src/guide/scaling-up/sfc.md#_snippet_2

```javascript
import MyComponent from './MyComponent.vue'

export default {
  components: {
    MyComponent
  }
}
```

