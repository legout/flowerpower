# Vue.js Quick Start Guide

## Enabling Import Maps for Vue (Options API)

This snippet demonstrates using import maps to map the 'vue' import specifier to the Vue.js ES module CDN URL. This allows using `import { createApp } from 'vue'` directly. It also includes the application initialization code using Options API.

Source: https://github.com/vuejs/docs/blob/main/src/guide/quick-start.md#_snippet_17

```HTML
<script type="importmap">
  {
    "imports": {
      "vue": "https://unpkg.com/vue@3/dist/vue.esm-browser.js"
    }
  }
</script>

<div id="app">{{ message }}</div>

<script type="module">
  import { createApp } from 'vue'

  createApp({
    data() {
      return {
        message: 'Hello Vue!'
      }
    }
  }).mount('#app')
</script>
```

---

## Enabling Import Maps for Vue (Composition API)

This snippet demonstrates using import maps to map the 'vue' import specifier to the Vue.js ES module CDN URL when using Composition API. This allows using `import { createApp } from 'vue'` directly. It also includes the application initialization code using Composition API.

Source: https://github.com/vuejs/docs/blob/main/src/guide/quick-start.md#_snippet_18

```HTML
<script type="importmap">
  {
    "imports": {
      "vue": "https://unpkg.com/vue@3/dist/vue.esm-browser.js"
    }
  }
</script>

<div id="app">{{ message }}</div>

<script type="module">
  import { createApp, ref } from 'vue'

  createApp({
    setup() {
      const message = ref('Hello Vue!')
      return {
        message
      }
    }
  }).mount('#app')
</script>
```

---

## Building a Vue Project with Yarn

This command builds a production-ready version of the Vue application using Yarn.  The output is typically placed in a `./dist` directory.

Source: https://github.com/vuejs/docs/blob/main/src/guide/quick-start.md#_snippet_10

```sh
$ yarn build
```

---

## Splitting Modules - Component Definition (Composition API)

This snippet defines a Vue component in a separate JavaScript file using the Composition API. It exports the component's setup function and template. Requires the main HTML file to import this component.

Source: https://github.com/vuejs/docs/blob/main/src/guide/quick-start.md#_snippet_21

```JavaScript
// my-component.js
import { ref } from 'vue'
export default {
  setup() {
    const count = ref(0)
    return { count }
  },
  template: `<div>Count is: {{ count }}</div>`
}
```

---

## Initializing Vue with ES Module CDN (Composition API)

This snippet initializes a Vue application using the ES module build from a CDN, utilizing the Composition API. It defines a reactive 'message' using 'ref' and makes it available to the template.  Requires a browser that supports ES modules.

Source: https://github.com/vuejs/docs/blob/main/src/guide/quick-start.md#_snippet_16

```HTML
<div id="app">{{ message }}</div>

<script type="module">
  import { createApp, ref } from 'https://unpkg.com/vue@3/dist/vue.esm-browser.js'

  createApp({
    setup() {
      const message = ref('Hello Vue!')
      return {
        message
      }
    }
  }).mount('#app')
</script>
```

---

## Initializing Vue with ES Module CDN (Options API)

This snippet shows how to initialize a Vue application using the ES module build from a CDN. It defines a simple component with data binding and mounts it to the DOM element with the ID 'app'. Requires a browser that supports ES modules.

Source: https://github.com/vuejs/docs/blob/main/src/guide/quick-start.md#_snippet_15

```HTML
<div id="app">{{ message }}</div>

<script type="module">
  import { createApp } from 'https://unpkg.com/vue@3/dist/vue.esm-browser.js'

  createApp({
    data() {
      return {
        message: 'Hello Vue!'
      }
    }
  }).mount('#app')
</script>
```

---

## Running a Vue Project with pnpm

These commands navigate to the project directory and then install dependencies and start the development server using pnpm. The template syntax `{{'<your-project-name>'}}` will need to be replaced with the actual project name.

Source: https://github.com/vuejs/docs/blob/main/src/guide/quick-start.md#_snippet_5

```sh
$ cd {{'<your-project-name>'}}
$ pnpm install
$ pnpm run dev
```

---

## Splitting Modules - Component Definition (Options API)

This snippet defines a Vue component in a separate JavaScript file using the Options API. It exports the component's options object, including data and template. Requires the main HTML file to import this component.

Source: https://github.com/vuejs/docs/blob/main/src/guide/quick-start.md#_snippet_20

```JavaScript
// my-component.js
export default {
  data() {
    return { count: 0 }
  },
  template: `<div>Count is: {{ count }}</div>`
}
```

