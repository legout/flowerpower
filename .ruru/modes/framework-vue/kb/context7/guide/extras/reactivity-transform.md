# Vue Reactivity Transform

## Using $ref macro in Vue component

This snippet demonstrates how to use the `$ref` macro within a Vue component's `<script setup>` block to create a reactive variable `count`. The compiler transforms this into a standard `ref` usage, eliminating the need for `.value` in the template.

Source: https://github.com/vuejs/docs/blob/main/src/guide/extras/reactivity-transform.md#_snippet_0

```vue
<script setup>
let count = $ref(0)

console.log(count)

function increment() {
  count++
}
</script>

<template>
  <button @click="increment">{{ count }}</button>
</template>
```

---

## Compiled output of $ref usage

This JavaScript code shows the compiled output of the previous Vue component using the `$ref` macro. The `count` variable is now a standard Vue `ref`, and `.value` is used for accessing and modifying its value.

Source: https://github.com/vuejs/docs/blob/main/src/guide/extras/reactivity-transform.md#_snippet_1

```javascript
import { ref } from 'vue'

let count = ref(0)

console.log(count.value)

function increment() {
  count.value++
}
```

---

## Compiled props declaration in Vue

This JavaScript code shows the compiled output for the prop declaration in the preceding component. The `defineProps` macro and destructuring are transformed into a standard props declaration with default values and a `setup` function that accesses props.

Source: https://github.com/vuejs/docs/blob/main/src/guide/extras/reactivity-transform.md#_snippet_7

```javascript
export default {
  props: {
    msg: { type: String, required: true },
    count: { type: Number, default: 1 },
    foo: String
  },
  setup(props) {
    watchEffect(() => {
      console.log(props.msg, props.count, props.foo)
    })
  }
}
```

---

## Destructuring refs with $() macro

This JavaScript code demonstrates the usage of the `$()` macro for destructuring an object of refs returned by a composition function (`useMouse` from `@vueuse/core`).  The `$()` macro ensures that the destructured variables (`x` and `y`) become reactive variables.

Source: https://github.com/vuejs/docs/blob/main/src/guide/extras/reactivity-transform.md#_snippet_3

```javascript
import { useMouse } from '@vueuse/core'

const { x, y } = $(useMouse())

console.log(x, y)
```

---

## Converting existing refs with $() macro

This JavaScript code shows how to use the `$()` macro to convert an existing ref (returned by `myCreateRef()`) into a reactive variable. This is useful when a function is not explicitly known to return a ref.

Source: https://github.com/vuejs/docs/blob/main/src/guide/extras/reactivity-transform.md#_snippet_5

```javascript
function myCreateRef() {
  return ref(0)
}

let count = $(myCreateRef())
```

---

## Importing $ref macro from vue/macros

This snippet shows how to explicitly import the `$ref` macro from the `vue/macros` module. This is optional, as the macros are globally available when Reactivity Transform is enabled. However, explicit import provides better code clarity.

Source: https://github.com/vuejs/docs/blob/main/src/guide/extras/reactivity-transform.md#_snippet_2

```javascript
import { $ref } from 'vue/macros'

let count = $ref(0)
```

---

## Compiled output of $() destructuring

This snippet illustrates the compiled output of the previous JavaScript code using the `$()` macro for destructuring.  `toRef` is used to convert the properties from the `useMouse()` return object into refs.

Source: https://github.com/vuejs/docs/blob/main/src/guide/extras/reactivity-transform.md#_snippet_4

```javascript
import { toRef } from 'vue'
import { useMouse } from '@vueuse/core'

const __temp = useMouse(),
  x = toRef(__temp, 'x'),
  y = toRef(__temp, 'y')

console.log(x.value, y.value)
```

---

## Configuring webpack with vue-loader in JavaScript

This code snippet demonstrates how to configure webpack to use vue-loader for processing `.vue` files. It includes enabling the `reactivityTransform` option.  Requires `vue-loader@>=17.0.0`. It should be placed inside `webpack.config.js` file.

Source: https://github.com/vuejs/docs/blob/main/src/guide/extras/reactivity-transform.md#_snippet_17

```JavaScript
// webpack.config.js
module.exports = {
  module: {
    rules: [
      {
        test: /\.vue$/,
        loader: 'vue-loader',
        options: {
          reactivityTransform: true
        }
      }
    ]
  }
}
```

---

## Vite configuration for Reactivity Transform

This JavaScript code shows how to configure Reactivity Transform in a Vite project using `@vitejs/plugin-vue`. The `reactivityTransform` option is set to `true` within the Vue plugin options.

Source: https://github.com/vuejs/docs/blob/main/src/guide/extras/reactivity-transform.md#_snippet_15

```javascript
// vite.config.js
export default {
  plugins: [
    vue({
      reactivityTransform: true
    })
  ]
}
```

