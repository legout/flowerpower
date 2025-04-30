# Vue and Web Components Integration

## Use Custom Element in Vue SFC without Type Definitions

Demonstrates how to use a custom element in a Vue SFC when the custom element library does not provide type definitions.  It shows how to define types locally and integrate those types with Vue's `GlobalComponents` type. It imports the custom element and the type helper and manually defines the property and event types.

Source: https://github.com/vuejs/docs/blob/main/src/guide/extras/web-components.md#_snippet_19

```vue
<script setup lang="ts">
// Suppose that `some-lib` is plain JS without type definitions, and TypeScript
// cannot infer the types:
import { SomeElement } from 'some-lib'

// We'll use the same type helper as before.
import { DefineCustomElement } from './DefineCustomElement'

type SomeElementProps = { foo?: number; bar?: string }
type SomeElementEvents = { 'apple-fell': AppleFellEvent }
interface AppleFellEvent extends Event {
  /* ... */
}

// Add the new element type to Vue's GlobalComponents type.
declare module 'vue' {
  interface GlobalComponents {
    'some-element': DefineCustomElement<
      SomeElementProps,
      SomeElementEvents
    >
  }
}

// ... same as before, use a reference to the element ...
</script>

<template>
  <!-- ... same as before, use the element in the template ... -->
</template>
```

---

## In-Browser Config for Custom Elements in Vue

This snippet demonstrates how to configure Vue in the browser to treat HTML tags containing a hyphen as custom elements. This configuration prevents Vue from attempting to resolve them as Vue components, avoiding warnings.

Source: https://github.com/vuejs/docs/blob/main/src/guide/extras/web-components.md#_snippet_0

```JavaScript
// Only works if using in-browser compilation.
// If using build tools, see config examples below.
app.config.compilerOptions.isCustomElement = (tag) => tag.includes('-')
```

---

## Defining a Custom Element with Vue

This snippet shows how to define a custom element using Vue's `defineCustomElement` method. It includes defining properties, events, a template, and styles, and registering the element for use in HTML.

Source: https://github.com/vuejs/docs/blob/main/src/guide/extras/web-components.md#_snippet_4

```JavaScript
import { defineCustomElement } from 'vue'

const MyVueElement = defineCustomElement({
  // normal Vue component options here
  props: {},
  emits: {},
  template: `...`,

  // defineCustomElement only: CSS to be injected into shadow root
  styles: [`/* inlined css */`]
})

// Register the custom element.
// After registration, all `<my-vue-element>` tags
// on the page will be upgraded.
customElements.define('my-vue-element', MyVueElement)

// You can also programmatically instantiate the element:
// (can only be done after registration)
document.body.appendChild(
  new MyVueElement({
    // initial props (optional)
  })
)
```

---

## Defining Custom Element Types in TypeScript

This TypeScript snippet demonstrates how to define types for Vue custom elements to enable type checking in Vue templates. It imports `defineCustomElement` from Vue, converts a Vue component into a custom element, registers it with the browser, and then augments the `GlobalComponents` interface in the Vue module to provide type information for the custom element in Vue templates.  It is important to use the Vue component type when augmenting the `GlobalComponents` interface.

Source: https://github.com/vuejs/docs/blob/main/src/guide/extras/web-components.md#_snippet_14

```typescript
import { defineCustomElement } from 'vue'

// Import the Vue component.
import SomeComponent from './src/components/SomeComponent.ce.vue'

// Turn the Vue component into a Custom Element class.
export const SomeElement = defineCustomElement(SomeComponent)

// Remember to register the element class with the browser.
customElements.define('some-element', SomeElement)

// Add the new element type to Vue's GlobalComponents type.
declare module 'vue' {
  interface GlobalComponents {
    // Be sure to pass in the Vue component type here 
    // (SomeComponent, *not* SomeElement).
    // Custom Elements require a hyphen in their name, 
    // so use the hyphenated element name here.
    'some-element': typeof SomeComponent
  }
}
```

---

## Passing DOM Properties to Custom Elements

This snippet demonstrates how to pass complex data as DOM properties to custom elements in Vue using the `.prop` modifier with `v-bind`.  This is necessary because DOM attributes can only be strings, while properties can hold complex data types.

Source: https://github.com/vuejs/docs/blob/main/src/guide/extras/web-components.md#_snippet_3

```Vue HTML
<my-element :user.prop="{ name: 'jack' }"></my-element>

<!-- shorthand equivalent -->
<my-element .user="{ name: 'jack' }"></my-element>
```

---

## Use Custom Element in Vue SFC with TypeScript

Demonstrates how to use the custom element in a Vue single-file component (SFC) with TypeScript support. It imports the custom element's JavaScript file and the Vue-specific type definition. It uses `useTemplateRef` to access the element's properties and sets up event handling. The template shows the usage of the custom element with type checked props and event handler.

Source: https://github.com/vuejs/docs/blob/main/src/guide/extras/web-components.md#_snippet_18

```vue
<script setup lang="ts">
// This will create and register the element with the browser.
import 'some-lib/dist/SomeElement.js'

// A user that is using TypeScript and Vue should additionally import the
// Vue-specific type definition (users of other frameworks may import other
// framework-specific type definitions).
import type {} from 'some-lib/dist/SomeElement.vue.js'

import { useTemplateRef, onMounted } from 'vue'

const el = useTemplateRef('el')

onMounted(() => {
  console.log(
    el.value!.foo,
    el.value!.bar,
    el.value!.lorem,
    el.value!.someMethod()
  )

  // Do not use these props, they are `undefined`
  // IDE will show them crossed out
  el.$props
  el.$emit
})
</script>

<template>
  <!-- Now we can use the element, with type checking: -->
  <some-element
    ref="el"
    :foo="456"
    :blah="'hello'"
    @apple-fell="
      (event) => {
        // The type of `event` is inferred here to be `AppleFellEvent`
      }
    "
  ></some-element>
</template>
```

---

## Using Custom Elements in JSX

This JSX snippet demonstrates how to import and define custom elements within a JSX component.  It imports the custom elements and then defines them using `customElements.define` before using them within the JSX markup. This allows for the usage of Vue-based custom elements in other frameworks that support JSX.

Source: https://github.com/vuejs/docs/blob/main/src/guide/extras/web-components.md#_snippet_13

```jsx
import { MyFoo, MyBar } from 'path/to/elements.js'

customElements.define('some-foo', MyFoo)
customElements.define('some-bar', MyBar)

export function MyComponent() {
  return <>
    <some-foo ... >
      <some-bar ... ></some-bar>
    </some-foo>
  </>
}
```

---

## Using Custom Elements in Vue

This Vue snippet illustrates how to import and register custom elements within a Vue component using the `register` function from the custom elements library. The `register` function is called within the `<script setup>` section to define the custom elements, making them available for use in the component's template.

Source: https://github.com/vuejs/docs/blob/main/src/guide/extras/web-components.md#_snippet_12

```vue
<script setup>
import { register } from 'path/to/elements.js'
register()
</script>

<template>
  <my-foo ...>
    <my-bar ...></my-bar>
  </my-foo>
</template>
```

---

## Vite Config for Custom Elements in Vue

This snippet shows how to configure Vite to treat HTML tags containing a hyphen as custom elements when using the Vue plugin.  This configuration is part of the build process and affects how Vue compiles the templates.

Source: https://github.com/vuejs/docs/blob/main/src/guide/extras/web-components.md#_snippet_1

```JavaScript
// vite.config.js
import vue from '@vitejs/plugin-vue'

export default {
  plugins: [
    vue({
      template: {
        compilerOptions: {
          // treat all tags with a dash as custom elements
          isCustomElement: (tag) => tag.includes('-')
        }
      }
    })
  ]
}
```

---

## Named Slots in Custom Element

Demonstrates how to use named slots with Vue-defined custom elements using the `slot` attribute.  The `v-slot` directive is not supported for named slots when consuming custom elements.

Source: https://github.com/vuejs/docs/blob/main/src/guide/extras/web-components.md#_snippet_8

```Vue HTML
<my-element>
    <div slot="named">hello</div>
  </my-element>
```

---

## Configure App Instance of Custom Element

Demonstrates how to configure the app instance of a Vue custom element using the configureApp option in `defineCustomElement`. This allows for customization of the Vue app instance that powers the custom element.

Source: https://github.com/vuejs/docs/blob/main/src/guide/extras/web-components.md#_snippet_9

```JavaScript
defineCustomElement(MyComponent, {
  configureApp(app) {
    app.config.errorHandler = (err) => {
      /* ... */
    }
  }
})
```

---

## Custom Element Usage in HTML

Example of how the custom element defined with Vue is used inside HTML. This shows the HTML tag that will be used to render the Vue component as a custom element.

Source: https://github.com/vuejs/docs/blob/main/src/guide/extras/web-components.md#_snippet_5

```Vue HTML
<my-vue-element></my-vue-element>
```

---

## Create Custom Element Type Helper in TypeScript

Creates a TypeScript type helper, `DefineCustomElement`, for registering custom element type definitions in Vue. It defines the `$props` and `$emit` properties for template type checking.  The `$props` type combines the element's props with global HTML props and Vue's special props. The `$emit` type is used to specifically define event types.

Source: https://github.com/vuejs/docs/blob/main/src/guide/extras/web-components.md#_snippet_16

```typescript
// file: some-lib/src/DefineCustomElement.ts

// We can re-use this type helper per each element we need to define.
type DefineCustomElement<
  ElementType extends HTMLElement,
  Events extends EventMap = {},
  SelectedAttributes extends keyof ElementType = keyof ElementType
> = new () => ElementType & {
  // Use $props to define the properties exposed to template type checking. Vue
  // specifically reads prop definitions from the `$props` type. Note that we
  // combine the element's props with the global HTML props and Vue's special
  // props.
  /** @deprecated Do not use the $props property on a Custom Element ref, 
    this is for template prop types only. */
  $props: HTMLAttributes &
    Partial<Pick<ElementType, SelectedAttributes>> &
    PublicProps

  // Use $emit to specifically define event types. Vue specifically reads event
  // types from the `$emit` type. Note that `$emit` expects a particular format
  // that we map `Events` to.
  /** @deprecated Do not use the $emit property on a Custom Element ref, 
    this is for template prop types only. */
  $emit: VueEmit<Events>
}

type EventMap = {
  [event: string]: Event
}

// This maps an EventMap to the format that Vue's $emit type expects.
type VueEmit<T extends EventMap> = EmitFn<{  [K in keyof T]: (event: T[K]) => void
}>
```

---

## Exporting Vue Custom Elements

This JavaScript snippet demonstrates how to export individual Vue custom elements and a registration function for convenient use in other applications. It utilizes `defineCustomElement` from Vue to convert Vue components into custom elements and then exports them along with a function to register them with the browser's `customElements` API.

Source: https://github.com/vuejs/docs/blob/main/src/guide/extras/web-components.md#_snippet_11

```javascript
// elements.js

import { defineCustomElement } from 'vue'
import Foo from './MyFoo.ce.vue'
import Bar from './MyBar.ce.vue'

const MyFoo = defineCustomElement(Foo)
const MyBar = defineCustomElement(Bar)

// export individual elements
export { MyFoo, MyBar }

export function register() {
  customElements.define('my-foo', MyFoo)
  customElements.define('my-bar', MyBar)
}
```

---

## Boolean and Number Props Casting Example

This shows how Vue casts props defined as Boolean or Number types when set as attributes in the custom element.  Attributes are always strings, so Vue automatically converts them to the specified type.

Source: https://github.com/vuejs/docs/blob/main/src/guide/extras/web-components.md#_snippet_6

```JavaScript
props: {
    selected: Boolean,
    index: Number
  }
```

---

## Importing SFC in Custom Element Mode

This example shows how to import a Vue Single-File Component (SFC) in custom element mode by using the `.ce.vue` extension.  This inlines the component's styles and exposes them in the component's `styles` option for use with `defineCustomElement`.

Source: https://github.com/vuejs/docs/blob/main/src/guide/extras/web-components.md#_snippet_10

```JavaScript
import { defineCustomElement } from 'vue'
import Example from './Example.ce.vue'

console.log(Example.styles) // ["/* inlined css */"]

// convert into custom element constructor
const ExampleElement = defineCustomElement(Example)

// register
customElements.define('my-example', ExampleElement)
```

