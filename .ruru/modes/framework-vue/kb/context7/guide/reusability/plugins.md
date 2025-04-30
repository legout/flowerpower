# Vue.js Plugins Documentation

## Defining a Plugin - Vue.js

Illustrates how to define a Vue.js plugin as an object with an `install()` method. The `install()` method receives the application instance (`app`) and any options passed during installation, allowing the plugin to configure the application as needed. This provides a structured way to encapsulate plugin logic.

Source: https://github.com/vuejs/docs/blob/main/src/guide/reusability/plugins.md#_snippet_1

```javascript
const myPlugin = {
  install(app, options) {
    // configure the app
  }
}
```

---

## Installing i18n Plugin with Translations - Vue.js

Shows how to install the i18n plugin and pass a configuration object containing the translations. The configuration object is passed as the second argument to `app.use()`, providing the translated values that the `$translate` method will use.

Source: https://github.com/vuejs/docs/blob/main/src/guide/reusability/plugins.md#_snippet_5

```javascript
import i18nPlugin from './plugins/i18n'

app.use(i18nPlugin, {
  greetings: {
    hello: 'Bonjour!'
  }
})
```

---

## Adding a Global Translation Method - Vue.js

Demonstrates how to add a globally available translation method (`$translate`) to a Vue.js application using a plugin. It attaches the method to `app.config.globalProperties`, allowing it to be accessed from any template. The method retrieves nested properties from the plugin's options based on a dot-delimited key.

Source: https://github.com/vuejs/docs/blob/main/src/guide/reusability/plugins.md#_snippet_3

```javascript
// plugins/i18n.js
export default {
  install: (app, options) => {
    // inject a globally available $translate() method
    app.config.globalProperties.$translate = (key) => {
      // retrieve a nested property in `options`
      // using `key` as the path
      return key.split('.').reduce((o, i) => {
        if (o) return o[i]
      }, options)
    }
  }
}
```

---

## Installing a Plugin - Vue.js

Demonstrates how to install a Vue.js plugin using the `app.use()` method. It imports the `createApp` function from Vue and then uses `app.use()` to install the specified plugin, passing optional configuration options as a second argument. This allows the plugin to extend the application's functionality.

Source: https://github.com/vuejs/docs/blob/main/src/guide/reusability/plugins.md#_snippet_0

```javascript
import { createApp } from 'vue'

const app = createApp({})

app.use(myPlugin, {
  /* optional options */
})
```

---

## Injecting Plugin Options (Composition API) - Vue.js

Shows how to inject the provided i18n options into a component using the Composition API's `inject` function. It imports `inject` from Vue and uses it to retrieve the `i18n` options, which can then be used within the component's setup function.

Source: https://github.com/vuejs/docs/blob/main/src/guide/reusability/plugins.md#_snippet_7

```vue
<script setup>
import { inject } from 'vue'

const i18n = inject('i18n')

console.log(i18n.greetings.hello)
</script>
```

---

## Using the Translation Method in a Template - Vue.js

Illustrates how to use the `$translate` method within a Vue.js template.  The method takes a string key (e.g. 'greetings.hello') which corresponds to a translated value defined in the plugin configuration.

Source: https://github.com/vuejs/docs/blob/main/src/guide/reusability/plugins.md#_snippet_4

```vue-html
<h1>{{ $translate('greetings.hello') }}</h1>
```

---

## Injecting Plugin Options (Options API) - Vue.js

Shows how to inject the provided i18n options into a component using the Options API's `inject` property. It specifies 'i18n' in the `inject` array, making the injected options available as `this.i18n` within the component instance, allowing access to the translation data.

Source: https://github.com/vuejs/docs/blob/main/src/guide/reusability/plugins.md#_snippet_8

```javascript
export default {
  inject: ['i18n'],
  created() {
    console.log(this.i18n.greetings.hello)
  }
}
```

