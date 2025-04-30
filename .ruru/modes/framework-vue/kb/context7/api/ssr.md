# Vue.js Server-Side Rendering API

## Accessing SSR Context in Vue Component

This snippet demonstrates how to access the SSR context within a Vue component using the `useSSRContext` composable. It checks if the code is running during server-side rendering (SSR) using `import.meta.env.SSR` and then retrieves the context object. This allows components to attach information to the context, such as head metadata.

Source: https://github.com/vuejs/docs/blob/main/src/api/ssr.md#_snippet_1

```vue
<script setup>
import { useSSRContext } from 'vue'

// make sure to only call it during SSR
// https://vitejs.dev/guide/ssr.html#conditional-logic
if (import.meta.env.SSR) {
  const ctx = useSSRContext()
  // ...attach properties to the context
}
</script>
```

---

## Piping Vue App to Node.js Writable

This snippet showcases piping a Vue application's server-side rendered output directly to a Node.js Writable stream (e.g., an HTTP response). It uses `pipeToNodeWritable` from `vue/server-renderer`. `app` should be a Vue application instance, and `res` a Node.js Writable stream.

Source: https://github.com/vuejs/docs/blob/main/src/api/ssr.md#_snippet_3

```javascript
// inside a Node.js http handler
pipeToNodeWritable(app, {}, res)
```

