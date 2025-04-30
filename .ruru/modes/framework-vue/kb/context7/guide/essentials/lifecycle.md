# Vue Component Lifecycle Hooks

## Incorrect onMounted Usage (Composition API, JavaScript)

Illustrates an incorrect way to use the `onMounted` hook in the Composition API.  `onMounted` must be called synchronously during component setup, not asynchronously inside a `setTimeout` call. This example shows what *not* to do.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/lifecycle.md#_snippet_2

```javascript
setTimeout(() => {
  onMounted(() => {
    // this won't work.
  })
}, 100)
```

