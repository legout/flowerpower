# Vue.js Component Options: Rendering

## Component Slots Type Definition - Vue.js

Explains the structure for defining type-safe slots in Vue.js components. The `slots` option is used to assist type inference in render functions when working with slots programmatically.  The actual types for the slots are defined using type casting along with the `SlotsType` type helper. This functionality is available in Vue 3.3 and later.

Source: https://github.com/vuejs/docs/blob/main/src/api/options-rendering.md#_snippet_3

```typescript
import { SlotsType } from 'vue'

defineComponent({
  slots: Object as SlotsType<{
    default: { foo: string; bar: number }
    item: { data: number }
  }>,
  setup(props, { slots }) {
    expectType<
      undefined | ((scope: { foo: string; bar: number }) => any)
    >(slots.default)
    expectType<undefined | ((scope: { data: number }) => any)>(
      slots.item
    )
  }
})
```

---

## Component Compiler Options Definition - Vue.js

Illustrates the structure of the `compilerOptions` object within a Vue component. These options allow for customizing the runtime template compilation behavior, like custom element handling, whitespace management, custom delimiters, and comment handling. These options are only relevant with a full build of Vue.js, which includes the template compiler.

Source: https://github.com/vuejs/docs/blob/main/src/api/options-rendering.md#_snippet_2

```typescript
interface ComponentOptions {
  compilerOptions?: {
    isCustomElement?: (tag: string) => boolean
    whitespace?: 'condense' | 'preserve' // default: 'condense'
    delimiters?: [string, string] // default: ['{{', '}}']
    comments?: boolean // default: false
  }
}
```

---

## Component Template String Definition - Vue.js

Defines the structure of the `template` option within a Vue component, specifying that it accepts a string value representing the component's template. The template is used to generate the component's DOM structure at runtime, if a compiler is available. It is important to trust the source of the template to avoid security vulnerabilities.

Source: https://github.com/vuejs/docs/blob/main/src/api/options-rendering.md#_snippet_0

```typescript
interface ComponentOptions {
  template?: string
}
```

