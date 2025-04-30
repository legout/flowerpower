# Vue.js Reactivity API: Core

## Creating a Reactive Object with reactive() in Vue.js

Creates a reactive proxy of the object using the `reactive()` function. The conversion is deep, affecting all nested properties and unwrapping refs while maintaining reactivity. It's recommended to work exclusively with the reactive proxy.

Source: https://github.com/vuejs/docs/blob/main/src/api/reactivity-core.md#_snippet_4

```javascript
const obj = reactive({ count: 0 })
obj.count++
```

---

## Watch with Side Effect Cleanup (Vue 3.5+) - JavaScript

Shows how to use `onWatcherCleanup` to register a cleanup function in Vue 3.5+. This function is called when the watcher is about to re-run, allowing for cleanup of previous side effects.

Source: https://github.com/vuejs/docs/blob/main/src/api/reactivity-core.md#_snippet_25

```javascript
import { onWatcherCleanup } from 'vue'

watch(id, async (newId) => {
  const { response, cancel } = doAsyncWork(newId)
  onWatcherCleanup(cancel)
  data.value = await response
})
```

---

## Creating a Watcher with watchEffect() in Vue.js

Creates a watcher that immediately runs a function while reactively tracking its dependencies. It re-runs the function whenever the dependencies are changed, by default, watchers run just prior to component rendering.

Source: https://github.com/vuejs/docs/blob/main/src/api/reactivity-core.md#_snippet_9

```javascript
const count = ref(0)

watchEffect(() => console.log(count.value))
// -> logs 0

count.value++
// -> logs 1
```

---

## Creating a Writable Computed Ref in Vue.js

Shows how to create a writable computed ref using the `computed()` function with a `get` and `set` object. This allows modifying the computed value, which in turn updates the underlying reactive value.

Source: https://github.com/vuejs/docs/blob/main/src/api/reactivity-core.md#_snippet_2

```javascript
const count = ref(1)
const plusOne = computed({
  get: () => count.value + 1,
  set: (val) => {
    count.value = val - 1
  }
})

plusOne.value = 1
console.log(count.value) // 0
```

---

## Watch Ref Example - JavaScript

Shows how to use the `watch` function in Vue.js to watch a ref. The callback function will be executed when the ref's value changes, providing the new and previous values.

Source: https://github.com/vuejs/docs/blob/main/src/api/reactivity-core.md#_snippet_17

```javascript
const count = ref(0)
watch(count, (count, prevCount) => {
  /* ... */
})
```

---

## Creating a Read-Only Computed Ref in Vue.js

Demonstrates how to create a read-only computed ref using the `computed()` function, which takes a getter function and returns a readonly reactive ref object. Attempts to modify the value of a read-only computed ref will result in an error.

Source: https://github.com/vuejs/docs/blob/main/src/api/reactivity-core.md#_snippet_1

```javascript
const count = ref(1)
const plusOne = computed(() => count.value + 1)

console.log(plusOne.value) // 2

plusOne.value++ // error
```

---

## Creating a Reactive Ref with ref() in Vue.js

Creates a reactive and mutable ref object with a single property `.value` that points to the inner value. Any read operations to `.value` are tracked, and write operations trigger associated effects.

Source: https://github.com/vuejs/docs/blob/main/src/api/reactivity-core.md#_snippet_0

```javascript
const count = ref(0)
console.log(count.value) // 0

count.value = 1
console.log(count.value) // 1
```

---

## Watch Getter Example - JavaScript

Demonstrates how to use the `watch` function in Vue.js to watch a getter function that accesses a reactive state. The callback function will be executed when the value returned by the getter changes.

Source: https://github.com/vuejs/docs/blob/main/src/api/reactivity-core.md#_snippet_16

```javascript
const state = reactive({ count: 0 })
watch(
  () => state.count,
  (count, prevCount) => {
    /* ... */
  }
)
```

---

## Watch Reactive Object with Deep Option - JavaScript

Demonstrates how to force deep traversal of the source if it is an object, so that the callback fires on deep mutations. When watching a reactive object with the `deep` option set to `true`, the watcher will trigger even when nested properties change.  If the callback was triggered by a deep mutation, the new and old values will be the same object.

Source: https://github.com/vuejs/docs/blob/main/src/api/reactivity-core.md#_snippet_19

```javascript
const state = reactive({ count: 0 })
watch(
  () => state,
  (newValue, oldValue) => {
    // newValue === oldValue
  },
  { deep: true }
)
```

---

## Ref Unwrapping with reactive() in Vue.js

Demonstrates how refs are automatically unwrapped when accessed as properties of a reactive object created with `reactive()`. Changes to the ref's value or the reactive object's property are synchronized.

Source: https://github.com/vuejs/docs/blob/main/src/api/reactivity-core.md#_snippet_5

```typescript
const count = ref(1)
const obj = reactive({ count })

// ref will be unwrapped
console.log(obj.count === count.value) // true

// it will update `obj.count`
count.value++
console.log(count.value) // 2
console.log(obj.count) // 2

// it will also update `count` ref
obj.count++
console.log(obj.count) // 3
console.log(count.value) // 3
```

---

## Watch with Flush and Debug Options - JavaScript

Demonstrates how to configure the `flush` timing and debugging options when using the `watch` function in Vue.js. These options allow fine-grained control over when the callback is executed and provide debugging hooks.

Source: https://github.com/vuejs/docs/blob/main/src/api/reactivity-core.md#_snippet_21

```javascript
watch(source, callback, {
  flush: 'post',
  onTrack(e) {
    debugger
  },
  onTrigger(e) {
    debugger
  }
})
```

---

## Watch with Side Effect Cleanup - JavaScript

Demonstrates how to use the `onCleanup` function within a `watch` callback to clean up side effects. This is useful for cancelling pending asynchronous operations when the watched source changes.

Source: https://github.com/vuejs/docs/blob/main/src/api/reactivity-core.md#_snippet_24

```javascript
watch(id, async (newId, oldId, onCleanup) => {
  const { response, cancel } = doAsyncWork(newId)
  // `cancel` will be called if `id` changes, cancelling
  // the previous request if it hasn't completed yet
  onCleanup(cancel)
  data.value = await response
})
```

---

## Debugging Computed Properties in Vue.js

Illustrates how to debug computed properties using the `onTrack` and `onTrigger` options within the computed function.  These options allow setting breakpoints when dependencies are tracked or when the computed value is triggered.

Source: https://github.com/vuejs/docs/blob/main/src/api/reactivity-core.md#_snippet_3

```javascript
const plusOne = computed(() => count.value + 1, {
  onTrack(e) {
    debugger
  },
  onTrigger(e) {
    debugger
  }
})
```

---

## Side Effect Cleanup in Watchers in Vue.js

Demonstrates how to perform side effect cleanup within a watcher using the `onCleanup` callback. The cleanup callback is called right before the next time the effect is re-run, allowing for cleanup of invalidated side effects.

Source: https://github.com/vuejs/docs/blob/main/src/api/reactivity-core.md#_snippet_12

```javascript
watchEffect(async (onCleanup) => {
  const { response, cancel } = doAsyncWork(newId)
  // `cancel` will be called if `id` changes, cancelling
  // the previous request if it hasn't completed yet
  onCleanup(cancel)
  data.value = await response
})
```

---

## Watch Reactive Object Directly - JavaScript

Shows how to directly watch a reactive object. The watcher is automatically in deep mode, and will trigger on any deep mutation to the object.

Source: https://github.com/vuejs/docs/blob/main/src/api/reactivity-core.md#_snippet_20

```javascript
const state = reactive({ count: 0 })
watch(state, () => {
  /* triggers on deep mutation to state */
})
```

---

## Side Effect Cleanup (Vue 3.5+) in Watchers

Shows side effect cleanup within a watcher using `onWatcherCleanup` introduced in Vue 3.5+. It offers a more direct way to register cleanup functions for watchers.

Source: https://github.com/vuejs/docs/blob/main/src/api/reactivity-core.md#_snippet_13

```javascript
import { onWatcherCleanup } from 'vue'

watchEffect(async () => {
  const { response, cancel } = doAsyncWork(newId)
  // `cancel` will be called if `id` changes, cancelling
  // the previous request if it hasn't completed yet
  onWatcherCleanup(cancel)
  data.value = await response
})
```

---

## onWatcherCleanup Example - TypeScript

Illustrates how to use the `onWatcherCleanup` function in Vue.js within a `watch` callback to register a cleanup function.  This function is called when the watcher is about to re-run, allowing for cleanup of previous side effects.

Source: https://github.com/vuejs/docs/blob/main/src/api/reactivity-core.md#_snippet_27

```typescript
import { watch, onWatcherCleanup } from 'vue'

watch(id, (newId) => {
  const { response, cancel } = doAsyncWork(newId)
  // `cancel` will be called if `id` changes, cancelling
  // the previous request if it hasn't completed yet
  onWatcherCleanup(cancel)
})
```

---

## Ref Unwrapping in Arrays and Collections with reactive() in Vue.js

Illustrates that refs are not automatically unwrapped when accessed as elements of a reactive array or native collection type like `Map`. The `.value` property needs to be explicitly accessed.

Source: https://github.com/vuejs/docs/blob/main/src/api/reactivity-core.md#_snippet_6

```javascript
const books = reactive([ref('Vue 3 Guide')])
// need .value here
console.log(books[0].value)

const map = reactive(new Map([['count', ref(0)]]))
// need .value here
console.log(map.get('count').value)
```

---

## Assigning Refs to Reactive Properties in Vue.js

Demonstrates that when assigning a ref to a property of a reactive object, the ref will be automatically unwrapped, and the reactive property will directly hold the ref's value.

Source: https://github.com/vuejs/docs/blob/main/src/api/reactivity-core.md#_snippet_7

```typescript
const count = ref(1)
const obj = reactive({})

obj.count = count

console.log(obj.count) // 1
console.log(obj.count === count.value) // true
```

---

## Stopping a Watcher in Vue.js

Shows how to stop a watcher created with `watchEffect()` using the handle function returned by `watchEffect()`. Calling the handle function prevents the effect from running again.

Source: https://github.com/vuejs/docs/blob/main/src/api/reactivity-core.md#_snippet_10

```javascript
const stop = watchEffect(() => {})

// when the watcher is no longer needed:
stop()
```

---

## Pausing and Resuming a Watcher - JavaScript

Shows how to pause and resume a watcher created with the `watch` function in Vue.js. This feature is available in Vue 3.5+. The pause method temporarily suspends the watcher, while resume reactivates it.

Source: https://github.com/vuejs/docs/blob/main/src/api/reactivity-core.md#_snippet_23

```javascript
const { stop, pause, resume } = watch(() => {})

// temporarily pause the watcher
pause()

// resume later
resume()

// stop
stop()
```

