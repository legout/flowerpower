# Vue.js Watchers Documentation

## Sync Watcher (Options API) - JavaScript

This code snippet creates a synchronous watcher using the Options API. The `flush: 'sync'` option makes the callback execute immediately after the reactive state changes, before any Vue-managed updates occur.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/watchers.md#_snippet_20

```javascript
export default {
  // ...
  watch: {
    key: {
      handler() {},
      flush: 'sync'
    }
  }
}
```

---

## Watching Reactive Object Property (Vue.js)

This snippet demonstrates the correct way to watch a property of a reactive object using a getter function in Vue.js Composition API. It highlights that directly watching obj.count won't work and provides the correct approach using a getter.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/watchers.md#_snippet_5

```javascript
// instead, use a getter:
watch(
  () => obj.count,
  (count) => {
    console.log(`Count is: ${count}`)
  }
)
```

---

## Post-Flush Watcher (Options API) - JavaScript

This shows how to define a post-flush watcher in the Options API.  The `flush: 'post'` option ensures the callback is executed after the owner component's DOM has been updated.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/watchers.md#_snippet_18

```javascript
export default {
  // ...
  watch: {
    key: {
      handler() {},
      flush: 'post'
    }
  }
}
```

---

## Basic Watcher in Composition API (Vue.js)

This code snippet illustrates a basic watcher implementation in Vue.js using the Composition API. It imports 'ref' and 'watch' from 'vue', creates reactive variables for 'question', 'answer', and 'loading', and then uses 'watch' to monitor changes to the 'question' ref. When the question includes a question mark, it fetches data from an API and updates the 'answer' ref.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/watchers.md#_snippet_3

```javascript
<script setup>
import { ref, watch } from 'vue'

const question = ref('')
const answer = ref('Questions usually contain a question mark. ;-)')
const loading = ref(false)

// watch works directly on a ref
watch(question, async (newQuestion, oldQuestion) => {
  if (newQuestion.includes('?')) {
    loading.value = true
    answer.value = 'Thinking...'
    try {
      const res = await fetch('https://yesno.wtf/api')
      answer.value = (await res.json()).answer
    } catch (error) {
      answer.value = 'Error! Could not reach the API. ' + error
    } finally {
      loading.value = false
    }
  }
})
</script>

<template>
  <p>
    Ask a yes/no question:
    <input v-model="question" :disabled="loading" />
  </p>
  <p>{{ answer }}</p>
</template>
```

---

## Stopping a Watcher with $watch (Options API)

This snippet demonstrates how to stop a watcher created using the `$watch()` instance method in the Options API.  The `$watch()` method returns a function, `unwatch`, which when called, stops the watcher. This is primarily useful for cases where the watcher needs to be stopped before the component is unmounted. The watcher is defined on 'foo' and executes a callback function.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/watchers.md#_snippet_23

```javascript
const unwatch = this.$watch('foo', callback)

// ...when the watcher is no longer needed:
unwatch()
```

---

## Watching a Ref with watch() - JavaScript

This code demonstrates how to use the `watch` function in Vue.js to watch a ref called `todoId`. It fetches data from an API whenever the value of `todoId` changes.  The `immediate: true` option ensures the watcher runs immediately upon creation.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/watchers.md#_snippet_12

```javascript
const todoId = ref(1)
const data = ref(null)

watch(
  todoId,
  async () => {
    const response = await fetch(
      `https://jsonplaceholder.typicode.com/todos/${todoId.value}`
    )
    data.value = await response.json()
  },
  { immediate: true }
)
```

---

## Sync Watcher (Composition API) - JavaScript

This snippet demonstrates creating a synchronous watcher using the Composition API. `flush: 'sync'` triggers the callback synchronously. The example shows the `watchSyncEffect()` alias.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/watchers.md#_snippet_21

```javascript
watch(source, callback, {
  flush: 'sync'
})

watchEffect(callback, {
  flush: 'sync'
})

import { watchSyncEffect } from 'vue'

watchSyncEffect(() => {
  /* executed synchronously upon reactive data change */
})
```

---

## watch() with Side Effect Cleanup (Composition API) - JavaScript

This snippet demonstrates how to perform side effect cleanup within a `watch` callback using the Composition API.  It uses `AbortController` to cancel a stale `fetch` request when the watched `id` changes. `onWatcherCleanup` registers the abort function.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/watchers.md#_snippet_14

```javascript
import { watch, onWatcherCleanup } from 'vue'

watch(id, (newId) => {
  const controller = new AbortController()

  fetch(`/api/${newId}`, { signal: controller.signal }).then(() => {
    // callback logic
  })

  onWatcherCleanup(() => {
    // abort stale request
    controller.abort()
  })
})
```

---

## Deep Watcher in Composition API (Vue.js)

This code shows that calling `watch()` directly on a reactive object creates a deep watcher by default. It also demonstrates how to force a deep watch when using a getter function with the `deep: true` option.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/watchers.md#_snippet_7

```javascript
watch(
  () => state.someObject,
  (newValue, oldValue) => {
    // Note: `newValue` will be equal to `oldValue` here
    // *unless* state.someObject has been replaced
  },
  { deep: true }
)
```

---

## Imperative Watcher with $watch() - JavaScript

This example demonstrates creating a watcher imperatively using the `$watch()` instance method within a Vue component's `created` lifecycle hook. This is helpful for conditionally setting up watchers or responding to user interactions.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/watchers.md#_snippet_22

```javascript
export default {
  created() {
    this.$watch('question', (newQuestion) => {
      // ...
    })
  }
}
```

---

## Using watchEffect() - JavaScript

This example shows how to use `watchEffect()` to automatically track reactive dependencies. It performs the same data fetching operation as the previous example, but without explicitly specifying `todoId` as a source. The `watchEffect` function automatically tracks `todoId.value` as a dependency.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/watchers.md#_snippet_13

```javascript
watchEffect(async () => {
  const response = await fetch(
    `https://jsonplaceholder.typicode.com/todos/${todoId.value}`
  )
  data.value = await response.json()
})
```

---

## Eager Watcher in Composition API (Vue.js)

This code demonstrates how to create an eager watcher in Vue.js using the Composition API.  The `immediate: true` option ensures that the callback is executed immediately.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/watchers.md#_snippet_9

```javascript
watch(
  source,
  (newValue, oldValue) => {
    // executed immediately, then again when `source` changes
  },
  { immediate: true }
)
```

---

## Side Effect Cleanup with Callback Argument (Composition API) - JavaScript

This example demonstrates passing the cleanup function as the 3rd argument in `watch` and as the 1st argument in `watchEffect`.  This is an alternative approach compatible with older versions of Vue (before 3.5).

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/watchers.md#_snippet_16

```javascript
watch(id, (newId, oldId, onCleanup) => {
  // ...
  onCleanup(() => {
    // cleanup logic
  })
})

watchEffect((onCleanup) => {
  // ...
  onCleanup(() => {
    // cleanup logic
  })
})
```

---

## Eager Watcher in Options API (Vue.js)

This code shows how to create an eager watcher in Vue.js using the Options API. The `immediate: true` option ensures that the callback is executed immediately when the component is created.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/watchers.md#_snippet_8

```javascript
export default {
  // ...
  watch: {
    question: {
      handler(newQuestion) {
        // this will be run immediately on component creation.
      },
      // force eager callback execution
      immediate: true
    }
  }
  // ...
}
```

---

## Once Watcher in Composition API (Vue.js)

This code demonstrates creating a watcher that triggers only once using the Composition API in Vue.js with the `once: true` option.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/watchers.md#_snippet_11

```javascript
watch(
  source,
  (newValue, oldValue) => {
    // when `source` changes, triggers only once
  },
  { once: true }
)
```

