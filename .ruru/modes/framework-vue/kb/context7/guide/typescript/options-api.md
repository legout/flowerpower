# TypeScript with Options API in Vue.js

## Augmenting Global Properties in Vue.js with TypeScript

This snippet explains how to augment global properties added to component instances via `app.config.globalProperties` in Vue.js using TypeScript module augmentation. It shows how to declare a module 'vue' and extend the `ComponentCustomProperties` interface to include the types of globally available properties, enabling type-safe access to these properties within components.

Source: https://github.com/vuejs/docs/blob/main/src/guide/typescript/options-api.md#_snippet_6

```typescript
import axios from 'axios'

declare module 'vue' {
  interface ComponentCustomProperties {
    $http: typeof axios
    $translate: (key: string) => string
  }
}
```

---

## Typing Component Props with defineComponent in Vue.js

This snippet demonstrates how to enable type inference for component props in Vue.js Options API using `defineComponent()`. It shows how Vue infers types based on the `props` option, including `required: true` and `default` settings. It covers basic types like String, Number, and String, as well as the `null` type.

Source: https://github.com/vuejs/docs/blob/main/src/guide/typescript/options-api.md#_snippet_0

```typescript
import { defineComponent } from 'vue'

export default defineComponent({
  // type inference enabled
  props: {
    name: String,
    id: [Number, String],
    msg: { type: String, required: true },
    metadata: null
  },
  mounted() {
    this.name // type: string | undefined
    this.id // type: number | string | undefined
    this.msg // type: string
    this.metadata // type: any
  }
})
```

---

## Typing Computed Properties in Vue.js

This snippet demonstrates how a computed property infers its type based on its return value in Vue.js. It shows a basic example where the `greeting` computed property's type is inferred from its return value, a string. It also shows how to explicitly annotate the return type of a computed property and how to annotate a writable computed property.

Source: https://github.com/vuejs/docs/blob/main/src/guide/typescript/options-api.md#_snippet_4

```typescript
import { defineComponent } from 'vue'

export default defineComponent({
  data() {
    return {
      message: 'Hello!'
    }
  },
  computed: {
    greeting() {
      return this.message + '!'
    }
  },
  mounted() {
    this.greeting // type: string
  }
})
```

```typescript
import { defineComponent } from 'vue'

export default defineComponent({
  data() {
    return {
      message: 'Hello!'
    }
  },
  computed: {
    // explicitly annotate return type
    greeting(): string {
      return this.message + '!'
    },

    // annotating a writable computed property
    greetingUppercased: {
      get(): string {
        return this.greeting.toUpperCase()
      },
      set(newValue: string) {
        this.message = newValue.toUpperCase()
      }
    }
  }
})
```

---

## Typing Event Handlers in Vue.js

This snippet shows how to properly type event handlers in Vue.js when dealing with native DOM events. It highlights the importance of explicitly annotating the `event` argument and using type assertions when accessing properties of `event` to avoid implicit `any` types and potential TypeScript errors.

Source: https://github.com/vuejs/docs/blob/main/src/guide/typescript/options-api.md#_snippet_5

```vue
<script lang="ts">
import { defineComponent } from 'vue'

export default defineComponent({
  methods: {
    handleChange(event) {
      // `event` implicitly has `any` type
      console.log(event.target.value)
    }
  }
})
</script>

<template>
  <input type="text" @change="handleChange" />
</template>
```

```typescript
import { defineComponent } from 'vue'

export default defineComponent({
  methods: {
    handleChange(event: Event) {
      console.log((event.target as HTMLInputElement).value)
    }
  }
})
```

---

## Annotating Complex Prop Types in Vue.js

This snippet illustrates how to annotate complex prop types in Vue.js, such as objects with nested properties or function call signatures, using the `PropType` utility type. It provides an example of defining a `Book` interface and using it to type the `book` prop, along with an example of typing a callback function.

Source: https://github.com/vuejs/docs/blob/main/src/guide/typescript/options-api.md#_snippet_1

```typescript
import { defineComponent } from 'vue'
import type { PropType } from 'vue'

interface Book {
  title: string
  author: string
  year: number
}

export default defineComponent({
  props: {
    book: {
      // provide more specific type to `Object`
      type: Object as PropType<Book>,
      required: true
    },
    // can also annotate functions
    callback: Function as PropType<(id: number) => void>
  },
  mounted() {
    this.book.title // string
    this.book.year // number

    // TS Error: argument of type 'string' is not
    // assignable to parameter of type 'number'
    this.callback?.('123')
  }
})
```

---

## Validator and Default Prop Options Caveats in Vue.js

This snippet addresses caveats related to using function values for `validator` and `default` prop options in TypeScript versions less than 4.7. It demonstrates the importance of using arrow functions to prevent TypeScript from failing to infer the type of `this` inside these functions.

Source: https://github.com/vuejs/docs/blob/main/src/guide/typescript/options-api.md#_snippet_2

```typescript
import { defineComponent } from 'vue'
import type { PropType } from 'vue'

interface Book {
  title: string
  year?: number
}

export default defineComponent({
  props: {
    bookA: {
      type: Object as PropType<Book>,
      // Make sure to use arrow functions if your TypeScript version is less than 4.7
      default: () => ({
        title: 'Arrow Function Expression'
      }),
      validator: (book: Book) => !!book.title
    }
  }
})
```

---

## Typing Component Emits in Vue.js

This snippet explains how to declare the expected payload type for an emitted event using the object syntax of the `emits` option. It also highlights that all non-declared emitted events will throw a type error when called, enforcing type safety for event emissions.

Source: https://github.com/vuejs/docs/blob/main/src/guide/typescript/options-api.md#_snippet_3

```typescript
import { defineComponent } from 'vue'

export default defineComponent({
  emits: {
    addBook(payload: { bookName: string }) {
      // perform runtime validation
      return payload.bookName.length > 0
    }
  },
  methods: {
    onSubmit() {
      this.$emit('addBook', {
        bookName: 123 // Type error!
      })

      this.$emit('non-declared-event') // Type error!
    }
  }
})
```

---

## Type Augmentation Placement in Vue.js

This snippet demonstrates the correct way to place TypeScript type augmentations for Vue.js. It emphasizes the necessity of placing the augmentation inside a TypeScript module (a file with at least one top-level import or export) to avoid overwriting the original types, ensuring proper augmentation instead.

Source: https://github.com/vuejs/docs/blob/main/src/guide/typescript/options-api.md#_snippet_8

```typescript
// Does not work, overwrites the original types.
declare module 'vue' {
  interface ComponentCustomProperties {
    $translate: (key: string) => string
  }
}
```

```typescript
// Works correctly
export {}

declare module 'vue' {
  interface ComponentCustomProperties {
    $translate: (key: string) => string
  }
}
```

---

## Augmenting Custom Options in Vue.js with TypeScript

This snippet shows how to augment the `ComponentCustomOptions` interface in Vue.js to support custom component options provided by plugins, such as `beforeRouteEnter` from `vue-router`.  It allows you to properly type the arguments of these custom options, ensuring type safety when using plugins that extend component options.

Source: https://github.com/vuejs/docs/blob/main/src/guide/typescript/options-api.md#_snippet_7

```typescript
import { defineComponent } from 'vue'

export default defineComponent({
  beforeRouteEnter(to, from, next) {
    // ...
  }
})

```

```typescript
import { Route } from 'vue-router'

declare module 'vue' {
  interface ComponentCustomOptions {
    beforeRouteEnter?(to: Route, from: Route, next: () => void): void
  }
}
```

