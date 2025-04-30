# Vue.js Style Guide - Priority C Rules: Recommended

## Good Single-File Component Structure - Vue HTML

Demonstrates the recommended structure for a Vue.js single-file component: `<script>`, `<template>`, then `<style>`. This ensures consistency and readability.

Source: https://github.com/vuejs/docs/blob/main/src/style-guide/rules-recommended.md#_snippet_5

```vue-html
<!-- ComponentA.vue -->
<script>/* ... */</script>
<template>...</template>
<style>/* ... */</style>

<!-- ComponentB.vue -->
<script>/* ... */</script>
<template>...</template>
<style>/* ... */</style>
```

```vue-html
<!-- ComponentA.vue -->
<template>...</template>
<script>/* ... */</script>
<style>/* ... */</style>

<!-- ComponentB.vue -->
<template>...</template>
<script>/* ... */</script>
<style>/* ... */</style>
```

---

## Component Props Definition without Empty Lines - Composition API - JavaScript

Demonstrates how to define component props using the Composition API in Vue.js without spaces. This example uses `defineProps` and `computed` to define properties and computed values.

Source: https://github.com/vuejs/docs/blob/main/src/style-guide/rules-recommended.md#_snippet_2

```javascript
defineProps({
  value: {
    type: String,
    required: true
  },
  focused: {
    type: Boolean,
    default: false
  },
  label: String,
  icon: String
})
const formattedValue = computed(() => {
  // ...
})
const inputClasses = computed(() => {
  // ...
})
```

---

## Bad Single-File Component Structure - Vue HTML

Illustrates a non-recommended structure for a Vue.js single-file component, where `<style>` is placed before `<script>` and/or `<template>`. This is inconsistent and not recommended.

Source: https://github.com/vuejs/docs/blob/main/src/style-guide/rules-recommended.md#_snippet_4

```vue-html
<style>/* ... */</style>
<script>/* ... */</script>
<template>...</template>
```

```vue-html
<!-- ComponentA.vue -->
<script>/* ... */</script>
<template>...</template>
<style>/* ... */</style>

<!-- ComponentB.vue -->
<template>...</template>
<script>/* ... */</script>
<style>/* ... */</style>
```

