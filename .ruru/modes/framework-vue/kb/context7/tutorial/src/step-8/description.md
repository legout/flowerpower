# Vue.js Computed Properties in Todo List

## Computed property (Options API, SFC)

This JavaScript snippet demonstrates how to define a computed property `filteredTodos` within a Vue.js component using the Options API and single-file component (SFC) syntax. The `filteredTodos` property is expected to return a filtered list of todos based on the `hideCompleted` state.

Source: https://github.com/vuejs/docs/blob/main/src/tutorial/src/step-8/description.md#_snippet_1

```javascript
export default {
  // ...
  computed: {
    filteredTodos() {
      // return filtered todos based on `this.hideCompleted`
    }
  }
}
```

---

## Binding checkbox with v-model in Vue.js

This HTML snippet demonstrates binding a checkbox to a `done` property of a `todo` object within a `v-for` loop. When the checkbox is checked or unchecked, the corresponding `todo.done` property is updated reactively.

Source: https://github.com/vuejs/docs/blob/main/src/tutorial/src/step-8/description.md#_snippet_0

```vue-html
<li v-for="todo in todos">
  <input type="checkbox" v-model="todo.done">
  ...
</li>
```

---

## Use the filteredTodos in v-for

This diff snippet shows how to replace the original `todos` list with the computed `filteredTodos` property in the `v-for` directive. This will render only the todos that satisfy the filtering logic defined in the `filteredTodos` computed property.

Source: https://github.com/vuejs/docs/blob/main/src/tutorial/src/step-8/description.md#_snippet_5

```diff
- <li v-for="todo in todos">
+ <li v-for="todo in filteredTodos">
```

---

## Computed property (Composition API, SFC)

This JavaScript snippet demonstrates how to create a computed ref `filteredTodos` within a Vue.js component using the Composition API and single-file component (SFC) syntax. It uses `ref` to create reactive variables `hideCompleted` and `todos`, and `computed` to create `filteredTodos` which depends on these reactive values.

Source: https://github.com/vuejs/docs/blob/main/src/tutorial/src/step-8/description.md#_snippet_3

```javascript
import { ref, computed } from 'vue'

const hideCompleted = ref(false)
const todos = ref([
  /* ... */
])

const filteredTodos = computed(() => {
  // return filtered todos based on
  // `todos.value` & `hideCompleted.value`
})
```

