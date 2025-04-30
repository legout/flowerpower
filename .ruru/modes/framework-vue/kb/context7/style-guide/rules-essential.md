# Vue.js Style Guide - Priority A Rules

## Use component-scoped styling - Good Example 1 - HTML/CSS (Scoped Attribute)

Demonstrates the correct way of styling components using the `scoped` attribute in Single-File Components. This ensures that the styles only apply to the current component, preventing style conflicts.

Source: https://github.com/vuejs/docs/blob/main/src/style-guide/rules-essential.md#_snippet_16

```vue-html
<template>
  <button class="button button-close">×</button>
</template>

<!-- Using the `scoped` attribute -->
<style scoped>
.button {
  border: none;
  border-radius: 2px;
}

.button-close {
  background-color: red;
}
</style>
```

---

## Use component-scoped styling - Good Example 3 - HTML/CSS (BEM)

Demonstrates the correct way of styling components using the BEM convention in Single-File Components. This provides human-readable class names that are unlikely to conflict.

Source: https://github.com/vuejs/docs/blob/main/src/style-guide/rules-essential.md#_snippet_18

```vue-html
<template>
  <button class="c-Button c-Button--close">×</button>
</template>

<!-- Using the BEM convention -->
<style>
.c-Button {
  border: none;
  border-radius: 2px;
}

.c-Button--close {
  background-color: red;
}
</style>
```

---

## Use keyed v-for - Good Example - HTML

Demonstrates the correct way of using `v-for` with a `key` attribute, ensuring predictable behavior and optimal performance when the list changes. The key should be unique for each item in the list.

Source: https://github.com/vuejs/docs/blob/main/src/style-guide/rules-essential.md#_snippet_9

```vue-html
<ul>
  <li
    v-for="todo in todos"
    :key="todo.id"
  >
    {{ todo.text }}
  </li>
</ul>
```

---

## Computed Property Example - Options API - Javascript

Illustrates the use of a computed property in the Options API to filter a list of users based on their active status. This is a good practice to avoid using `v-if` with `v-for` directly on the element.

Source: https://github.com/vuejs/docs/blob/main/src/style-guide/rules-essential.md#_snippet_11

```javascript
computed: {
  activeUsers() {
    return this.users.filter(user => user.isActive)
  }
}
```

---

## Computed Property Example - Composition API - Javascript

Illustrates the use of a computed property in the Composition API to filter a list of users based on their active status. This is a good practice to avoid using `v-if` with `v-for` directly on the element.

Source: https://github.com/vuejs/docs/blob/main/src/style-guide/rules-essential.md#_snippet_12

```javascript
const activeUsers = computed(() => {
  return users.filter((user) => user.isActive)
})
```

---

## Use component-scoped styling - Good Example 2 - HTML/CSS (CSS Modules)

Demonstrates the correct way of styling components using CSS Modules in Single-File Components. This uses unique class names for each component and avoids style conflicts.

Source: https://github.com/vuejs/docs/blob/main/src/style-guide/rules-essential.md#_snippet_17

```vue-html
<template>
  <button :class="[$style.button, $style.buttonClose]">×</button>
</template>

<!-- Using CSS modules -->
<style module>
.button {
  border: none;
  border-radius: 2px;
}

.buttonClose {
  background-color: red;
}
</style>
```

---

## Data Example - Composition API - Javascript

Illustrates a data structure using ref representing a list of todos, used to exemplify the importance of using keys in v-for directives. This snippet is provided for context in Composition API.

Source: https://github.com/vuejs/docs/blob/main/src/style-guide/rules-essential.md#_snippet_7

```javascript
const todos = ref([
  {
    id: 1,
    text: 'Learn to use v-for'
  },
  {
    id: 2,
    text: 'Learn to use key'
  }
])
```

---

## Use detailed prop definitions - Good Example - Javascript - Composition API

Demonstrates a good practice of defining props with detailed configurations using the Composition API. It includes type validation and a custom validator to ensure prop values are correct.

Source: https://github.com/vuejs/docs/blob/main/src/style-guide/rules-essential.md#_snippet_5

```javascript
const props = defineProps({
  status: String
})
```

```javascript
// Even better!

const props = defineProps({
  status: {
    type: String,
    required: true,

    validator: (value) => {
      return ['syncing', 'synced', 'version-conflict', 'error'].includes(
        value
      )
    }
  }
})
```

---

## Avoid v-if with v-for - Good Example 2 - HTML

Demonstrates an alternative correct way of using a `template` tag with `v-for` to wrap the element with the conditional rendering using `v-if`. This prevents the error of evaluating `v-if` before `v-for`.

Source: https://github.com/vuejs/docs/blob/main/src/style-guide/rules-essential.md#_snippet_14

```vue-html
<ul>
  <template v-for="user in users" :key="user.id">
    <li v-if="user.isActive">
      {{ user.name }}
    </li>
  </template>
</ul>
```

---

## Use detailed prop definitions - Good Example - Javascript - Options API

Demonstrates a good practice of defining props with detailed configurations in the Options API. It includes type validation and a custom validator to ensure prop values are correct.

Source: https://github.com/vuejs/docs/blob/main/src/style-guide/rules-essential.md#_snippet_3

```javascript
props: {
  status: String
}
```

```javascript
// Even better!
props: {
  status: {
    type: String,
    required: true,

    validator: value => {
      return [
        'syncing',
        'synced',
        'version-conflict',
        'error'
      ].includes(value)
    }
  }
}
```

