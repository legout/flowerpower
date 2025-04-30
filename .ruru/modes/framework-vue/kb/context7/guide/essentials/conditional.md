# Vue.js Conditional Rendering

## Initializing reactive data with ref

This script initializes a reactive boolean variable named `awesome` using `ref` from the `vue` library. The `awesome` variable controls the conditional rendering examples in the document.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/conditional.md#_snippet_0

```javascript
import { ref } from 'vue'
const awesome = ref(true)
```

---

## Conditional rendering with v-if on template

This snippet demonstrates the use of `v-if` on a `<template>` element to conditionally render multiple elements. The elements inside the template are only rendered if the `ok` variable is truthy. The template element itself is not rendered.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/conditional.md#_snippet_4

```vue-html
<template v-if="ok">
  <h1>Title</h1>
  <p>Paragraph 1</p>
  <p>Paragraph 2</p>
</template>
```

---

## Rendering content with v-if and v-else

This snippet shows how to use `v-if` and `v-else` directives together to render different content based on a condition. A button toggles the value of `awesome`, which controls which h1 element is displayed.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/conditional.md#_snippet_2

```vue-html
<button @click="awesome = !awesome">Toggle</button>

<h1 v-if="awesome">Vue is awesome!</h1>
<h1 v-else>Oh no 😢</h1>
```

---

## Showing content with v-show

This snippet demonstrates the use of the `v-show` directive to conditionally display an element by toggling its `display` CSS property. The element is always rendered, but its visibility is controlled by the `ok` variable.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/conditional.md#_snippet_5

```vue-html
<h1 v-show="ok">Hello!</h1>
```

