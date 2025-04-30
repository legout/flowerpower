# Vue.js Reactivity Fundamentals

## Exposing ref to Template - Composition API - JavaScript

Shows how to expose a `ref` to a component's template by declaring it within the `setup()` function and returning it. When using refs in templates, the `.value` property is automatically unwrapped.
Dependencies: Vue.js

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/reactivity-fundamentals.md#_snippet_4

```JavaScript
import { ref } from 'vue'

export default {
  // `setup` is a special hook dedicated for the Composition API.
  setup() {
    const count = ref(0)

    // expose the ref to the template
    return {
      count
    }
  }
}
```

---

## Declaring Reactive State with ref() - Composition API - JavaScript

Shows how to declare reactive state using the `ref()` function in the Composition API.  `ref()` wraps the argument in a ref object with a `.value` property, which must be accessed to get or set the value. The ref needs to be declared and returned from the component's `setup()` function to be accessed in the template.
Dependencies: Vue.js

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/reactivity-fundamentals.md#_snippet_2

```JavaScript
import { ref } from 'vue'

const count = ref(0)
```

---

## Deep Reactivity with Composition API in Vue

This example illustrates deep reactivity using the Composition API in Vue. The `ref` function is used to create a reactive object `obj`. The `mutateDeeply` function modifies nested properties within `obj`, and Vue automatically detects these changes.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/reactivity-fundamentals.md#_snippet_14

```javascript
import { ref } from 'vue'

const obj = ref({
  nested: { count: 0 },
  arr: ['foo', 'bar']
})

function mutateDeeply() {
  // these will work as expected.
  obj.value.nested.count++
  obj.value.arr.push('baz')
}
```

---

## Using reactive state in Vue templates

This example shows how to use the state created with `reactive()` in a Vue template. The `state.count` property is accessed and mutated directly within the template using data binding and event handling.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/reactivity-fundamentals.md#_snippet_18

```vue-html
<button @click="state.count++">
  {{ state.count }}
</button>
```

---

## Using Exposed Method as Event Handler - Composition API - HTML

Example of how to use the method exposed above in a Vue HTML template. This displays the usage of the increment function within the template.
Dependencies: Vue.js

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/reactivity-fundamentals.md#_snippet_8

```Vue
<button @click="increment">
  {{ count }}
</button>
```

---

## Declaring Reactive State with reactive() in Vue

This example shows how to use the `reactive()` API to create reactive state in Vue. The `reactive()` function takes an object and returns a reactive proxy of that object, allowing Vue to track changes to its properties.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/reactivity-fundamentals.md#_snippet_17

```javascript
import { reactive } from 'vue'

const state = reactive({ count: 0 })
```

---

## Declaring Reactive State - Options API - JavaScript

Demonstrates how to declare reactive state using the `data` option in the Options API.  The `data` option should be a function that returns an object. Vue wraps the returned object in its reactivity system, allowing access to its properties via `this` in methods and lifecycle hooks.
Dependencies: Vue.js

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/reactivity-fundamentals.md#_snippet_0

```JavaScript
export default {
  data() {
    return {
      count: 1
    }
  },

  // `mounted` is a lifecycle hook which we will explain later
  mounted() {
    // `this` refers to the component instance.
    console.log(this.count) // => 1

    // data can be mutated as well
    this.count = 2
  }
}
```

---

## Accessing ref Value - Composition API - JavaScript

Demonstrates accessing and mutating the value of a `ref` object using the `.value` property. It highlights the difference between accessing the `ref` object itself and its value.
Dependencies: Vue.js

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/reactivity-fundamentals.md#_snippet_3

```JavaScript
const count = ref(0)

console.log(count) // { value: 0 }
console.log(count.value) // 0

count.value++
console.log(count.value) // 1
```

---

## Declaring Methods - Options API - JavaScript

Demonstrates how to add methods to a component instance using the `methods` option in the Options API. Vue automatically binds the `this` value for methods, ensuring it refers to the component instance. Arrow functions should be avoided when defining methods to preserve the correct `this` binding.
Dependencies: Vue.js

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/reactivity-fundamentals.md#_snippet_10

```JavaScript
export default {
  data() {
    return {
      count: 0
    }
  },
  methods: {
    increment() {
      this.count++
    }
  },
  mounted() {
    // methods can be called in lifecycle hooks, or other methods!
    this.increment()
  }
}
```

---

## Deep Reactivity with Options API in Vue

This example demonstrates how Vue's reactivity system automatically detects changes to nested objects and arrays when using the Options API. The `mutateDeeply` method modifies the `obj` and `arr` properties, which triggers reactivity updates.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/reactivity-fundamentals.md#_snippet_13

```javascript
export default {
  data() {
    return {
      obj: {
        nested: { count: 0 },
        arr: ['foo', 'bar']
      }
    }
  },
  methods: {
    mutateDeeply() {
      // these will work as expected.
      this.obj.nested.count++
      this.obj.arr.push('baz')
    }
  }
}
```

---

## Ref Unwrapping After Destructuring in Template

Demonstrates ref unwrapping in a Vue template after destructuring the `id` property into a top-level property.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/reactivity-fundamentals.md#_snippet_28

```vue-html
{{ id + 1 }}
```

---

## Creating Instance-Specific Debounced Method in Vue

This code snippet shows the recommended approach to create a debounced method within a Vue component using the `created` lifecycle hook. This ensures that each component instance has its own independent copy of the debounced function, preventing interference. The timer is also canceled in the `unmounted` lifecycle hook.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/reactivity-fundamentals.md#_snippet_31

```JavaScript
export default {
  created() {
    // each instance now has its own copy of debounced handler
    this.debouncedClick = _.debounce(this.click, 500)
  },
  unmounted() {
    // also a good idea to cancel the timer
    // when the component is removed
    this.debouncedClick.cancel()
  },
  methods: {
    click() {
      // ... respond to click ...
    }
  }
}
```

---

## Reactive Proxy vs. Original Object

This snippet highlights that `reactive()` returns a proxy, not the original object. Modifying the original object will not trigger reactivity, reinforcing the need to work exclusively with the proxy returned by `reactive()`.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/reactivity-fundamentals.md#_snippet_19

```javascript
const raw = {}
const proxy = reactive(raw)

// proxy is NOT equal to the original.
console.log(proxy === raw) // false
```

---

## script setup Example - Composition API - Vue

Example of using `<script setup>` to simplify Composition API usage in Single-File Components (SFCs). Top-level imports, variables, and functions declared within `<script setup>` are automatically available in the template.
Dependencies: Vue.js

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/reactivity-fundamentals.md#_snippet_9

```Vue
<script setup>
import { ref } from 'vue'

const count = ref(0)

function increment() {
  count.value++
}
</script>

<template>
  <button @click="increment">
    {{ count }}
  </button>
</template>
```

---

## Nested Reactive Objects

Illustrates that nested objects within a reactive object are also proxies due to Vue's deep reactivity.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/reactivity-fundamentals.md#_snippet_21

```javascript
const proxy = reactive({})

const raw = {}
proxy.nested = raw

console.log(proxy.nested === raw) // false
```

---

## Ref Unwrapping in Templates (Not Top-Level Property)

Illustrates that ref unwrapping does not apply if the ref is not a top-level property in the template render context. `object.id` is not unwrapped and remains a ref object, requiring explicit unwrapping or destructuring.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/reactivity-fundamentals.md#_snippet_26

```vue-html
{{ object.id + 1 }}
```

---

## Declaring Methods to Mutate ref - Composition API - JavaScript

Illustrates declaring a function within the `setup()` function to mutate a `ref` and exposing the function as a method.  The `.value` property is needed within the JavaScript function to modify the ref. The function then needs to be returned to be used within the template.
Dependencies: Vue.js

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/reactivity-fundamentals.md#_snippet_7

```JavaScript
import { ref } from 'vue'

export default {
  setup() {
    const count = ref(0)

    function increment() {
      // .value is needed in JavaScript
      count.value++
    }

    // don't forget to expose the function as well.
    return {
      count,
      increment
    }
  }
}
```

---

## Mutating ref in Event Handlers - Composition API - HTML

Demonstrates mutating a `ref` directly in an event handler within a Vue template. This showcases how to directly modify the ref's value in response to user interactions.
Dependencies: Vue.js

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/reactivity-fundamentals.md#_snippet_6

```Vue
<button @click="count++">
  {{ count }}
</button>
```

