# Using Vue with TypeScript

## Using TypeScript in Single-File Components

Shows how to use TypeScript within Vue Single-File Components (SFCs) by adding the `lang="ts"` attribute to the `<script>` tag. This enables type checking and auto-completion in the template.  The example defines a component with a data property and displays it in the template.

Source: https://github.com/vuejs/docs/blob/main/src/guide/typescript/overview.md#_snippet_2

```vue
<script lang="ts">
import { defineComponent } from 'vue'

export default defineComponent({
  data() {
    return {
      count: 1
    }
  }
})
</script>

<template>
  <!-- type checking and auto-completion enabled -->
  {{ count.toFixed(2) }}
</template>
```

---

## Define Component with TypeScript

Demonstrates how to use `defineComponent()` to enable type inference for component options in Vue.js. This includes defining props with their respective types and accessing them within the component's `data` and `mounted` hooks. It showcases type checking for props, data properties, and the component instance (`this`).

Source: https://github.com/vuejs/docs/blob/main/src/guide/typescript/overview.md#_snippet_0

```typescript
import { defineComponent } from 'vue'

export default defineComponent({
  // type inference enabled
  props: {
    name: String,
    msg: { type: String, required: true }
  },
  data() {
    return {
      count: 1
    }
  },
  mounted() {
    this.name // type: string | undefined
    this.msg // type: string
    this.count // type: number
  }
})
```

---

## TypeScript Casting in Templates

Illustrates how to perform type casting in Vue templates when using TypeScript. This is useful when TypeScript cannot infer the correct type, and you need to explicitly cast a variable to a specific type to access its properties or methods.  The example casts a union type (string | number) to a number to use the `toFixed` method.

Source: https://github.com/vuejs/docs/blob/main/src/guide/typescript/overview.md#_snippet_4

```vue
<script setup lang="ts">
let x: string | number = 1
</script>

<template>
  {{ (x as number).toFixed(2) }}
</template>
```

---

## Define Component with Props and Setup

Illustrates using `defineComponent()` with the `setup()` function to enable type inference for props in Vue.js when using the Composition API. This example demonstrates how to define props and access them within the `setup()` function, with TypeScript providing type checking for the props.

Source: https://github.com/vuejs/docs/blob/main/src/guide/typescript/overview.md#_snippet_1

```typescript
import { defineComponent } from 'vue'

export default defineComponent({
  // type inference enabled
  props: {
    message: String
  },
  setup(props) {
    props.message // type: string | undefined
  }
})
```

