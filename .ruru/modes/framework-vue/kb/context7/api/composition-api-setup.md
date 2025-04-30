# Vue.js Composition API setup() Hook

## Basic setup() Usage in Vue.js

Demonstrates the basic usage of the `setup()` hook in a Vue.js component to declare reactive state using `ref` and expose it to the template and other options API hooks. Includes a simple counter example.

Source: https://github.com/vuejs/docs/blob/main/src/api/composition-api-setup.md#_snippet_0

```vue
<script>
import { ref } from 'vue'

export default {
  setup() {
    const count = ref(0)

    // expose to template and other options API hooks
    return {
      count
    }
  },

  mounted() {
    console.log(this.count) // 0
  }
}
</script>

<template>
  <button @click="count++">{{ count }}</button>
</template>
```

---

## setup() with Render Functions

Demonstrates using `setup()` to return a render function directly, allowing the render function to use reactive state declared in the same scope.  Also demonstrates using `expose()` to expose methods when returning a render function.

Source: https://github.com/vuejs/docs/blob/main/src/api/composition-api-setup.md#_snippet_5

```javascript
import { h, ref } from 'vue'

export default {
  setup() {
    const count = ref(0)
    return () => h('div', count.value)
  }
}
```

```javascript
import { h, ref } from 'vue'

export default {
  setup(props, { expose }) {
    const count = ref(0)
    const increment = () => ++count.value

    expose({
      increment
    })

    return () => h('div', count.value)
  }
}
```

---

## Accessing Props in setup()

Illustrates how to access props within the `setup()` function in a Vue.js component. It highlights that props are reactive and updated when new props are passed in, and recommends accessing props as `props.xxx` to maintain reactivity.

Source: https://github.com/vuejs/docs/blob/main/src/api/composition-api-setup.md#_snippet_1

```javascript
export default {
  props: {
    title: String
  },
  setup(props) {
    console.log(props.title)
  }
}
```

---

## Destructuring Props with toRefs()

Shows how to destructure props while retaining reactivity using `toRefs()` and `toRef()` utility APIs.  `toRefs` converts the props object into an object of refs, while `toRef` converts a single prop into a ref.

Source: https://github.com/vuejs/docs/blob/main/src/api/composition-api-setup.md#_snippet_2

```javascript
import { toRefs, toRef } from 'vue'

export default {
  setup(props) {
    // turn `props` into an object of refs, then destructure
    const { title } = toRefs(props)
    // `title` is a ref that tracks `props.title`
    console.log(title.value)

    // OR, turn a single property on `props` into a ref
    const title = toRef(props, 'title')
  }
}
```

