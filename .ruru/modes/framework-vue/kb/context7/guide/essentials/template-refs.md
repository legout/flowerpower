# Vue.js Template Refs

## Template Ref Attribute Vue HTML

Demonstrates the basic usage of the `ref` attribute in a Vue template. The `ref` attribute allows obtaining a direct reference to a specific DOM element after it's mounted. The value of the `ref` attribute is a string that serves as the reference name.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/template-refs.md#_snippet_0

```html
<input ref="input">
```

---

## Ref on Component (Composition API before 3.5)

Demonstrates using a ref on a child component in Vue versions before 3.5, using Composition API. The code imports `ref`, `onMounted`, and the `Child` component. A ref named `child` is created and initialized to null. The ref is then assigned to the Child component using the `ref` attribute.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/template-refs.md#_snippet_7

```vue
<script setup>
import { ref, onMounted } from 'vue'
import Child from './Child.vue'

const child = ref(null)

onMounted(() => {
  // child.value will hold an instance of <Child />
})
</script>

<template>
  <Child ref="child" />
</template>
```

---

## Exposing Public Interface (Composition API)

Demonstrates how to expose a public interface for a component using `<script setup>` and `defineExpose`. It defines two variables, `a` and `b`, and then uses `defineExpose` to make them accessible to parent components via a template ref.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/template-refs.md#_snippet_9

```vue
<script setup>
import { ref } from 'vue'

const a = 1
const b = ref(2)

// Compiler macros, such as defineExpose, don't need to be imported
defineExpose({
  a,
  b
})
</script>
```

---

## Accessing Refs with Composition API (useTemplateRef)

Illustrates accessing a template ref using the `useTemplateRef()` helper function in the Composition API. It imports `useTemplateRef` and `onMounted` from Vue, defines a ref using `useTemplateRef` with the ref name matching the template, and focuses the input element in the `onMounted` lifecycle hook.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/template-refs.md#_snippet_1

```vue
<script setup>
import { useTemplateRef, onMounted } from 'vue'

// the first argument must match the ref value in the template
const input = useTemplateRef('my-input')

onMounted(() => {
  input.value.focus()
})
</script>

<template>
  <input ref="my-input" />
</template>
```

---

## Limiting Instance Access (Options API)

Demonstrates how to use the `expose` option in the Options API to limit access to a child component's properties and methods from a parent component using a template ref. It defines `publicData`, `privateData`, `publicMethod`, and `privateMethod`, and then exposes only `publicData` and `publicMethod` using the `expose` option.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/template-refs.md#_snippet_10

```javascript
export default {
  expose: ['publicData', 'publicMethod'],
  data() {
    return {
      publicData: 'foo',
      privateData: 'bar'
    }
  },
  methods: {
    publicMethod() {
      /* ... */
    },
    privateMethod() {
      /* ... */
    }
  }
}
```

---

## Refs Inside v-for (Options API)

Illustrates using template refs inside a `v-for` loop using the Options API. It initializes the `list` data property with an array and accesses the corresponding elements through `this.$refs.items` in the `mounted` hook.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/template-refs.md#_snippet_13

```vue
<script>
export default {
  data() {
    return {
      list: [
        /* ... */
      ]
    }
  },
  mounted() {
    console.log(this.$refs.items)
  }
}
</script>

<template>
  <ul>
    <li v-for="item in list" ref="items">
      {{ item }}
    </li>
  </ul>
</template>
```

---

## Accessing Refs with Options API

Demonstrates how to access template refs using the Options API.  It accesses the referenced DOM element through `this.$refs` in the `mounted` lifecycle hook, focusing the input element.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/template-refs.md#_snippet_4

```vue
<script>
export default {
  mounted() {
    this.$refs.input.focus()
  }
}
</script>

<template>
  <input ref="input" />
</template>
```

---

## Function Refs

Demonstrates the usage of function refs, where the `ref` attribute is bound to a function. This function is called on each component update, providing the element reference as the first argument, allowing for flexible storage of the reference.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/template-refs.md#_snippet_14

```html
<input :ref="(el) => { /* assign el to a property or ref */ }">
```

---

## Ref on Component (Options API)

Illustrates how to use `ref` on a child component using the Options API. In the `mounted` hook, `this.$refs.child` is used to access the child component instance.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/template-refs.md#_snippet_8

```vue
<script>
import Child from './Child.vue'

export default {
  components: {
    Child
  },
  mounted() {
    // this.$refs.child will hold an instance of <Child />
  }
}
</script>

<template>
  <Child ref="child" />
</template>
```

---

## Returning Ref from Setup Function

Shows how to return a template ref from the `setup()` function when not using `<script setup>`. It initializes the `input` ref to `null`, and includes the `input` ref in the object returned by the `setup` function, making it accessible in the template.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/template-refs.md#_snippet_3

```javascript
export default {
  setup() {
    const input = ref(null)
    // ...
    return {
      input
    }
  }
}
```

