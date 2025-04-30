# Vue.js Utility Types Documentation

## Augmenting Component Options in Vue.js

Illustrates how to use declaration merging to augment the `ComponentCustomOptions` interface, allowing you to add custom options to the Vue component definition.  This is useful for adding custom lifecycle hooks or other component-specific configurations.

Source: https://github.com/vuejs/docs/blob/main/src/api/utility-types.md#_snippet_4

```typescript
import { Route } from 'vue-router'

declare module 'vue' {
  interface ComponentCustomOptions {
    beforeRouteEnter?(to: any, from: any, next: () => void): void
  }
}
```

---

## Extracting Public Prop Types in Vue.js

Shows how to use `ExtractPublicPropTypes` to extract the public prop types from a runtime props options object, representing the props that the parent component is allowed to pass. This utility type is available in Vue 3.3+.

Source: https://github.com/vuejs/docs/blob/main/src/api/utility-types.md#_snippet_2

```typescript
const propsOptions = {
  foo: String,
  bar: Boolean,
  baz: {
    type: Number,
    required: true
  },
  qux: {
    type: Number,
    default: 1
  }
} as const

type Props = ExtractPublicPropTypes<typeof propsOptions>
// {
//   foo?: string,
//   bar?: boolean,
//   baz: number,
//   qux?: number
// }
```

---

## Extracting Internal Prop Types in Vue.js

Illustrates how to use `ExtractPropTypes` to extract the internal prop types from a runtime props options object. The extracted types include resolved props received by the component, considering boolean props and props with default values which are always defined.

Source: https://github.com/vuejs/docs/blob/main/src/api/utility-types.md#_snippet_1

```typescript
const propsOptions = {
  foo: String,
  bar: Boolean,
  baz: {
    type: Number,
    required: true
  },
  qux: {
    type: Number,
    default: 1
  }
} as const

type Props = ExtractPropTypes<typeof propsOptions>
// {
//   foo?: string,
//   bar: boolean,
//   baz: number,
//   qux: number
// }
```

---

## Augmenting TSX Props in Vue.js

Shows how to augment allowed TSX props using `ComponentCustomProps` to enable the usage of non-declared props on TSX elements. This is particularly useful when working with third-party components or libraries that might not have complete type definitions.

Source: https://github.com/vuejs/docs/blob/main/src/api/utility-types.md#_snippet_5

```typescript
declare module 'vue' {
  interface ComponentCustomProps {
    hello?: string
  }
}

export {}
```

```typescript
// now works even if hello is not a declared prop
<MyComponent hello="world" />
```

---

## Augmenting CSS Properties in Vue.js

Demonstrates how to augment the `CSSProperties` interface to allow custom CSS properties to be used in style bindings. This enables the use of CSS variables with type checking in Vue templates.

Source: https://github.com/vuejs/docs/blob/main/src/api/utility-types.md#_snippet_6

```typescript
declare module 'vue' {
  interface CSSProperties {
    [key: `--${string}`]: string
  }
}
```

```typescript
<div style={ { '--bg-color': 'blue' } }>
```

```typescript
<div :style="{ '--bg-color': 'blue' }"></div>
```

