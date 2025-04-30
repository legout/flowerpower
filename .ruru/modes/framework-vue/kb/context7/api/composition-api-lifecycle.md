# Vue.js Composition API Lifecycle Hooks

## Using onUnmounted to clear interval

This example demonstrates the usage of the `onUnmounted` lifecycle hook to clear an interval. This is important for cleaning up side effects and preventing memory leaks. It imports `onMounted` and `onUnmounted` from 'vue', sets up an interval in `onMounted`, and clears the interval in `onUnmounted`.

Source: https://github.com/vuejs/docs/blob/main/src/api/composition-api-lifecycle.md#_snippet_2

```vue
<script setup>
import { onMounted, onUnmounted } from 'vue'

let intervalId
onMounted(() => {
  intervalId = setInterval(() => {
    // ...
  })
})

onUnmounted(() => clearInterval(intervalId))
</script>
```

---

## Using onUpdated to access updated DOM

This example demonstrates the usage of the `onUpdated` lifecycle hook to access and log the updated DOM content. The `onUpdated` hook is called after the component's DOM has been updated due to reactive state changes. It imports `ref` and `onUpdated` from 'vue', defines a reactive `count`, and logs the text content of an element with the id 'count' within the `onUpdated` callback.

Source: https://github.com/vuejs/docs/blob/main/src/api/composition-api-lifecycle.md#_snippet_1

```vue
<script setup>
import { ref, onUpdated } from 'vue'

const count = ref(0)

onUpdated(() => {
  // text content should be the same as current `count.value`
  console.log(document.getElementById('count').textContent)
})
</script>

<template>
  <button id="count" @click="count++">{{ count }}</button>
</template>
```

---

## Using onMounted to access template ref

This example demonstrates how to use the `onMounted` lifecycle hook to access a DOM element using a template ref. The `onMounted` hook ensures that the DOM is available before accessing the element. It imports `ref` and `onMounted` from 'vue', defines a ref called `el`, and accesses its value within the `onMounted` callback.

Source: https://github.com/vuejs/docs/blob/main/src/api/composition-api-lifecycle.md#_snippet_0

```vue
<script setup>
import { ref, onMounted } from 'vue'

const el = ref()

onMounted(() => {
  el.value // <div>
})
</script>

<template>
  <div ref="el"></div>
</template>
```

---

## Vue onServerPrefetch() Example

Demonstrates the usage of onServerPrefetch within a Vue component. It fetches data on the server using `fetchOnServer` and assigns it to a ref. If the component is dynamically rendered on the client, it fetches data using `fetchOnClient` in the `onMounted` hook.

Source: https://github.com/vuejs/docs/blob/main/src/api/composition-api-lifecycle.md#_snippet_4

```vue
<script setup>
import { ref, onServerPrefetch, onMounted } from 'vue'

const data = ref(null)

onServerPrefetch(async () => {
  // component is rendered as part of the initial request
  // pre-fetch data on server as it is faster than on the client
  data.value = await fetchOnServer(/* ... */)
})

onMounted(async () => {
  if (!data.value) {
    // if data is null on mount, it means the component
    // is dynamically rendered on the client. Perform a
    // client-side fetch instead.
    data.value = await fetchOnClient(/* ... */)
  }
})
</script>
```

