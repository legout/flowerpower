# Vue.js Built-in Special Elements Documentation

## Rendering Built-in Components by Name in Vue

Demonstrates how to register and use built-in components like `Transition` and `TransitionGroup` with the `<component>` tag. The `is` prop is bound to the component name, which necessitates registration in the `components` option.

Source: https://github.com/vuejs/docs/blob/main/src/api/built-in-special-elements.md#_snippet_4

```vue
<script>
import { Transition, TransitionGroup } from 'vue'

export default {
  components: {
    Transition,
    TransitionGroup
  }
}
</script>

<template>
  <component :is="isGroup ? 'TransitionGroup' : 'Transition'">
    ...
  </component>
</template>
```

---

## Defining Slot Props Interface in TypeScript

Defines the TypeScript interface `SlotProps` for the properties that can be passed to a `<slot>` element. It includes properties for scoped slots and a reserved property for the slot name.

Source: https://github.com/vuejs/docs/blob/main/src/api/built-in-special-elements.md#_snippet_6

```typescript
interface SlotProps {
  /**
   * Any props passed to <slot> to passed as arguments
   * for scoped slots
   */
  [key: string]: any
  /**
   * Reserved for specifying slot name.
   */
  name?: string
}
```

---

## Rendering Component by Registered Name in Vue (Options API)

Demonstrates rendering a dynamic component using the `is` prop of the `<component>` element. The `view` data property determines which component (Foo or Bar) is rendered based on its registered name in the components option.

Source: https://github.com/vuejs/docs/blob/main/src/api/built-in-special-elements.md#_snippet_1

```vue
<script>
import Foo from './Foo.vue'
import Bar from './Bar.vue'

export default {
  components: { Foo, Bar },
  data() {
    return {
      view: 'Foo'
    }
  }
}
</script>

<template>
  <component :is="view" />
</template>
```

---

## Rendering HTML Elements Dynamically in Vue

Demonstrates rendering different HTML elements dynamically using the `is` prop of the `<component>` element. The example switches between an `<a>` tag (if `href` is truthy) and a `<span>` tag.

Source: https://github.com/vuejs/docs/blob/main/src/api/built-in-special-elements.md#_snippet_3

```vue-html
<component :is="href ? 'a' : 'span'"></component>
```

