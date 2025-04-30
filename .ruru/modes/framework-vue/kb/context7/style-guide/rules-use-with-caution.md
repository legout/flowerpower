# Vue.js Priority D Rules: Use with Caution

## Parent-Child Communication with Events (Composition API) - Good

This code demonstrates the preferred pattern for parent-child component communication using events with Composition API.  The child component emits an event to notify the parent of a change, and the parent handles the event. The `defineEmits` function is used to declare emitted events.

Source: https://github.com/vuejs/docs/blob/main/src/style-guide/rules-use-with-caution.md#_snippet_5

```vue
<script setup>
defineProps({
  todo: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['input'])
</script>

<template>
  <input :value="todo.text" @input="emit('input', $event.target.value)" />
</template>

```

```vue
<script setup>
defineProps({
  todo: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['delete'])
</script>

<template>
  <span>
    {{ todo.text }}
    <button @click="emit('delete')">×</button>
  </span>
</template>

```

---

## Styling Vue Components with Scoped CSS - Good Example

This code demonstrates the recommended approach of using class selectors within a `<style scoped>` block in a Vue component. This is more performant because Vue only needs to add attributes to elements with the specified class, instead of every element.

Source: https://github.com/vuejs/docs/blob/main/src/style-guide/rules-use-with-caution.md#_snippet_1

```vue-html
<template>
  <button class="btn btn-close">×</button>
</template>

<style scoped>
.btn-close {
  background-color: red;
}
</style>
```

