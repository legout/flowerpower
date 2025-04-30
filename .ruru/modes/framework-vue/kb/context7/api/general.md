# Vue.js Global API: General

## Defining a Component with Composition API and render function

This code snippet demonstrates the usage of `defineComponent` with a function signature (Composition API and render function).  It defines a component that uses the Composition API to manage state (`count`) and returns a render function (using `h`) to create the component's virtual DOM.  The props are manually declared.

Source: https://github.com/vuejs/docs/blob/main/src/api/general.md#_snippet_3

```javascript
import { ref, h } from 'vue'

const Comp = defineComponent(
  (props) => {
    // use Composition API here like in <script setup>
    const count = ref(0)

    return () => {
      // render function or JSX
      return h('div', count.value)
    }
  },
  // extra options, e.g. declare props and emits
  {
    props: {
      /* ... */
    }
  }
)
```

---

## Using nextTick with Composition API in Vue

This code snippet demonstrates how to use `nextTick` within a Vue component using the Composition API. It increments a reactive `count` value and uses `nextTick` to wait for the DOM to update before asserting the updated value. The `await nextTick()` ensures the DOM has been updated before proceeding, demonstrating its usage with async/await.

Source: https://github.com/vuejs/docs/blob/main/src/api/general.md#_snippet_1

```vue
<script setup>
import { ref, nextTick } from 'vue'

const count = ref(0)

async function increment() {
  count.value++

  // DOM not yet updated
  console.log(document.getElementById('counter').textContent) // 0

  await nextTick()
  // DOM is now updated
  console.log(document.getElementById('counter').textContent) // 1
}
</script>

<template>
  <button id="counter" @click="increment">{{ count }}</button>
</template>
```

---

## Using webpack Treeshaking with defineComponent

This code snippet demonstrates how to mark a `defineComponent` call as side-effect-free to enable webpack treeshaking. Adding the `/*#__PURE__*/` annotation before the function call tells webpack that it's safe to remove this component if it's not used in the application, preventing unnecessary code from being included in the final bundle.

Source: https://github.com/vuejs/docs/blob/main/src/api/general.md#_snippet_5

```javascript
export default /*#__PURE__*/ defineComponent(/* ... */)
```

---

## Using nextTick with Options API in Vue

This code snippet demonstrates how to use `nextTick` within a Vue component using the Options API. It increments a `count` data property and uses `nextTick` to wait for the DOM to update before asserting the updated value. The `await nextTick()` ensures the DOM has been updated before proceeding, demonstrating its usage with async/await in the Options API context.

Source: https://github.com/vuejs/docs/blob/main/src/api/general.md#_snippet_2

```vue
<script>
import { nextTick } from 'vue'

export default {
  data() {
    return {
      count: 0
    }
  },
  methods: {
    async increment() {
      this.count++

      // DOM not yet updated
      console.log(document.getElementById('counter').textContent) // 0

      await nextTick()
      // DOM is now updated
      console.log(document.getElementById('counter').textContent) // 1
    }
  }
}
</script>

<template>
  <button id="counter" @click="increment">{{ count }}</button>
</template>
```

---

## Defining a Component with TSX and Generics

This code snippet shows how to define a Vue component using `defineComponent` with TypeScript, TSX, and generics.  It defines a generic type `T` for the `msg` and `list` props. The component utilizes the Composition API and returns a render function using JSX.  Manual runtime props declaration is needed.

Source: https://github.com/vuejs/docs/blob/main/src/api/general.md#_snippet_4

```typescript
const Comp = defineComponent(
  <T extends string | number>(props: { msg: T; list: T[] }) => {
    // use Composition API here like in <script setup>
    const count = ref(0)

    return () => {
      // render function or JSX
      return <div>{count.value}</div>
    }
  },
  // manual runtime props declaration is currently still needed.
  {
    props: ['msg', 'list']
  }
)
```

---

## Accessing Vue Version in JavaScript

This code snippet shows how to import and access the current version of Vue. It imports the `version` export from the `vue` package and logs it to the console. This can be useful for debugging or feature detection based on the Vue version.

Source: https://github.com/vuejs/docs/blob/main/src/api/general.md#_snippet_0

```javascript
import { version } from 'vue'

console.log(version)
```

