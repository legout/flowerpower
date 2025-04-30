# Component Registration in Vue.js

## Global Component Registration in Vue.js

Demonstrates how to register a component globally using the `.component()` method on a Vue application instance. This makes the component available in all templates within the application. The example shows registering both a component implementation and an imported .vue file.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/registration.md#_snippet_0

```javascript
import { createApp } from 'vue'

const app = createApp({})

app.component(
  // the registered name
  'MyComponent',
  // the implementation
  {
    /* ... */
  }
)
```

---

## Local Component Registration in Vue.js (Options API)

Demonstrates how to register a component locally using the `components` option in a Vue.js component definition (Options API, without `<script setup>`). This makes the component available only within the current component's template. The example imports the component and registers it in the `components` object.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/registration.md#_snippet_5

```javascript
import ComponentA from './ComponentA.js'

export default {
  components: {
    ComponentA
  },
  setup() {
    // ...
  }
}
```

---

## Local Component Usage in Vue.js with <script setup>

Shows how to use components locally within a Vue.js component using `<script setup>`. Imported components are automatically available in the template without needing explicit registration in the `components` option. Requires using Single-File Components (SFCs).

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/registration.md#_snippet_4

```vue
<script setup>
import ComponentA from './ComponentA.vue'
</script>

<template>
  <ComponentA />
</template>
```

---

## Local Component Registration and Usage in Vue.js (Options API + Template)

Illustrates local component registration within a Vue.js Single-File Component (SFC) using the `components` option. It includes the template code demonstrating how to use the locally registered component.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/registration.md#_snippet_6

```vue
<script>
import ComponentA from './ComponentA.vue'

export default {
  components: {
    ComponentA
  }
}
</script>

<template>
  <ComponentA />
</template>
```

---

## Using Globally Registered Components in Vue.js Template

Demonstrates how to use globally registered components within a Vue.js template. The components can be used in any component within the application without needing explicit import or registration in each component.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/registration.md#_snippet_3

```vue-html
<!-- this will work in any component inside the app -->
<ComponentA/>
<ComponentB/>
<ComponentC/>
```

---

## Chained Global Component Registration in Vue.js

Illustrates how to chain the `.component()` method to register multiple components globally in a concise manner. This approach allows for registering several components in a single statement.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/registration.md#_snippet_2

```javascript
app
  .component('ComponentA', ComponentA)
  .component('ComponentB', ComponentB)
  .component('ComponentC', ComponentC)
```

---

## Global Component Registration with SFC in Vue.js

Shows how to register a Single-File Component (SFC) globally using the `.component()` method. The component is imported from a `.vue` file and registered with a specified name.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/registration.md#_snippet_1

```javascript
import MyComponent from './App.vue'

app.component('MyComponent', MyComponent)
```

