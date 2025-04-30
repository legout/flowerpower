# TypeScript with Composition API in Vue.js

## Typing Provide/Inject with InjectionKey in Vue.js

This code snippet demonstrates how to use `InjectionKey` to properly type injected values in Vue.js. It defines a symbol-based injection key and uses it with `provide` and `inject` to ensure type safety between the provider and consumer. Providing a non-string value to `provide` will result in an error due to the type constraint on the `InjectionKey`.

Source: https://github.com/vuejs/docs/blob/main/src/guide/typescript/composition-api.md#_snippet_25

```typescript
import { provide, inject } from 'vue'
import type { InjectionKey } from 'vue'

const key = Symbol() as InjectionKey<string>

provide(key, 'foo') // providing non-string value will result in error

const foo = inject(key) // type of foo: string | undefined
```

---

## Props Definition Using an Interface in Vue

This code shows defining props using an interface for better organization and reusability. An interface `Props` is defined with `foo` as a required string and `bar` as an optional number. This interface is then used as the generic type for `defineProps`.

Source: https://github.com/vuejs/docs/blob/main/src/guide/typescript/composition-api.md#_snippet_2

```vue
<script setup lang="ts">
interface Props {
  foo: string
  bar?: number
}

const props = defineProps<Props>()
</script>
```

---

## Concise Typing for Component Emits in Vue 3.3+

This code snippet shows the more succinct syntax available from Vue 3.3+ for typing component emits using a type literal where values are array/tuple types representing accepted event parameters. Named tuples provide explicit naming for each argument.

Source: https://github.com/vuejs/docs/blob/main/src/guide/typescript/composition-api.md#_snippet_13

```vue
<script setup lang="ts">
// 3.3+: alternative, more succinct syntax
const emit = defineEmits<{  change: [id: number]
  update: [value: string]
}>()
</script>
```

---

## Typing Component Props with defineProps in Vue

This code snippet shows how to define component props with TypeScript using the `defineProps` macro in `<script setup>`. It uses runtime declaration, inferring the props types based on the argument provided to `defineProps()`. The example defines `foo` as a required string and `bar` as an optional number.

Source: https://github.com/vuejs/docs/blob/main/src/guide/typescript/composition-api.md#_snippet_0

```vue
<script setup lang="ts">
const props = defineProps({
  foo: { type: String, required: true },
  bar: Number
})

props.foo // string
props.bar // number | undefined
</script>
```

---

## Overriding Type Inference with ref() in Vue

This example demonstrates how to override the default type inference of `ref()` by passing a generic argument when calling the function. Here, `year` is explicitly defined as `Ref<string | number>`, allowing it to accept both string and number values.

Source: https://github.com/vuejs/docs/blob/main/src/guide/typescript/composition-api.md#_snippet_17

```typescript
// resulting type: Ref<string | number>
const year = ref<string | number>('2020')

year.value = 2020 // ok!
```

---

## Type Inference with ref() in Vue

This code demonstrates how `ref()` infers its type from the initial value.  `year` is inferred to be `Ref<number>`. Subsequent attempts to assign a string value will result in a TypeScript error.

Source: https://github.com/vuejs/docs/blob/main/src/guide/typescript/composition-api.md#_snippet_15

```typescript
import { ref } from 'vue'

// inferred type: Ref<number>
const year = ref(2020)

// => TS Error: Type 'string' is not assignable to type 'number'.
year.value = '2020'
```

---

## Typing Emits with defineComponent in Vue

This example shows how to use `defineComponent()` to type the `emit` function when not using `<script setup>`. `defineComponent` infers the allowed events based on the `emits` option, enabling type checking and autocompletion.

Source: https://github.com/vuejs/docs/blob/main/src/guide/typescript/composition-api.md#_snippet_14

```typescript
import { defineComponent } from 'vue'

export default defineComponent({
  emits: ['change'],
  setup(props, { emit }) {
    emit('change') // <-- type check / auto-completion
  }
})
```

---

## Typing Template Refs with useTemplateRef in Vue.js

This example demonstrates how to explicitly type a template ref using `useTemplateRef` and a generic type argument. This is useful when auto-inference is not possible or when you need to ensure a specific type for the referenced DOM element. Requires Vue 3.5+ and @vue/language-tools 2.1+ for optimal inference.

Source: https://github.com/vuejs/docs/blob/main/src/guide/typescript/composition-api.md#_snippet_29

```typescript
const el = useTemplateRef<HTMLInputElement>('el')
```

---

## Explicitly Typing Reactive Properties in Vue

This snippet shows how to explicitly type a `reactive` property using interfaces. The `book` reactive object is explicitly typed using the `Book` interface, providing type safety for its properties.

Source: https://github.com/vuejs/docs/blob/main/src/guide/typescript/composition-api.md#_snippet_20

```typescript
import { reactive } from 'vue'

interface Book {
  title: string
  year?: number
}

const book: Book = reactive({ title: 'Vue 3 Guide' })
```

---

## Typing Component Emits with Options-Based Declaration in Vue

This example shows how to define component emits with TypeScript using an options-based approach with `defineEmits`. This allows you to specify validation functions for each emitted event.

Source: https://github.com/vuejs/docs/blob/main/src/guide/typescript/composition-api.md#_snippet_11

```vue
<script setup lang="ts">
// options based
const emit = defineEmits({
  change: (id: number) => {
    // return `true` or `false` to indicate
    // validation pass / fail
  },
  update: (value: string) => {
    // return `true` or `false` to indicate
    // validation pass / fail
  }
})
</script>
```

---

## Typing Component Template Refs with InstanceType in Vue.js

This code snippet illustrates how to type a component template ref using `InstanceType` to extract the instance type of an imported component. It showcases a scenario with dynamic components where the ref can point to different component types, and uses a union type to represent the possible instance types. The `useTemplateRef` hook from Vue is utilized.

Source: https://github.com/vuejs/docs/blob/main/src/guide/typescript/composition-api.md#_snippet_31

```vue
<!-- App.vue -->
<script setup lang="ts">
import { useTemplateRef } from 'vue'
import Foo from './Foo.vue'
import Bar from './Bar.vue'

type FooType = InstanceType<typeof Foo>
type BarType = InstanceType<typeof Bar>

const compRef = useTemplateRef<FooType | BarType>('comp')
</script>

<template>
  <component :is="Math.random() > 0.5 ? Foo : Bar" ref="comp" />
</template>
```

---

## Type-Based Props Declaration with defineProps in Vue

This code snippet demonstrates defining component props using a generic type argument in `defineProps`. This method allows for a cleaner and more straightforward way to define props types, where the compiler infers runtime options based on the type argument. `foo` is defined as a string and `bar` as an optional number.

Source: https://github.com/vuejs/docs/blob/main/src/guide/typescript/composition-api.md#_snippet_1

```vue
<script setup lang="ts">
const props = defineProps<{  foo: string
  bar?: number
}>()
</script>
```

---

## Props Default Values with withDefaults in Vue

This code demonstrates using the `withDefaults` compiler macro to define default values for props. It provides type checks for the default values and ensures the returned `props` type has optional flags removed for properties that have default values declared. Mutable reference types should be wrapped in functions to avoid accidental modification.

Source: https://github.com/vuejs/docs/blob/main/src/guide/typescript/composition-api.md#_snippet_5

```typescript
interface Props {
  msg?: string
  labels?: string[]
}

const props = withDefaults(defineProps<Props>(), {
  msg: 'hello',
  labels: () => ['one', 'two']
})
```

---

## Generic Component Definition

Defines a generic Vue component `MyGenericModal` that accepts a type parameter `ContentType`.  It uses `defineExpose` to expose the `open` method, which takes a value of type `ContentType` and sets the component's internal `content` ref.  This component requires the `vue` library.

Source: https://github.com/vuejs/docs/blob/main/src/guide/typescript/composition-api.md#_snippet_34

```vue
<!-- MyGenericModal.vue -->
<script setup lang="ts" generic="ContentType extends string | number">
import { ref } from 'vue'

const content = ref<ContentType | null>(null)

const open = (newContent: ContentType) => (content.value = newContent)

defineExpose({
  open
})
</script>
```

---

## Props Default Values with Reactive Props Destructure in Vue

This snippet illustrates how to set default values for props using Reactive Props Destructure. This approach allows specifying default values directly within the destructuring assignment, providing a concise way to define defaults for optional props.

Source: https://github.com/vuejs/docs/blob/main/src/guide/typescript/composition-api.md#_snippet_4

```typescript
interface Props {
  msg?: string
  labels?: string[]
}

const { msg = 'hello', labels = ['one', 'two'] } = defineProps<Props>()
```

---

## Typing Event Handlers with Type Assertion in Vue

This code demonstrates typing an event handler and using type assertions to access properties of the event target.  The `event` argument is explicitly typed as `Event`, and a type assertion is used to treat `event.target` as an `HTMLInputElement` to access the `value` property.

Source: https://github.com/vuejs/docs/blob/main/src/guide/typescript/composition-api.md#_snippet_24

```typescript
function handleChange(event: Event) {
  console.log((event.target as HTMLInputElement).value)
}
```

---

## Specifying Explicit Type with computed() in Vue

This shows how to specify an explicit type for a computed property via a generic argument.  The compiler will check that the getter function returns the specified type.

Source: https://github.com/vuejs/docs/blob/main/src/guide/typescript/composition-api.md#_snippet_22

```typescript
const double = computed<number>(() => {
  // type error if this doesn't return a number
})
```

---

## Typing Component Emits with Runtime Declaration in Vue

This snippet demonstrates typing component emits using the `defineEmits` macro with runtime declaration. It specifies the event names as an array of strings.

Source: https://github.com/vuejs/docs/blob/main/src/guide/typescript/composition-api.md#_snippet_10

```vue
<script setup lang="ts">
// runtime
const emit = defineEmits(['change', 'update'])
</script>
```

---

## Type Inference with defineComponent for Props in Vue

This example shows how to use `defineComponent()` when not using `<script setup>` to enable props type inference. The type of the props object passed to `setup()` is inferred from the `props` option.

Source: https://github.com/vuejs/docs/blob/main/src/guide/typescript/composition-api.md#_snippet_6

```typescript
import { defineComponent } from 'vue'

export default defineComponent({
  props: {
    message: String
  },
  setup(props) {
    props.message // <-- type: string
  }
})
```

---

## ref() with Generic Type and no Initial Value in Vue

This shows what happens when you specify a generic type argument to `ref()` but omit the initial value. The resulting type will be a union type that includes `undefined`.

Source: https://github.com/vuejs/docs/blob/main/src/guide/typescript/composition-api.md#_snippet_18

```typescript
// inferred type: Ref<number | undefined>
const n = ref<number>()
```

---

## Complex Prop Types with Options API in Vue

This code shows defining a complex prop type with `defineComponent` using the Options API. It uses `PropType` to define the type of the `book` prop as a `Book` object. This method is commonly used when working with the Options API.

Source: https://github.com/vuejs/docs/blob/main/src/guide/typescript/composition-api.md#_snippet_9

```typescript
import { defineComponent } from 'vue'
import type { PropType } from 'vue'

export default defineComponent({
  props: {
    book: Object as PropType<Book>
  }
})
```

---

## Typing Provide/Inject with String Keys in Vue.js

This code snippet shows how to type injected values when using string injection keys in Vue.js.  Since string keys result in an `unknown` type, a generic type argument is used with `inject` to explicitly declare the type. The injected value can be undefined if no provider is present, requiring a default value or a type assertion.

Source: https://github.com/vuejs/docs/blob/main/src/guide/typescript/composition-api.md#_snippet_26

```typescript
const foo = inject<string>('foo') // type: string | undefined
```

---

## Force Casting Injected Values in Vue.js

This code snippet demonstrates force casting an injected value when you are certain that the value is always provided.  This avoids potential `undefined` issues. Note that this approach should be used cautiously, only when you are absolutely sure that the value will be provided at runtime.

Source: https://github.com/vuejs/docs/blob/main/src/guide/typescript/composition-api.md#_snippet_28

```typescript
const foo = inject('foo') as string
```

---

## Typing Component Emits with Type-Based Declaration in Vue

This code snippet demonstrates typing component emits using type-based declaration, providing fine-grained control over the type constraints of emitted events using call signatures in a type literal.

Source: https://github.com/vuejs/docs/blob/main/src/guide/typescript/composition-api.md#_snippet_12

```vue
<script setup lang="ts">
// type-based
const emit = defineEmits<{  (e: 'change', id: number): void
  (e: 'update', value: string): void
}>()
</script>
```

---

## Typing Generic Component Template Refs with ComponentExposed in Vue.js

This code demonstrates how to type template refs for generic components using `ComponentExposed` from the `vue-component-type-helpers` library. It is required because `InstanceType` doesn't work for generic components. It imports `useTemplateRef` from vue, `MyGenericModal` component, and `ComponentExposed` from `vue-component-type-helpers`.

Source: https://github.com/vuejs/docs/blob/main/src/guide/typescript/composition-api.md#_snippet_33

```vue
<!-- App.vue -->
<script setup lang="ts">
import { useTemplateRef } from 'vue'
import MyGenericModal from './MyGenericModal.vue'
import type { ComponentExposed } from 'vue-component-type-helpers'

const modal = useTemplateRef<ComponentExposed<typeof MyGenericModal>>('modal')

const openModal = () => {
  modal.value?.open('newValue')
}
</script>
```

---

## Typing Event Handlers in Vue

This example illustrates typing event handlers in Vue components. Without type annotation, the `event` argument implicitly has a type of `any`. It's recommended to explicitly annotate the event handler's argument for type safety and to avoid potential TS errors when `strict` or `noImplicitAny` are enabled.

Source: https://github.com/vuejs/docs/blob/main/src/guide/typescript/composition-api.md#_snippet_23

```vue
<script setup lang="ts">
function handleChange(event) {
  // `event` implicitly has `any` type
  console.log(event.target.value)
}
</script>

<template>
  <input type="text" @change="handleChange" />
</template>
```

---

## Type Inference with reactive() in Vue

This code demonstrates how `reactive()` implicitly infers the type from its argument. In this example, `book` is inferred to be of type `{ title: string }`.

Source: https://github.com/vuejs/docs/blob/main/src/guide/typescript/composition-api.md#_snippet_19

```typescript
import { reactive } from 'vue'

// inferred type: { title: string }
const book = reactive({ title: 'Vue 3 Guide' })
```

