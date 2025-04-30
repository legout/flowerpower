# Vue.js List Rendering with v-for

## List Rendering with v-for in Vue

This code snippet demonstrates how to use the `v-for` directive in Vue.js to render a list of `<li>` elements based on the `todos` array.  The `key` attribute is bound to a unique `id` for each todo object to improve rendering performance and handle list updates efficiently.

Source: https://github.com/vuejs/docs/blob/main/src/tutorial/src/step-7/description.md#_snippet_0

```vue-html
<ul>
  <li v-for="todo in todos" :key="todo.id">
    {{ todo.text }}
  </li>
</ul>
```

---

## Updating List using filter() - Composition API

This JavaScript code demonstrates how to update a list in Vue.js Composition API by replacing the original array with a new filtered array. The `filter()` method is used to create the new array, and `todos` is assumed to be a `ref` object, hence the `.value` access.

Source: https://github.com/vuejs/docs/blob/main/src/tutorial/src/step-7/description.md#_snippet_3

```js
todos.value = todos.value.filter(/* ... */)
```

---

## Updating List using push() - Composition API

This JavaScript code demonstrates how to update a list in Vue.js Composition API by using the `push()` method to add a new item (`newTodo`) to the `todos` array.  `todos` is assumed to be a `ref` object, hence the `.value` access.

Source: https://github.com/vuejs/docs/blob/main/src/tutorial/src/step-7/description.md#_snippet_1

```js
todos.value.push(newTodo)
```

---

## Updating List using filter() - Options API

This JavaScript code demonstrates how to update a list in Vue.js Options API by replacing the original array with a new filtered array. The `filter()` method is used to create the new array, and `this.todos` assumes that `todos` is defined in the `data` property of the Vue component.

Source: https://github.com/vuejs/docs/blob/main/src/tutorial/src/step-7/description.md#_snippet_4

```js
this.todos = this.todos.filter(/* ... */)
```

---

## Updating List using push() - Options API

This JavaScript code demonstrates how to update a list in Vue.js Options API by using the `push()` method to add a new item (`newTodo`) to the `todos` array.  `this.todos` assumes that `todos` is defined in the `data` property of the Vue component.

Source: https://github.com/vuejs/docs/blob/main/src/tutorial/src/step-7/description.md#_snippet_2

```js
this.todos.push(newTodo)
```

