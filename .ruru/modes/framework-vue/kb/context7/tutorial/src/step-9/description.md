# Vue.js Lifecycle and Template Refs

## Creating a Template Ref in Vue

This code snippet demonstrates how to create a template ref in Vue using the `ref` attribute in the HTML template. The `ref` attribute allows you to obtain a reference to a specific DOM element.

Source: https://github.com/vuejs/docs/blob/main/src/tutorial/src/step-9/description.md#_snippet_0

```vue-html
<p ref="pElementRef">hello</p>
```

---

## Using onMounted Hook (Composition API)

This code demonstrates how to use the `onMounted` lifecycle hook in the Composition API to execute code after the component has been mounted. This hook is useful for performing DOM operations or accessing template refs after the DOM is ready.

Source: https://github.com/vuejs/docs/blob/main/src/tutorial/src/step-9/description.md#_snippet_3

```js
import { onMounted } from 'vue'

onMounted(() => {
  // component is now mounted.
})
```

---

## Accessing Template Ref in setup() (Composition API)

This snippet illustrates how to access and expose a template ref within the `setup()` function of a Vue component using the Composition API. The ref is initialized to `null` and then returned to be accessible in the template.

Source: https://github.com/vuejs/docs/blob/main/src/tutorial/src/step-9/description.md#_snippet_2

```js
setup() {
  const pElementRef = ref(null)

  return {
    pElementRef
  }
}
```

---

## Accessing Template Ref (Composition API)

This snippet shows how to access a template ref in the Composition API within a Vue component. It initializes a ref with `null` and exposes it for access in the template.

Source: https://github.com/vuejs/docs/blob/main/src/tutorial/src/step-9/description.md#_snippet_1

```js
const pElementRef = ref(null)
```

---

## Using mounted Hook (Options API)

This code snippet shows how to use the `mounted` lifecycle hook in the Options API to execute code after the component has been mounted. It is typically used to perform DOM manipulations after initial rendering.

Source: https://github.com/vuejs/docs/blob/main/src/tutorial/src/step-9/description.md#_snippet_5

```js
export default {
  mounted() {
    // component is now mounted.
  }
}
```

---

## Using mounted in createApp (Options API)

This snippet demonstrates using the `mounted` lifecycle hook within a `createApp` instance in the Options API to execute code after the component has been fully mounted within the application.

Source: https://github.com/vuejs/docs/blob/main/src/tutorial/src/step-9/description.md#_snippet_6

```js
createApp({
  mounted() {
    // component is now mounted.
  }
})
```

---

## Using onMounted in createApp (Composition API)

This code illustrates how to use the `onMounted` lifecycle hook within a `createApp` instance using the Composition API. It shows how to ensure code executes after the component has been fully mounted within the application.

Source: https://github.com/vuejs/docs/blob/main/src/tutorial/src/step-9/description.md#_snippet_4

```js
import { onMounted } from 'vue'

createApp({
  setup() {
    onMounted(() => {
      // component is now mounted.
    })
  }
})
```

