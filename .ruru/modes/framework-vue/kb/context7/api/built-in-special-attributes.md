# Vue.js Built-in Special Attributes Documentation

## Template Ref in Options API in Vue

This code demonstrates how to use the `ref` attribute in the Options API in Vue.js to create a template reference. The `ref` attribute is bound to a DOM element, making it accessible via `this.$refs` within the component instance. The `ref` will be registered under the component's `this.$refs` object.

Source: https://github.com/vuejs/docs/blob/main/src/api/built-in-special-attributes.md#_snippet_2

```vue-html
<!-- stored as this.$refs.p -->
<p ref="p">hello</p>
```

---

## List Rendering with Key Attribute in Vue

This code demonstrates the usage of the `key` attribute within a `v-for` directive in Vue.js. The `key` attribute helps Vue's virtual DOM efficiently update and re-render list items.  It expects a unique `number`, `string`, or `symbol` for each item.

Source: https://github.com/vuejs/docs/blob/main/src/api/built-in-special-attributes.md#_snippet_0

```vue-html
<ul>
  <li v-for="item in items" :key="item.id">...</li>
</ul>
```

---

## Using `is` attribute for dynamic components in Vue

This code snippet illustrates using the `is` attribute to render a Vue component in place of a native HTML element. The `vue:` prefix tells Vue.js to treat the element as a Vue component, resolving potential template parsing issues within the DOM.

Source: https://github.com/vuejs/docs/blob/main/src/api/built-in-special-attributes.md#_snippet_5

```vue-html
<table>
  <tr is="vue:my-row-component"></tr>
</table>
```

---

## Template Ref in Composition API in Vue

This code demonstrates how to use the `ref` attribute in the Composition API with `<script setup>` in Vue.js to create a template reference. The `useTemplateRef` helper is imported and used to bind the ref to the DOM element. The reference will be stored in a ref with matching name.

Source: https://github.com/vuejs/docs/blob/main/src/api/built-in-special-attributes.md#_snippet_3

```vue
<script setup>
import { useTemplateRef } from 'vue'

const pRef = useTemplateRef('p')
</script>

<template>
  <p ref="p">hello</p>
</template>
```

---

## Function Ref in Vue

This code shows an alternative usage of the `ref` attribute, accepting a function value. This function provides full control over where to store the reference to the element.

Source: https://github.com/vuejs/docs/blob/main/src/api/built-in-special-attributes.md#_snippet_4

```vue-html
<ChildComponent :ref="(el) => child = el" />
```

