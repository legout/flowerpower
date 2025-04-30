# Vue Composables: Reusing Stateful Logic

## Simplified Mouse Tracking Composable JavaScript

This updated `useMouse` composable utilizes the `useEventListener` composable to manage the mousemove event listener. It imports both `ref` from Vue and `useEventListener` from './event'. It encapsulates the reactive state (x and y coordinates) and uses the `useEventListener` composable to handle the event listener lifecycle.  This showcases how composables can be nested for complex logic reuse.

Source: https://github.com/vuejs/docs/blob/main/src/guide/reusability/composables.md#_snippet_4

```javascript
// mouse.js
import { ref } from 'vue'
import { useEventListener } from './event'

export function useMouse() {
  const x = ref(0)
  const y = ref(0)

  useEventListener(window, 'mousemove', (event) => {
    x.value = event.pageX
    y.value = event.pageY
  })

  return { x, y }
}
```

---

## Event Listener Composable JavaScript

This JavaScript code defines a `useEventListener` composable that simplifies adding and removing event listeners on a specified target. It takes the target element, event type, and callback function as arguments. It uses `onMounted` and `onUnmounted` to manage the event listener's lifecycle, ensuring it's added when the component is mounted and removed when unmounted.

Source: https://github.com/vuejs/docs/blob/main/src/guide/reusability/composables.md#_snippet_3

```javascript
// event.js
import { onMounted, onUnmounted } from 'vue'

export function useEventListener(target, event, callback) {
  // if you want, you can also make this
  // support selector strings as target
  onMounted(() => target.addEventListener(event, callback))
  onUnmounted(() => target.removeEventListener(event, callback))
}
```

---

## Async Data Fetching Component Vue

This Vue component demonstrates basic asynchronous data fetching using `fetch`. It utilizes `ref` to manage the data and error states. The template conditionally renders a loading message, the fetched data, or an error message based on the current state.  This is a basic pattern for fetching data within a Vue component.

Source: https://github.com/vuejs/docs/blob/main/src/guide/reusability/composables.md#_snippet_5

```vue
<script setup>
import { ref } from 'vue'

const data = ref(null)
const error = ref(null)

fetch('...')
  .then((res) => res.json())
  .then((json) => (data.value = json))
  .catch((err) => (error.value = err))
</script>

<template>
  <div v-if="error">Oops! Error encountered: {{ error.message }}</div>
  <div v-else-if="data">
    Data loaded:
    <pre>{{ data }}</pre>
  </div>
  <div v-else>Loading...</div>
</template>
```

---

## Reactive Data Fetching with useFetch Composable in Vue.js

This `useFetch` composable function demonstrates fetching data using a URL that can be a static string, a ref, or a getter function. It leverages `watchEffect` to react to changes in the URL, and `toValue` to normalize the URL argument. The composable returns reactive `data` and `error` refs.

Source: https://github.com/vuejs/docs/blob/main/src/guide/reusability/composables.md#_snippet_10

```javascript
// fetch.js
import { ref, watchEffect, toValue } from 'vue'

export function useFetch(url) {
  const data = ref(null)
  const error = ref(null)

  const fetchData = () => {
    // reset state before fetching..
    data.value = null
    error.value = null

    fetch(toValue(url))
      .then((res) => res.json())
      .then((json) => (data.value = json))
      .catch((err) => (error.value = err))
  }

  watchEffect(() => {
    fetchData()
  })

  return { data, error }
}
```

---

## Destructuring Refs from Composables in Vue.js

This example shows how to correctly destructure refs returned from a composable while maintaining reactivity. Composables should return plain objects containing refs to allow destructuring without losing the reactivity connection to the internal state of the composable.

Source: https://github.com/vuejs/docs/blob/main/src/guide/reusability/composables.md#_snippet_12

```javascript
// x and y are refs
const { x, y } = useMouse()
```

---

## Using Data Fetching Composable Vue

This Vue component demonstrates how to use the `useFetch` composable to fetch and display data. It imports the `useFetch` composable, calls it with a URL, and destructures the returned `data` and `error` refs. The template then utilizes these reactive values to display the fetched data or an error message.

Source: https://github.com/vuejs/docs/blob/main/src/guide/reusability/composables.md#_snippet_7

```vue
<script setup>
import { useFetch } from './fetch.js'

const { data, error } = useFetch('...')
</script>
```

---

## Using Reactive Wrapper for Composables in Vue.js

This code demonstrates how to use `reactive()` to wrap the return value of a composable function, allowing access to the returned state as object properties while maintaining reactivity. This approach unwraps the refs so they can be accessed directly.

Source: https://github.com/vuejs/docs/blob/main/src/guide/reusability/composables.md#_snippet_13

```javascript
const mouse = reactive(useMouse())
// mouse.x is linked to original ref
console.log(mouse.x)
```

---

## Mouse Tracking Component (Direct Implementation) Vue

This Vue component demonstrates mouse tracking functionality using the Composition API directly within the component. It uses `ref` to create reactive state for the x and y coordinates of the mouse, and `onMounted` and `onUnmounted` lifecycle hooks to add and remove the mousemove event listener. The template displays the current mouse position.

Source: https://github.com/vuejs/docs/blob/main/src/guide/reusability/composables.md#_snippet_0

```vue
<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const x = ref(0)
const y = ref(0)

function update(event) {
  x.value = event.pageX
  y.value = event.pageY
}

onMounted(() => window.addEventListener('mousemove', update))
onUnmounted(() => window.removeEventListener('mousemove', update))
</script>

<template>Mouse position is at: {{ x }}, {{ y }}</template>
```

---

## Mouse Tracking Composable JavaScript

This JavaScript file defines a `useMouse` composable function that tracks the mouse position using Vue's Composition API. It uses `ref` to create reactive state for the x and y coordinates and `onMounted` and `onUnmounted` to manage the mousemove event listener. The composable returns the x and y coordinates as a reactive object.

Source: https://github.com/vuejs/docs/blob/main/src/guide/reusability/composables.md#_snippet_1

```javascript
// mouse.js
import { ref, onMounted, onUnmounted } from 'vue'

// by convention, composable function names start with "use"
export function useMouse() {
  // state encapsulated and managed by the composable
  const x = ref(0)
  const y = ref(0)

  // a composable can update its managed state over time.
  function update(event) {
    x.value = event.pageX
    y.value = event.pageY
  }

  // a composable can also hook into its owner component's
  // lifecycle to setup and teardown side effects.
  onMounted(() => window.addEventListener('mousemove', update))
onUnmounted(() => window.removeEventListener('mousemove', update))

  // expose managed state as return value
  return { x, y }
}
```

---

## Using Mouse Tracking Composable Vue

This Vue component utilizes the `useMouse` composable function to track and display the mouse position. It imports the composable and destructures the returned reactive values (x and y) to be used in the template.  This demonstrates how to consume the stateful logic encapsulated within the `useMouse` composable.

Source: https://github.com/vuejs/docs/blob/main/src/guide/reusability/composables.md#_snippet_2

```vue
<script setup>
import { useMouse } from './mouse.js'

const { x, y } = useMouse()
</script>

<template>Mouse position is at: {{ x }}, {{ y }}</template>
```

---

## Using Composables with Options API in Vue.js

This example shows how to use composables within a Vue.js component that uses the Options API. Composables must be called inside the `setup()` function, and the returned values must be returned from `setup()` to be accessible in the component's template and `this` context.

Source: https://github.com/vuejs/docs/blob/main/src/guide/reusability/composables.md#_snippet_16

```javascript
import { useMouse } from './mouse.js'
import { useFetch } from './fetch.js'

export default {
  setup() {
    const { x, y } = useMouse()
    const { data, error } = useFetch('...')
    return { x, y, data, error }
  },
  mounted() {
    // setup() exposed properties can be accessed on `this`
    console.log(this.x)
  }
  // ...other options
}
```

---

## Data Fetching Composable JavaScript

This JavaScript code defines a `useFetch` composable that encapsulates the logic for fetching data asynchronously. It takes a URL as an argument and uses `ref` to create reactive states for data and error. It uses the `fetch` API to make a request, parses the JSON response, and updates the data or error ref accordingly. It returns an object containing the `data` and `error` refs.

Source: https://github.com/vuejs/docs/blob/main/src/guide/reusability/composables.md#_snippet_6

```javascript
// fetch.js
import { ref } from 'vue'

export function useFetch(url) {
  const data = ref(null)
  const error = ref(null)

  fetch(url)
    .then((res) => res.json())
    .then((json) => (data.value = json))
    .catch((err) => (error.value = err))

  return { data, error }
}
```

---

## Fetching Data with Reactive URL (Ref) in Vue.js

This example demonstrates how to use a ref as the URL in a `useFetch()` composable.  When the ref's value changes, the `useFetch` function will automatically re-fetch the data. This enables reactive data fetching based on external changes.

Source: https://github.com/vuejs/docs/blob/main/src/guide/reusability/composables.md#_snippet_8

```javascript
const url = ref('/initial-url')

const { data, error } = useFetch(url)

// this should trigger a re-fetch
url.value = '/new-url'
```

---

## Organizing Component Logic with Composables in Vue.js

This example illustrates how to organize component logic by extracting and using multiple composables within a Vue.js component. It shows how composables can be imported and used in `<script setup>`, allowing for better code organization and modularity.

Source: https://github.com/vuejs/docs/blob/main/src/guide/reusability/composables.md#_snippet_15

```javascript
<script setup>
import { useFeatureA } from './featureA.js'
import { useFeatureB } from './featureB.js'
import { useFeatureC } from './featureC.js'

const { foo, bar } = useFeatureA()
const { baz } = useFeatureB(foo)
const { qux } = useFeatureC(baz)
</script>
```

---

## Fetching Data with Reactive URL (Getter) in Vue.js

This example demonstrates how to use a getter function to dynamically determine the URL in a `useFetch()` composable. When the value returned by the getter function changes (e.g., due to a change in `props.id`), the `useFetch` function will automatically re-fetch the data. This allows reactive data fetching based on computed values.

Source: https://github.com/vuejs/docs/blob/main/src/guide/reusability/composables.md#_snippet_9

```javascript
// re-fetch when props.id changes
const { data, error } = useFetch(() => `/posts/${props.id}`)
```

---

## Normalizing Values with toValue in Vue.js Composables

This code snippet illustrates the use of `toValue()` within a composable function to normalize input arguments. `toValue()` converts refs and getters into their corresponding values, ensuring consistent handling of different input types. This approach promotes flexibility and allows composables to accept various forms of input data.

Source: https://github.com/vuejs/docs/blob/main/src/guide/reusability/composables.md#_snippet_11

```javascript
import { toValue } from 'vue'

function useFeature(maybeRefOrGetter) {
  // If maybeRefOrGetter is a ref or a getter,
  // its normalized value will be returned.
  // Otherwise, it is returned as-is.
  const value = toValue(maybeRefOrGetter)
}
```

