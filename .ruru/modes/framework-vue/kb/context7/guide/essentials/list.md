# Vue.js List Rendering with v-for

## v-for on Component

Illustrates how to use the `v-for` directive directly on a Vue component. This example shows how to iterate over an array of items and render a component for each item, ensuring each component has a unique key.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/list.md#_snippet_21

```vue-html
<MyComponent v-for="item in items" :key="item.id" />
```

---

## Initializing Array with Composition API in Vue

This code snippet demonstrates how to initialize an array of objects using the Composition API in Vue. It uses the `ref` function to create a reactive reference to the array.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/list.md#_snippet_0

```javascript
const items = ref([{ message: 'Foo' }, { message: 'Bar' }])
```

---

## v-for with Props

Demonstrates how to pass data to a component when using `v-for`. The `item` and `index` from the loop are passed as props to the `MyComponent`, making the data accessible within the component's scope.  The key prop is essential for Vue's reactivity system to track changes efficiently.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/list.md#_snippet_22

```vue-html
<MyComponent
  v-for="(item, index) in items"
  :item="item"
  :index="index"
  :key="item.id"
/>
```

---

## Rendering List with Index and Parent Message in Vue

This snippet uses `v-for` to iterate over an array and display a message that includes the parent message, the index of the item, and the item's message. This demonstrates accessing variables from both the parent scope and the current iteration.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/list.md#_snippet_5

```html
<li v-for="(item, index) in items">
  {{ parentMessage }} - {{ index }} - {{ item.message }}
</li>
```

---

## Method for Filtering (Composition API)

Shows how to use a method to filter an array in Vue.js using the Composition API. The `even` method filters an array of numbers and returns a new array containing only the even numbers. This is useful in situations where computed properties are not feasible, such as inside nested `v-for` loops.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/list.md#_snippet_28

```javascript
const sets = ref([
  [1, 2, 3, 4, 5],
  [6, 7, 8, 9, 10]
])

function even(numbers) {
  return numbers.filter((number) => number % 2 === 0)
}
```

---

## Replacing Array (Composition API)

Shows how to replace an array in Vue.js using the Composition API. The example filters an array of items and assigns the new, filtered array to the `items.value` ref. This approach ensures that Vue's reactivity system detects the change and updates the DOM accordingly.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/list.md#_snippet_23

```javascript
// `items` is a ref with array value
items.value = items.value.filter((item) => item.message.match(/Foo/))
```

---

## Initializing Object with Options API in Vue

This code snippet shows how to initialize an object in the `data` option when using the Options API in Vue.  This makes the object available to the Vue component.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/list.md#_snippet_11

```javascript
data() {
  return {
    myObject: {
      title: 'How to do lists in Vue',
      author: 'Jane Doe',
      publishedAt: '2016-04-10'
    }
  }
}
```

---

## Rendering List with v-for in Vue Template

This code snippet shows how to use the `v-for` directive in a Vue template to render a list of items. It iterates over the `items` array and displays the `message` property of each item within an `<li>` element.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/list.md#_snippet_2

```html
<li v-for="item in items">
  {{ item.message }}
</li>
```

---

## Maintaining State with Key Attribute in v-for

This code demonstrates how to use the `key` attribute with `v-for` to help Vue track each node's identity, enabling reuse and reordering of existing elements for efficient updates.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/list.md#_snippet_19

```html
<div v-for="item in items" :key="item.id">
  <!-- content -->
</div>
```

---

## Replacing Array (Options API)

Demonstrates how to replace an array in Vue.js using the Options API. The example filters an array of items and assigns the new, filtered array to `this.items`.  Vue intelligently re-renders only the changed elements, making this an efficient operation.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/list.md#_snippet_24

```javascript
this.items = this.items.filter((item) => item.message.match(/Foo/))
```

---

## Computed Property for Filtering (Options API)

Demonstrates how to use a computed property to filter an array in Vue.js using the Options API. The `evenNumbers` computed property returns a new array containing only the even numbers from the `numbers` data property. This maintains the immutability of the original array.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/list.md#_snippet_26

```javascript
data() {
  return {
    numbers: [1, 2, 3, 4, 5]
  }
},
computed: {
  evenNumbers() {
    return this.numbers.filter(n => n % 2 === 0)
  }
}
```

---

## Initializing Object with Composition API in Vue

This code snippet shows how to initialize a reactive object using the Composition API in Vue. The `reactive` function makes the object's properties reactive, so changes to them will trigger updates in the UI.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/list.md#_snippet_10

```javascript
const myObject = reactive({
  title: 'How to do lists in Vue',
  author: 'Jane Doe',
  publishedAt: '2016-04-10'
})
```

---

## JavaScript Equivalent of v-for Scoping

This JavaScript snippet demonstrates the variable scoping behavior of `v-for` using the `forEach` method. It shows how the callback function has access to the outer scope variables but its own parameters (`item` and `index`) are only available within the callback.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/list.md#_snippet_6

```javascript
const parentMessage = 'Parent'
const items = [
  /* ... */
]

items.forEach((item, index) => {
  // has access to outer scope `parentMessage`
  // but `item` and `index` are only available in here
  console.log(parentMessage, item.message, index)
})
```

---

## v-if and v-for with <template> (Correct)

This code snippet shows the correct usage of `v-if` and `v-for` by placing the `v-for` on a wrapping `<template>` tag. This allows the `v-if` condition to access variables from the `v-for` scope.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/list.md#_snippet_18

```html
<template v-for="todo in todos">
  <li v-if="!todo.isComplete">
    {{ todo.name }}
  </li>
</template>
```

---

## Method for Filtering (Options API)

Demonstrates how to use a method to filter an array in Vue.js using the Options API. The `even` method filters an array of numbers and returns a new array containing only the even numbers. This is useful when computed properties are not suitable, for instance, within nested `v-for` loops.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/list.md#_snippet_29

```javascript
data() {
  return {
    sets: [[ 1, 2, 3, 4, 5 ], [6, 7, 8, 9, 10]]
  }
},
methods: {
  even(numbers) {
    return numbers.filter(number => number % 2 === 0)
  }
}
```

---

## Iterating Through Object with Key and Value in Vue

This demonstrates iterating through an object's properties with `v-for`, accessing both the value and the key of each property.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/list.md#_snippet_13

```html
<li v-for="(value, key) in myObject">
  {{ key }}: {{ value }}
</li>
```

---

## Accessing Parent Scope and Index in v-for (Options API)

This code snippet initializes a parent message and an array of items using the Options API, providing data for rendering within a v-for loop that accesses both the item and its index.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/list.md#_snippet_4

```javascript
data() {
  return {
    parentMessage: 'Parent',
    items: [{ message: 'Foo' }, { message: 'Bar' }]
  }
}
```

---

## Rendering a Range with v-for in Vue

This snippet shows how to use `v-for` to render a range of numbers. It iterates from 1 to 10 (inclusive) and displays each number within a `<span>` element.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/list.md#_snippet_15

```html
<span v-for="n in 10">{{ n }}</span>
```

---

## v-for with 'of' Delimiter in Vue Template

This code snippet demonstrates using `of` as the delimiter in the `v-for` directive, providing a syntax closer to JavaScript iterators.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/list.md#_snippet_9

```html
<div v-for="item of items"></div>
```

---

## v-if and v-for on the Same Element (Incorrect)

This code snippet shows the incorrect usage of `v-if` and `v-for` on the same element.  The `v-if` condition cannot access variables from the `v-for` scope directly.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/list.md#_snippet_17

```html
<!--
This will throw an error because property "todo"
is not defined on instance.
-->
<li v-for="todo in todos" v-if="!todo.isComplete">
  {{ todo.name }}
</li>
```

---

## Iterating Through Object Properties with v-for in Vue

This demonstrates iterating through the properties (values) of an object using `v-for`. The `value` alias represents the value of each property.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/list.md#_snippet_12

```html
<ul>
  <li v-for="value in myObject">
    {{ value }}
  </li>
</ul>
```

---

## Accessing Parent Scope and Index in v-for (Composition API)

This code snippet initializes a parent message and an array of items using the Composition API, preparing them for rendering within a v-for loop that accesses both the item and its index.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/list.md#_snippet_3

```javascript
const parentMessage = ref('Parent')
const items = ref([{ message: 'Foo' }, { message: 'Bar' }])
```

