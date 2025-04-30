# Vue.js Server-Side Rendering (SSR) Documentation

## Custom Directive SSR Implementation JavaScript

This JavaScript code defines a custom directive with client-side (`mounted`) and server-side (`getSSRProps`) implementations. The `getSSRProps` hook allows specifying attributes to be added to the rendered element during SSR, enabling custom directive behavior on the server. It receives the directive binding as an argument.

Source: https://github.com/vuejs/docs/blob/main/src/guide/scaling-up/ssr.md#_snippet_9

```JavaScript
const myDirective = {
  mounted(el, binding) {
    // client-side implementation:
    // directly update the DOM
    el.id = binding.value
  },
  getSSRProps(binding) {
    // server-side implementation:
    // return the props to be rendered.
    // getSSRProps only receives the directive binding.
    return {
      id: binding.value
    }
  }
}
```

---

## Running Node.js script

The shell command executes the specified JavaScript file using Node.js. This is often used to start the server-side rendering process or run other server-side scripts.

Source: https://github.com/vuejs/docs/blob/main/src/guide/scaling-up/ssr.md#_snippet_6

```Shell
> node example.js
```

---

## Express Server with Vue SSR

This snippet sets up an Express server to handle requests and render a Vue app to HTML on the server-side. It imports Express, creates a Vue app instance, renders it to a string using `renderToString`, and sends the rendered HTML wrapped in a basic HTML structure as a response. Requires the 'express' and 'vue' packages.

Source: https://github.com/vuejs/docs/blob/main/src/guide/scaling-up/ssr.md#_snippet_1

```JavaScript
import express from 'express'
import { createSSRApp } from 'vue'
import { renderToString } from 'vue/server-renderer'

const server = express()

server.get('/', (req, res) => {
  const app = createSSRApp({
    data: () => ({ count: 1 }),
    template: `<button @click="count++">{{ count }}</button>`
  })

  renderToString(app).then((html) => {
    res.send(`
    <!DOCTYPE html>
    <html>
      <head>
        <title>Vue SSR Example</title>
      </head>
      <body>
        <div id="app">${html}</div>
      </body>
    </html>
    `)
  })
})

server.listen(3000, () => {
  console.log('ready')
})
```

---

## Creating SSR App with Request-Specific Store Instance - Vue.js

This code snippet demonstrates how to create a new instance of the Vue application, including a new store instance, for each server request to prevent cross-request state pollution in SSR environments. It uses `createSSRApp` from Vue and `app.provide` to make the store available to components.

Source: https://github.com/vuejs/docs/blob/main/src/guide/scaling-up/ssr.md#_snippet_7

```javascript
// app.js (shared between server and client)
import { createSSRApp } from 'vue'
import { createStore } from './store.js'

// called on each request
export function createApp() {
  const app = createSSRApp(/* ... */)
  // create new instance of store per request
  const store = createStore(/* ... */)
  // provide store at the app level
  app.provide('store', store)
  // also expose store for hydration purposes
  return { app, store }
}
```

---

## Creating Universal App

This JavaScript module exports a function `createApp` that creates a Vue app instance. This module is designed to be shared between the server and the client, ensuring that both environments use the same app definition. It uses `createSSRApp` for SSR compatibility.

Source: https://github.com/vuejs/docs/blob/main/src/guide/scaling-up/ssr.md#_snippet_3

```JavaScript
// app.js (shared between server and client)
import { createSSRApp } from 'vue'

export function createApp() {
  return createSSRApp({
    data: () => ({ count: 1 }),
    template: `<button @click="count++">{{ count }}</button>`
  })
}
```

---

## Client Entry Point

This JavaScript snippet serves as the entry point for the client-side application. It imports the `createApp` function from the shared `app.js` module, calls the function to create the Vue app instance, and mounts the app to the DOM element with the ID 'app', initiating the hydration process.

Source: https://github.com/vuejs/docs/blob/main/src/guide/scaling-up/ssr.md#_snippet_4

```JavaScript
// client.js
import { createApp } from './app.js'

createApp().mount('#app')
```

---

## Server-Side Rendering with Shared App

This JavaScript snippet demonstrates how to use the shared `createApp` function in the server-side rendering process. It imports the function from `app.js`, calls it to create a Vue app instance within the request handler, renders the app to HTML using `renderToString`, and sends the HTML as a response. Omitting the irrelevant code.

Source: https://github.com/vuejs/docs/blob/main/src/guide/scaling-up/ssr.md#_snippet_5

```JavaScript
// server.js (irrelevant code omitted)
import { createApp } from './app.js'

server.get('/', (req, res) => {
  const app = createApp()
  renderToString(app).then(html => {
    // ...
  })
})
```

---

## SSR App Rendering (Node.js)

This JavaScript snippet demonstrates the basic rendering of a Vue app to a string on the server using Node.js. It imports the necessary functions from 'vue' and 'vue/server-renderer', creates a simple Vue app instance with a button, and renders it to HTML. The rendered HTML is then logged to the console.

Source: https://github.com/vuejs/docs/blob/main/src/guide/scaling-up/ssr.md#_snippet_0

```JavaScript
// this runs in Node.js on the server.
import { createSSRApp } from 'vue'
// Vue's server-rendering API is exposed under `vue/server-renderer`.
import { renderToString } from 'vue/server-renderer'

const app = createSSRApp({
  data: () => ({ count: 1 }),
  template: `<button @click="count++">{{ count }}</button>`
})

renderToString(app).then((html) => {
  console.log(html)
})
```

---

## Teleports SSR Context Example JavaScript

This JavaScript code shows how teleports are exposed under the `teleports` property of the SSR context object when using `renderToString`.  The `ctx.teleports` object contains the teleported content, which needs to be manually injected into the final page HTML. The context is passed into `renderToString` function.

Source: https://github.com/vuejs/docs/blob/main/src/guide/scaling-up/ssr.md#_snippet_10

```JavaScript
const ctx = {}
const html = await renderToString(app, ctx)

console.log(ctx.teleports) // { '#teleported': 'teleported content' }
```

---

## Client-Side Hydration (Browser)

This JavaScript snippet shows how to hydrate a server-rendered Vue app on the client-side. It imports `createSSRApp` from 'vue', creates a Vue app instance (identical to the server-side app), and mounts it to the DOM element with the ID 'app'. This process attaches event listeners and makes the app interactive.

Source: https://github.com/vuejs/docs/blob/main/src/guide/scaling-up/ssr.md#_snippet_2

```JavaScript
// this runs in the browser.
import { createSSRApp } from 'vue'

const app = createSSRApp({
  // ...same app as on server
})

// mounting an SSR app on the client assumes
// the HTML was pre-rendered and will perform
// hydration instead of mounting new DOM nodes.
app.mount('#app')
```

