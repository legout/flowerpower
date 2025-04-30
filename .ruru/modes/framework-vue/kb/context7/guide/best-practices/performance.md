# Vue.js Performance Optimization Guide

## Optimized Computed Property with Manual Comparison

Illustrates how to optimize a computed property by manually comparing the new value with the old value and conditionally returning the old value if nothing has changed. This prevents unnecessary effect triggers.

Source: https://github.com/vuejs/docs/blob/main/src/guide/best-practices/performance.md#_snippet_6

```javascript
const computedObj = computed((oldValue) => {
  const newValue = {
    isEven: count.value % 2 === 0
  }
  if (oldValue && oldValue.isEven === newValue.isEven) {
    return oldValue
  }
  return newValue
})
```

---

## Async Component Definition in Vue.js

This JavaScript snippet showcases how to define an asynchronous component in Vue.js using `defineAsyncComponent`.  The component is loaded only when it's rendered on the page, enabling code splitting and reducing initial load time.  `Foo.vue` and its dependencies are created as a separate chunk.

Source: https://github.com/vuejs/docs/blob/main/src/guide/best-practices/performance.md#_snippet_1

```javascript
import { defineAsyncComponent } from 'vue'

// a separate chunk is created for Foo.vue and its dependencies.
// it is only fetched on demand when the async component is
// rendered on the page.
const Foo = defineAsyncComponent(() => import('./Foo.vue'))
```

---

## Efficient List Rendering in Vue.js (Props Stability)

This Vue.js template snippet shows an optimized way to render a list.  Each `ListItem` only updates when its own `active` prop changes, reducing unnecessary re-renders.  The active state is pre-calculated in the parent component and passed as a direct prop.  The active state depends on a boolean expression.

Source: https://github.com/vuejs/docs/blob/main/src/guide/best-practices/performance.md#_snippet_3

```vue-html
<ListItem
  v-for="item in list"
  :id="item.id"
  :active="item.id === activeId" />
```

---

## Reducing Reactivity Overhead with shallowRef

Demonstrates how to use `shallowRef()` to opt-out of deep reactivity for large immutable structures. Updates to nested properties won't trigger reactivity unless the root state is replaced.

Source: https://github.com/vuejs/docs/blob/main/src/guide/best-practices/performance.md#_snippet_7

```javascript
const shallowArray = shallowRef([
  /* big list of deep objects */
])

// this won't trigger updates...
shallowArray.value.push(newObject)
// this does:
shallowArray.value = [...shallowArray.value, newObject]

// this won't trigger updates...
shallowArray.value[0].foo = 1
// this does:
shallowArray.value = [
  {
    ...shallowArray.value[0],
    foo: 1
  },
  ...shallowArray.value.slice(1)
]
```

---

## Inefficient Computed Property with New Object Creation

Shows a scenario where a computed property creates a new object on each compute, leading to unnecessary effect triggers because Vue.js considers the new value always different from the old one.

Source: https://github.com/vuejs/docs/blob/main/src/guide/best-practices/performance.md#_snippet_5

```javascript
const computedObj = computed(() => {
  return {
    isEven: count.value % 2 === 0
  }
})
```

---

## Computed Property Stability Example in Vue.js

Demonstrates how a computed property in Vue.js 3.4+ triggers effects only when its computed value changes. The example uses a ref to track a count and a computed property to determine if the count is even.

Source: https://github.com/vuejs/docs/blob/main/src/guide/best-practices/performance.md#_snippet_4

```javascript
const count = ref(0)
const isEven = computed(() => count.value % 2 === 0)

watchEffect(() => console.log(isEven.value)) // true

// will not trigger new logs because the computed value stays `true`
count.value = 2
count.value = 4
```

---

## Inefficient List Rendering in Vue.js (Props Stability)

This Vue.js template snippet demonstrates an inefficient way to render a list.  Every `ListItem` updates whenever `activeId` changes, even if the `item.id` is not equal to `activeId`. This leads to unnecessary re-renders.  The list items depend on the ID and the active ID.

Source: https://github.com/vuejs/docs/blob/main/src/guide/best-practices/performance.md#_snippet_2

```vue-html
<ListItem
  v-for="item in list"
  :id="item.id"
  :active-id="activeId" />
```

