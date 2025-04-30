# Vue.js Custom Elements API Documentation

## Type Definition for defineCustomElement

Shows the TypeScript type definition for the `defineCustomElement` function and the `CustomElementsOptions` interface. It illustrates the structure and available options when defining custom elements in Vue.

Source: https://github.com/vuejs/docs/blob/main/src/api/custom-elements.md#_snippet_0

```typescript
function defineCustomElement(
  component:
    | (ComponentOptions & CustomElementsOptions)
    | ComponentOptions['setup'],
  options?: CustomElementsOptions
): {
  new (props?: object): HTMLElement
}

interface CustomElementsOptions {
  styles?: string[]

  // the following options are 3.5+
  configureApp?: (app: App) => void
  shadowRoot?: boolean
  nonce?: string
}
```

---

## Registering a Custom Element

Demonstrates how to define a custom element using `defineCustomElement` and register it with the browser using `customElements.define`.  It shows the fundamental steps involved in creating and registering a Vue-powered web component.

Source: https://github.com/vuejs/docs/blob/main/src/api/custom-elements.md#_snippet_2

```javascript
import { defineCustomElement } from 'vue'

const MyVueElement = defineCustomElement({
  /* component options */
})

// Register the custom element.
customElements.define('my-vue-element', MyVueElement)
```

---

## Custom Element Configuration Example

Illustrates how to configure a custom element using the `configureApp` option. Demonstrates passing custom options to `defineCustomElement` for Vue application configuration.

Source: https://github.com/vuejs/docs/blob/main/src/api/custom-elements.md#_snippet_1

```javascript
import Element from './MyElement.ce.vue'

defineCustomElement(Element, {
  configureApp(app) {
    // ...
  }
})
```

