# Vue.js Getting Started Tutorial

## Configure Vite Alias for Vue

This code snippet shows how to configure an alias in Vite to resolve the `vue` import to the `vue/dist/vue.esm-bundler.js` file. This configuration is necessary when using Vue in HTML mode with Vite, ensuring correct in-browser template compilation.

Source: https://github.com/vuejs/docs/blob/main/src/tutorial/src/step-1/description.md#_snippet_1

```JavaScript
// vite.config.js
export default {
  resolve: {
    alias: {
      vue: 'vue/dist/vue.esm-bundler.js'
    }
  }
}
```

