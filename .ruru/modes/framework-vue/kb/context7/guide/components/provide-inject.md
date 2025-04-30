# Vue.js Provide / Inject

## Providing with Symbol Key (Composition API)

This snippet shows how to provide data using a Symbol injection key in Vue.js Composition API. It imports the Symbol key and provides an object associated with it.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/provide-inject.md#_snippet_19

```javascript
// in provider component
import { provide } from 'vue'
import { myInjectionKey } from './keys.js'

provide(myInjectionKey, {
  /* data to provide */
})
```

---

## Defining Symbol Injection Key (JavaScript)

This snippet demonstrates how to define a Symbol injection key in JavaScript. This is used to avoid potential naming conflicts when providing and injecting dependencies in large applications. It exports the Symbol for use in both provider and injector components.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/provide-inject.md#_snippet_18

```javascript
// keys.js
export const myInjectionKey = Symbol()
```

---

## Provide Reactive Value in Vue.js

This code snippet demonstrates providing a reactive value using `ref` and `provide` from Vue.js. It creates a reactive `count` using `ref` and provides it under the key 'key'. This allows descendant components to reactively connect to the provided value. Import both `ref` and `provide` from 'vue'.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/provide-inject.md#_snippet_2

```javascript
import { ref, provide } from 'vue'

const count = ref(0)
provide('key', count)
```

---

## Providing Reactive Data in Vue (Composition API)

This snippet demonstrates providing reactive data using the `provide` function in Vue.js Composition API.  It defines a `location` ref and a function `updateLocation` to mutate it, then provides both to the child component. The lines highlighted with {7-9,13} are the `updateLocation` function and the destructuring of the injected object.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/provide-inject.md#_snippet_14

```vue
<!-- inside provider component -->
<script setup>
import { provide, ref } from 'vue'

const location = ref('North Pole')

function updateLocation() {
  location.value = 'South Pole'
}

provide('location', {
  location,
  updateLocation
})
</script>
```

---

## Inject value using setup function in Vue.js

This code snippet illustrates injecting a value using the `inject` function within the `setup()` function (when not using `<script setup>`).  The `inject` function retrieves the provided value based on the given injection key.  Ensure to import `inject` from 'vue' and return the injected value from the `setup` function.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/provide-inject.md#_snippet_7

```javascript
import { inject } from 'vue'

export default {
  setup() {
    const message = inject('message')
    return { message }
  }
}
```

---

## Injection Default Values (Options API)

This code demonstrates how to provide default values for injected properties using the object syntax within the `inject` option of Vue.js' Options API.  You can provide primitive default values directly, or use a factory function for non-primitive values or values that are expensive to create.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/provide-inject.md#_snippet_13

```javascript
export default {
  // object syntax is required
  // when declaring default values for injections
  inject: {
    message: {
      from: 'message', // this is optional if using the same key for injection
      default: 'default value'
    },
    user: {
      // use a factory function for non-primitive values that are expensive
      // to create, or ones that should be unique per component instance.
      default: () => ({ name: 'John' })
    }
  }
}
```

---

## Injecting Reactive Data in Vue (Composition API)

This snippet demonstrates injecting reactive data using the `inject` function in Vue.js Composition API. It injects the `location` and `updateLocation` from the parent component and uses them in the template. The line highlighted with {5} shows the destructuring of the injected object.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/provide-inject.md#_snippet_15

```vue
<!-- in injector component -->
<script setup>
import { inject } from 'vue'

const { location, updateLocation } = inject('location')
</script>

<template>
  <button @click="updateLocation">{{ location }}</button>
</template>
```

---

## Provide value using Composition API in Vue.js

This code snippet demonstrates how to provide a value using the `provide` function from Vue.js' Composition API.  The first argument is the injection key (a string or Symbol), and the second is the value being provided. Make sure to import `provide` from 'vue'.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/provide-inject.md#_snippet_0

```vue
<script setup>
import { provide } from 'vue'

provide(/* key */ 'message', /* value */ 'hello!')
</script>
```

---

## Providing Reactive Data with Computed Property (Options API)

This snippet shows how to provide reactive data using a computed property in Vue.js Options API. It creates a computed property `message` that depends on the component's `message` data property, ensuring that changes to the `message` data property are reflected in the provided value. Line {10} highlights the creation of the computed property.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/provide-inject.md#_snippet_17

```javascript
import { computed } from 'vue'

export default {
  data() {
    return {
      message: 'hello!'
    }
  },
  provide() {
    return {
      // explicitly provide a computed property
      message: computed(() => this.message)
    }
  }
}
```

---

## App-level Provide in Vue.js

This code shows how to provide values at the app level in Vue.js. This makes the provided values available to all components rendered within the app. This approach is useful for plugins. Import `createApp` from 'vue'.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/provide-inject.md#_snippet_5

```javascript
import { createApp } from 'vue'

const app = createApp({})

app.provide(/* key */ 'message', /* value */ 'hello!')
```

---

## Injection Aliasing in Vue.js Options API

This code snippet demonstrates how to alias an injection key to a different local key using the object syntax in the `inject` option of Vue.js' Options API. The `from` property specifies the injection key, and the local key becomes the name of the property on the component instance (e.g., `this.localMessage`).

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/provide-inject.md#_snippet_10

```javascript
export default {
  inject: {
    /* local key */ localMessage: {
      from: /* injection key */ 'message'
    }
  }
}
```

---

## Provide value using setup function in Vue.js

This code snippet illustrates how to provide a value using the `provide` function within the `setup()` function when not using `<script setup>`. The `provide` function takes an injection key and the value to provide. It's crucial to call `provide()` synchronously inside `setup()` to ensure it registers correctly.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/provide-inject.md#_snippet_1

```javascript
import { provide } from 'vue'

export default {
  setup() {
    provide(/* key */ 'message', /* value */ 'hello!')
  }
}
```

---

## Inject value using Composition API in Vue.js

This code snippet demonstrates how to inject a value provided by an ancestor component using the `inject` function from Vue.js' Composition API. The `inject` function takes the injection key as an argument and returns the provided value.  Import `inject` from 'vue'.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/provide-inject.md#_snippet_6

```vue
<script setup>
import { inject } from 'vue'

const message = inject('message')
</script>
```

---

## Provide per-instance state using Options API

This code demonstrates how to provide per-instance state in Vue.js' Options API.  The `provide` option should be a function that returns an object containing the provided values. This is necessary to access `this` and provide data defined in the `data()` option. Note that this does not make the injection reactive unless further steps are taken.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/provide-inject.md#_snippet_4

```javascript
export default {
  data() {
    return {
      message: 'hello!'
    }
  },
  provide() {
    // use function syntax so that we can access `this`
    return {
      message: this.message
    }
  }
}
```

---

## Providing Read-Only Data in Vue (Composition API)

This snippet demonstrates providing read-only reactive data using the `readonly` function in Vue.js Composition API.  It provides a `count` ref wrapped in `readonly` to prevent mutation by the injecting component.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/provide-inject.md#_snippet_16

```vue
<script setup>
import { ref, provide, readonly } from 'vue'

const count = ref(0)
provide('read-only-count', readonly(count))
</script>
```

---

## Providing with Symbol Key (Options API)

This snippet demonstrates providing data using a Symbol injection key within the Options API.  It defines the provide option as a function that returns an object, using the Symbol key as a property name.  This ensures type safety and avoids naming conflicts.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/provide-inject.md#_snippet_21

```javascript
// in provider component
import { myInjectionKey } from './keys.js'

export default {
  provide() {
    return {
      [myInjectionKey]: {
        /* data to provide */
      }
    }
  }
}
```

---

## Injection Default Value (Composition API)

This shows how to provide a default value for an injected property using Vue.js Composition API.  If the injection key is not provided in the parent chain, the default value will be used.  The second argument to `inject` is the default value.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/provide-inject.md#_snippet_11

```javascript
// `value` will be "default value"
// if no data matching "message" was provided
const value = inject('message', 'default value')
```

---

## Provide value using Options API in Vue.js

This code snippet demonstrates how to provide a value using the `provide` option in Vue.js' Options API. The `provide` option is an object where keys are injection keys, and values are the values to be provided.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/provide-inject.md#_snippet_3

```javascript
export default {
  provide: {
    message: 'hello!'
  }
}
```

