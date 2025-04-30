# Vue.js Event Listener Documentation

## Increment Function in Vue Composition API (SFC)

This code defines a Vue component using the Composition API within a Single-File Component (SFC). It uses `ref` to create a reactive `count` variable and defines an `increment` function that increments the `count`'s value when called.  It highlights the usage of `ref` and updating its `.value`.

Source: https://github.com/vuejs/docs/blob/main/src/tutorial/src/step-4/description.md#_snippet_4

```vue
<script setup>
import { ref } from 'vue'

const count = ref(0)

function increment() {
  // update component state
  count.value++
}
</script>
```

---

## Binding Event Listener with v-on Directive in Vue

This code demonstrates how to use the `v-on` directive to bind a click event to a button element. When the button is clicked, the `increment` method is called. The component's `count` property is displayed within the button's text.

Source: https://github.com/vuejs/docs/blob/main/src/tutorial/src/step-4/description.md#_snippet_0

```vue-html
<button v-on:click="increment">{{ count }}</button>
```

---

## Shorthand Syntax for v-on Directive in Vue

This code shows the shorthand syntax for the `v-on` directive using the `@` symbol. It achieves the same functionality as `v-on:click`, binding the `increment` method to the button's click event.

Source: https://github.com/vuejs/docs/blob/main/src/tutorial/src/step-4/description.md#_snippet_1

```vue-html
<button @click="increment">{{ count }}</button>
```

