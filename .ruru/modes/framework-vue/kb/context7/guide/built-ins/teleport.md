# Vue.js Teleport Component Documentation

## MyModal Component (Composition API)

This snippet shows the implementation of the <MyModal> component using the Composition API. It uses a ref to manage the open/close state of the modal and includes the modal's template and styles.  The modal is styled with fixed positioning and a z-index.

Source: https://github.com/vuejs/docs/blob/main/src/guide/built-ins/teleport.md#_snippet_1

```vue
<script setup>
import { ref } from 'vue'

const open = ref(false)
</script>

<template>
  <button @click="open = true">Open Modal</button>

  <div v-if="open" class="modal">
    <p>Hello from the modal!</p>
    <button @click="open = false">Close</button>
  </div>
</template>

<style scoped>
.modal {
  position: fixed;
  z-index: 999;
  top: 20%;
  left: 50%;
  width: 300px;
  margin-left: -150px;
}
</style>
```

---

## Teleporting the Modal

This snippet demonstrates how to use the <Teleport> component to move the modal's content to the body tag. The to prop specifies the target element, which can be a CSS selector or a DOM node. This allows the modal to break out of the nested DOM structure and avoid potential styling and z-index issues.

Source: https://github.com/vuejs/docs/blob/main/src/guide/built-ins/teleport.md#_snippet_3

```vue-html
<button @click="open = true">Open Modal</button>

<Teleport to="body">
  <div v-if="open" class="modal">
    <p>Hello from the modal!</p>
    <button @click="open = false">Close</button>
  </div>
</Teleport>
```

---

## Multiple Teleports on the Same Target

This snippet shows how multiple <Teleport> components can mount their content to the same target element. The order will be a simple append, with later mounts located after earlier ones, but all within the target element.

Source: https://github.com/vuejs/docs/blob/main/src/guide/built-ins/teleport.md#_snippet_5

```vue-html
<Teleport to="#modals">
  <div>A</div>
</Teleport>
<Teleport to="#modals">
  <div>B</div>
</Teleport>
```

---

## Deferred Teleport Usage

Demonstrates using the `defer` prop in `<Teleport>` to postpone target resolution until other application parts have mounted. This targets a container rendered by Vue later in the component tree.

Source: https://github.com/vuejs/docs/blob/main/src/guide/built-ins/teleport.md#_snippet_6

```vue-html
<Teleport defer to="#late-div">...</Teleport>

<!-- somewhere later in the template -->
<div id="late-div"></div>
```

---

## Disabling Teleport Conditionally

This snippet shows how to conditionally disable the <Teleport> component using the disabled prop.  The disabled prop is bound to a boolean value, allowing for dynamic control over whether the teleport is active.  This can be useful for rendering components differently based on the environment (e.g., desktop vs. mobile).

Source: https://github.com/vuejs/docs/blob/main/src/guide/built-ins/teleport.md#_snippet_4

```vue-html
<Teleport :disabled="isMobile">
  ...
</Teleport>
```

