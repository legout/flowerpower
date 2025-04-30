# Vue.js Compile-Time Flags Configuration

## Configuring Compile-Time Flags in Vite

This code snippet demonstrates how to configure compile-time flags in a Vite project using the `define` config option. It enables detailed warnings for hydration mismatches in production builds. This is achieved by setting the `__VUE_PROD_HYDRATION_MISMATCH_DETAILS__` flag to `'true'`.

Source: https://github.com/vuejs/docs/blob/main/src/api/compile-time-flags.md#_snippet_0

```JavaScript
// vite.config.js
import { defineConfig } from 'vite'

export default defineConfig({
  define: {
    // enable hydration mismatch details in production build
    __VUE_PROD_HYDRATION_MISMATCH_DETAILS__: 'true'
  }
})
```

---

## Configuring Compile-Time Flags in Webpack

This code snippet demonstrates how to configure compile-time flags in a Webpack project using the `DefinePlugin`. It sets the values for `__VUE_OPTIONS_API__`, `__VUE_PROD_DEVTOOLS__`, and `__VUE_PROD_HYDRATION_MISMATCH_DETAILS__` flags. This allows for fine-grained control over which features are included in the final bundle.

Source: https://github.com/vuejs/docs/blob/main/src/api/compile-time-flags.md#_snippet_2

```JavaScript
// webpack.config.js
module.exports = {
  // ...
  plugins: [
    new webpack.DefinePlugin({
      __VUE_OPTIONS_API__: 'true',
      __VUE_PROD_DEVTOOLS__: 'false',
      __VUE_PROD_HYDRATION_MISMATCH_DETAILS__: 'false'
    })
  ]
}
```

---

## Configuring Compile-Time Flags in Vue CLI

This code snippet shows how to configure compile-time flags in a Vue CLI project using `chainWebpack`. It sets the values for `__VUE_OPTIONS_API__`, `__VUE_PROD_DEVTOOLS__`, and `__VUE_PROD_HYDRATION_MISMATCH_DETAILS__` flags. This allows customizing the features included in the build.

Source: https://github.com/vuejs/docs/blob/main/src/api/compile-time-flags.md#_snippet_1

```JavaScript
// vue.config.js
module.exports = {
  chainWebpack: (config) => {
    config.plugin('define').tap((definitions) => {
      Object.assign(definitions[0], {
        __VUE_OPTIONS_API__: 'true',
        __VUE_PROD_DEVTOOLS__: 'false',
        __VUE_PROD_HYDRATION_MISMATCH_DETAILS__: 'false'
      })
      return definitions
    })
  }
}
```

