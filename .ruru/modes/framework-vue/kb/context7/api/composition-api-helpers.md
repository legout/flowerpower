# Vue Composition API Helpers Documentation

## useModel() Usage Example - JavaScript

Demonstrates how to use `useModel()` within a component's setup function in JavaScript. It shows how to bind a prop named 'count' using `useModel` and update its value. This snippet requires the `props` to be defined along with corresponding `emits`.

Source: https://github.com/vuejs/docs/blob/main/src/api/composition-api-helpers.md#_snippet_3

```javascript
export default {
    props: ['count'],
    emits: ['update:count'],
    setup(props) {
      const msg = useModel(props, 'count')
      msg.value = 1
    }
  }
```

---

## useId() Usage Example - Vue

Illustrates how to use `useId()` within a `<script setup>` component to generate a unique ID for a form element's label and input. This ensures proper association between the label and input, improving accessibility.

Source: https://github.com/vuejs/docs/blob/main/src/api/composition-api-helpers.md#_snippet_7

```vue
<script setup>
  import { useId } from 'vue'

  const id = useId()
  </script>

  <template>
    <form>
      <label :for="id">Name:</label>
      <input :id="id" type="text" />
    </form>
  </template>
```

---

## useTemplateRef() Usage Example - Vue

Demonstrates how to use `useTemplateRef()` in a `<script setup>` component to access a template element. In this example, `useTemplateRef('input')` is used to get a reference to an `<input>` element with `ref="input"` in the template, and then `focus()` is called on the element after the component is mounted.

Source: https://github.com/vuejs/docs/blob/main/src/api/composition-api-helpers.md#_snippet_5

```vue
<script setup>
  import { useTemplateRef, onMounted } from 'vue'

  const inputRef = useTemplateRef('input')

  onMounted(() => {
    inputRef.value.focus()
  })
  </script>

  <template>
    <input ref="input" />
  </template>
```

---

## useModel() Type Definition - TypeScript

Defines the type definitions for the `useModel()` function and related types `DefineModelOptions` and `ModelRef`. `useModel()` is a helper function underlying `defineModel()` and is available in Vue 3.4+. It allows for creating a two-way binding ref.

Source: https://github.com/vuejs/docs/blob/main/src/api/composition-api-helpers.md#_snippet_2

```typescript
function useModel(
    props: Record<string, any>,
    key: string,
    options?: DefineModelOptions
  ): ModelRef

  type DefineModelOptions<T = any> = {
    get?: (v: T) => any
    set?: (v: T) => any
  }

  type ModelRef<T, M extends PropertyKey = string, G = T, S = T> = Ref<G, S> & [
    ModelRef<T, M, G, S>,
    Record<M, true | undefined>
  ]
```

---

## useId() Type Definition - TypeScript

Displays the type definition for the `useId()` function, which is used to generate unique application-wide IDs. This function doesn't take any arguments and returns a string which represents the unique ID.

Source: https://github.com/vuejs/docs/blob/main/src/api/composition-api-helpers.md#_snippet_6

```typescript
function useId(): string
```

