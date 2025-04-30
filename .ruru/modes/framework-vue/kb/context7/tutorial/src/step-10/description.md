# Vue.js Watchers: Reactively Performing Side Effects

## Watching a Ref with Composition API in Vue.js

This code snippet demonstrates how to use the `watch` function from the Vue.js Composition API to watch a ref and execute a callback function whenever the ref's value changes. The `count` ref is initialized to 0, and the `watch` function is used to log the new count value to the console whenever it changes. This approach allows for reactive side effects based on changes in reactive data.

Source: https://github.com/vuejs/docs/blob/main/src/tutorial/src/step-10/description.md#_snippet_0

```javascript
import { ref, watch } from 'vue'

const count = ref(0)

watch(count, (newCount) => {
  // yes, console.log() is a side effect
  console.log(`new count is: ${newCount}`)
})
```

