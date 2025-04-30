# Vue.js SFC Script Setup Documentation

## Define Props and Emits Vue

Shows how to declare options like `props` and `emits` with full type inference support using the `defineProps` and `defineEmits` APIs inside `<script setup>`. These are compiler macros and do not need to be imported.

Source: https://github.com/vuejs/docs/blob/main/src/api/sfc-script-setup.md#_snippet_10

```vue
<script setup>
const props = defineProps({
  foo: String
})

const emit = defineEmits(['change', 'delete'])
// setup code
</script>
```

---

## Defining a Two-Way Binding Prop with defineModel in Vue

This code snippet shows how to use `defineModel` to declare a two-way binding prop in Vue. The `defineModel` macro automatically declares a model prop and a corresponding value update event, enabling the use of `v-model` from the parent component. The code also shows how to declare the prop with options.

Source: https://github.com/vuejs/docs/blob/main/src/api/sfc-script-setup.md#_snippet_16

```javascript
// declares "modelValue" prop, consumed by parent via v-model
const model = defineModel()
// OR: declares "modelValue" prop with options
const model = defineModel({ type: String })

// emits "update:modelValue" when mutated
model.value = 'hello'

// declares "count" prop, consumed by parent via v-model:count
const count = defineModel('count')
// OR: declares "count" prop with options
const count = defineModel('count', { type: Number, default: 0 })

function inc() {
  // emits "update:count" when mutated
  count.value++
}
```

---

## Type-Only Props/Emit Declarations TypeScript

Illustrates how to declare props and emits using pure-type syntax by passing a literal type argument to `defineProps` or `defineEmits`.  This allows for type safety and automatic runtime declaration generation.

Source: https://github.com/vuejs/docs/blob/main/src/api/sfc-script-setup.md#_snippet_11

```typescript
const props = defineProps<{
  foo: string
  bar?: number
}>()

const emit = defineEmits<{
  (e: 'change', id: number): void
  (e: 'update', value: string): void
}>()

// 3.3+: alternative, more succinct syntax
const emit = defineEmits<{
  change: [id: number] // named tuple syntax
  update: [value: string]
}>()
```

---

## Exposing Properties in Script Setup with defineExpose in Vue

This code snippet demonstrates how to explicitly expose properties in a `<script setup>` component using the `defineExpose` compiler macro. This allows parent components to access these properties via template refs or `$parent` chains.

Source: https://github.com/vuejs/docs/blob/main/src/api/sfc-script-setup.md#_snippet_22

```vue
<script setup>
import { ref } from 'vue'

const a = 1
const b = ref(2)

defineExpose({
  a,
  b
})
</script>
```

---

## Using Typescript with defineModel in Vue

This snippet demonstrates how to use TypeScript with `defineModel` to specify the types of the model value and the modifiers. It shows how to define the type of the model value and how to specify the available modifiers.

Source: https://github.com/vuejs/docs/blob/main/src/api/sfc-script-setup.md#_snippet_21

```typescript
const modelValue = defineModel<string>()
//    ^? Ref<string | undefined>

// default model with options, required removes possible undefined values
const modelValue = defineModel<string>({ required: true })
//    ^? Ref<string>

const [modelValue, modifiers] = defineModel<string, 'trim' | 'uppercase'>()
//                 ^? Record<'trim' | 'uppercase', true | undefined>
```

---

## Using Imported Helpers Vue

Demonstrates how imported helper functions can be directly used in template expressions without needing to expose them via the `methods` option. The example uses a `capitalize` function imported from a local file.

Source: https://github.com/vuejs/docs/blob/main/src/api/sfc-script-setup.md#_snippet_2

```vue
<script setup>
import { capitalize } from './helpers'
</script>

<template>
  <div>{{ capitalize('hello') }}</div>
</template>
```

---

## Default Values for Type-Based Props TypeScript

Shows how to use JavaScript's native default value syntax to declare default values for props when using type-based props declaration with `defineProps`.

Source: https://github.com/vuejs/docs/blob/main/src/api/sfc-script-setup.md#_snippet_14

```typescript
interface Props {
  msg?: string
  labels?: string[]
}

const { msg = 'hello', labels = ['one', 'two'] } = defineProps<Props>()
```

---

## Reactivity with Refs Vue

Shows how to create reactive state using the `ref` function from Vue's reactivity APIs.  Refs are automatically unwrapped when referenced in templates. This example creates a reactive `count` variable.

Source: https://github.com/vuejs/docs/blob/main/src/api/sfc-script-setup.md#_snippet_3

```vue
<script setup>
import { ref } from 'vue'

const count = ref(0)
</script>

<template>
  <button @click="count++">{{ count }}</button>
</template>
```

---

## Defining Default Props with Typescript in Vue

This code snippet demonstrates how to define default values for props when using TypeScript with Vue. It uses the `withDefaults` compiler macro to provide type checks for the default values and ensures that the returned `props` type has the optional flags removed for properties that do have default values declared.

Source: https://github.com/vuejs/docs/blob/main/src/api/sfc-script-setup.md#_snippet_15

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

## Namespaced Components Vue

Illustrates the usage of component tags with dots (e.g., `<Foo.Bar>`) to refer to components nested under object properties, which is useful when importing multiple components from a single file.

Source: https://github.com/vuejs/docs/blob/main/src/api/sfc-script-setup.md#_snippet_7

```vue
<script setup>
import * as Form from './form-components'
</script>

<template>
  <Form.Input>
    <Form.Label>label</Form.Label>
  </Form.Input>
</template>
```

---

## Importing Custom Directives Vue

Demonstrates importing a custom directive and renaming it to fit the required naming scheme `vNameOfDirective` for use in `<script setup>`.

Source: https://github.com/vuejs/docs/blob/main/src/api/sfc-script-setup.md#_snippet_9

```vue
<script setup>
import { myDirective as vMyDirective } from './MyDirective.js'
</script>
```

---

## Exposing Top-Level Bindings Vue

Illustrates how top-level bindings (variables, function declarations, and imports) declared inside `<script setup>` are directly usable in the template. The example shows a variable `msg` and a function `log` being used in the template.

Source: https://github.com/vuejs/docs/blob/main/src/api/sfc-script-setup.md#_snippet_1

```vue
<script setup>
// variable
const msg = 'Hello!'

// functions
function log() {
  console.log(msg)
}
</script>

<template>
  <button @click="log">{{ msg }}</button>
</template>
```

---

## Dynamic Components Vue

Demonstrates the usage of dynamic components inside `<script setup>` using the `:is` binding. The components are referenced as variables, allowing for conditional rendering of different components.

Source: https://github.com/vuejs/docs/blob/main/src/api/sfc-script-setup.md#_snippet_5

```vue
<script setup>
import Foo from './Foo.vue'
import Bar from './Bar.vue'
</script>

<template>
  <component :is="Foo" />
  <component :is="someCondition ? Foo : Bar" />
</template>
```

---

## Reactive Props Destructure TypeScript

Demonstrates reactive props destructuring using `defineProps` in Vue 3.5+. Variables destructured from the return value of `defineProps` are reactive, and default values can be declared using JavaScript's native default value syntax. The compiler automatically prepends `props.` when code in the same `<script setup>` block accesses variables destructured from `defineProps`.

Source: https://github.com/vuejs/docs/blob/main/src/api/sfc-script-setup.md#_snippet_12

```typescript
const { foo } = defineProps(['foo'])

watchEffect(() => {
  // runs only once before 3.5
  // re-runs when the "foo" prop changes in 3.5+
  console.log(foo)
})

```

---

## Top-level Await in Vue Script Setup

This code shows the usage of top-level `await` inside `<script setup>`. The resulting code is compiled as `async setup()`, allowing you to directly await promises within the setup scope. Awaited expressions are compiled in a format that preserves the current component instance context after the `await`.

Source: https://github.com/vuejs/docs/blob/main/src/api/sfc-script-setup.md#_snippet_27

```vue
<script setup>
const post = await fetch(`/api/post/1`).then((r) => r.json())
</script>
```

---

## Accessing v-model Modifiers with defineModel in Vue

This code shows how to access modifiers used with the `v-model` directive by destructuring the return value of `defineModel()`. It demonstrates how to check if a modifier is present and conditionally transform the model value.

Source: https://github.com/vuejs/docs/blob/main/src/api/sfc-script-setup.md#_snippet_19

```javascript
const [modelValue, modelModifiers] = defineModel()

// corresponds to v-model.trim
if (modelModifiers.trim) {
  // ...
}
```

---

## Providing Type Hints for Slots with defineSlots in Vue

This snippet shows how to use the `defineSlots` macro to provide type hints for slot name and props type checking in Vue. This macro allows you to specify the expected props for each slot, improving IDE support and code maintainability.

Source: https://github.com/vuejs/docs/blob/main/src/api/sfc-script-setup.md#_snippet_24

```vue
<script setup lang="ts">
const slots = defineSlots<{
  default(props: { msg: string }): any
}>()
</script>
```

---

## Using InstanceType with Generics

This code snippet illustrates how to correctly reference a generic component in a `ref` using `vue-component-type-helpers`.  It imports components and uses `ComponentExposed` from `vue-component-type-helpers` to create a type for a ref targeting a generic component. InstanceType works for components without generics.

Source: https://github.com/vuejs/docs/blob/main/src/api/sfc-script-setup.md#_snippet_32

```vue
<script
  setup
  lang="ts"
>
import componentWithoutGenerics from '../component-without-generics.vue';
import genericComponent from '../generic-component.vue';

import type { ComponentExposed } from 'vue-component-type-helpers';

// Works for a component without generics
ref<InstanceType<typeof componentWithoutGenerics>>();

ref<ComponentExposed<typeof genericComponent>>();
</script>
```

---

## De-synchronization Issue with Default defineModel Prop Value - HTML

This HTML shows how to invoke child component that leads to de-synchronization issue between parent and child components.

Source: https://github.com/vuejs/docs/blob/main/src/api/sfc-script-setup.md#_snippet_18

```html
<Child v-model="myRef"></Child>
```

---

## Using useSlots and useAttrs in Vue Script Setup

This code snippet demonstrates how to use the `useSlots` and `useAttrs` helpers inside `<script setup>` to access slots and attributes, respectively. These helpers are useful in cases where you need to access slots and attributes directly within the setup function.

Source: https://github.com/vuejs/docs/blob/main/src/api/sfc-script-setup.md#_snippet_25

```vue
<script setup>
import { useSlots, useAttrs } from 'vue'

const slots = useSlots()
const attrs = useAttrs()
</script>
```

---

## Passing Explicit Types with @vue-generic Directive

This code snippet demonstrates how to pass explicit types to a Vue component using the `@vue-generic` directive. This is useful when the type cannot be inferred automatically. In the example, `ApiSelect` components are used with different data types (`Actor` and `Genre`) that are imported from the '@/api' module.

Source: https://github.com/vuejs/docs/blob/main/src/api/sfc-script-setup.md#_snippet_31

```vue
<template>
  <!-- @vue-generic {import('@/api').Actor} -->
  <ApiSelect v-model="peopleIds" endpoint="/api/actors" id-prop="actorId" />

  <!-- @vue-generic {import('@/api').Genre} -->
  <ApiSelect v-model="genreIds" endpoint="/api/genres" id-prop="genreId" />
</template>
```

---

## Basic Script Setup Syntax Vue

Demonstrates the basic syntax for using `<script setup>` in a Vue Single-File Component (SFC).  The `setup` attribute is added to the `<script>` block to enable the syntax, where code inside is compiled as the content of the component's `setup()` function.

Source: https://github.com/vuejs/docs/blob/main/src/api/sfc-script-setup.md#_snippet_0

```vue
<script setup>
console.log('hello script setup')
</script>
```

---

## Usage of normal <script> alongside <script setup> in Vue

This code demonstrates the use of a normal `<script>` tag alongside `<script setup>`. A normal `<script>` is required for declaring options that cannot be expressed in `<script setup>`, declaring named exports, and running side effects that should only execute once.

Source: https://github.com/vuejs/docs/blob/main/src/api/sfc-script-setup.md#_snippet_26

```vue
<script>
// normal <script>, executed in module scope (only once)
runSideEffectOnce()

// declare additional options
export default {
  inheritAttrs: false,
  customOptions: {}
}
</script>

<script setup>
// executed in setup() scope (for each instance)
</script>
```

---

## Import Statements in Vue Script Setup

This example shows how to use import statements inside `<script setup>`. You can use aliases defined in your build tool configuration.

Source: https://github.com/vuejs/docs/blob/main/src/api/sfc-script-setup.md#_snippet_28

```vue
<script setup>
import { ref } from 'vue'
import { componentA } from './Components'
import { componentB } from '@/Components'
import { componentC } from '~/Components'
</script>
```

---

## Compiled Reactive Props Destructure JavaScript

Shows the compiled equivalent of the reactive props destructure example, demonstrating how the compiler transforms accesses to destructured props to `props.foo`.

Source: https://github.com/vuejs/docs/blob/main/src/api/sfc-script-setup.md#_snippet_13

```javascript
const props = defineProps(['foo'])

watchEffect(() => {
  // `foo` transformed to `props.foo` by the compiler
  console.log(props.foo)
})

```

---

## Declaring Component Options with defineOptions in Vue

This code snippet shows how to declare component options directly inside `<script setup>` using the `defineOptions` macro. This eliminates the need for a separate `<script>` block for defining options like `inheritAttrs` or custom options.

Source: https://github.com/vuejs/docs/blob/main/src/api/sfc-script-setup.md#_snippet_23

```vue
<script setup>
defineOptions({
  inheritAttrs: false,
  customOptions: {
    /* ... */
  }
})
</script>
```

