# Component v-model in Vue.js

## Two-way data binding with defineModel() in Vue Component

This Vue component demonstrates two-way data binding using the `defineModel()` macro. The `model` ref is synced with the parent's v-model value, and updates to it emit an `update:modelValue` event.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/v-model.md#_snippet_0

```vue
<!-- Child.vue -->
<script setup>
const model = defineModel()

function update() {
  model.value++
}
</script>

<template>
  <div>Parent bound v-model is: {{ model }}</div>
  <button @click="update">Increment</button>
</template>
```

---

## v-model on custom component

Demonstrates v-model on a custom component, showing how the v-model is equivalent to a `:model-value` prop and an `@update:model-value` event listener.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/v-model.md#_snippet_8

```vue-html
<CustomInput
  :model-value="searchText"
  @update:model-value="newValue => searchText = newValue"
/>
```

---

## v-model Modifier Handling (Composition API)

Shows how to access and handle custom modifiers on a `v-model` binding within a Vue.js component using the Composition API and `defineModel`. It demonstrates how to use the `set` option to implement a `capitalize` modifier.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/v-model.md#_snippet_21

```vue
<script setup>
const [model, modifiers] = defineModel({
  set(value) {
    if (modifiers.capitalize) {
      return value.charAt(0).toUpperCase() + value.slice(1)
    }
    return value
  }
})
</script>

<template>
  <input type="text" v-model="model" />
</template>
```

---

## Two-way data binding with native input element

This shows how to bind the `defineModel` ref to a native input element using v-model to wrap native input elements and provide the same `v-model` usage.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/v-model.md#_snippet_2

```vue
<script setup>
const model = defineModel()
</script>

<template>
  <input v-model="model" />
</template>
```

---

## defineModel with Arguments and Options

Shows how to pass both the model name and prop options to `defineModel` when using arguments with v-model.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/v-model.md#_snippet_13

```javascript
const title = defineModel('title', { required: true })
```

---

## Defining prop options for defineModel

Shows how to pass prop options to `defineModel` to specify if the `v-model` is required or provide a default value.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/v-model.md#_snippet_5

```javascript
// making the v-model required
const model = defineModel({ required: true })

// providing a default value
const model = defineModel({ default: 0 })
```

---

## v-model with Arguments Options API

Options API implementation of `v-model` with arguments: the child component should expect a `title` prop and emit an `update:title` event to update the parent value.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/v-model.md#_snippet_15

```vue
<!-- MyComponent.vue -->
<script>
export default {
  props: ['title'],
  emits: ['update:title']
}
</script>

<template>
  <input
    type="text"
    :value="title"
    @input="$emit('update:title', $event.target.value)"
  />
</template>
```

---

## Binding a v-model to a Vue Component

This shows how a parent component can bind a value to a child component using `v-model`.  Any changes made to the `countModel` in the child will automatically update the `countModel` in the parent.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/v-model.md#_snippet_1

```vue-html
<!-- Parent.vue -->
<Child v-model="countModel" />
```

---

## Custom Input Component

Implementation of a custom input component to work with `v-model`. It accepts a `modelValue` prop and emits an `update:modelValue` event when the input changes.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/v-model.md#_snippet_9

```vue
<!-- CustomInput.vue -->
<script>
export default {
  props: ['modelValue'],
  emits: ['update:modelValue']
}
</script>

<template>
  <input
    :value="modelValue"
    @input="$emit('update:modelValue', $event.target.value)"
  />
</template>
```

---

## Multiple v-model Bindings (Composition API)

Shows how to define multiple `v-model` bindings within a Vue.js component using Composition API and `defineModel`. It defines two refs, `firstName` and `lastName`, which are bound to input fields.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/v-model.md#_snippet_17

```vue
<script setup>
const firstName = defineModel('firstName')
const lastName = defineModel('lastName')
</script>

<template>
  <input type="text" v-model="firstName" />
  <input type="text" v-model="lastName" />
</template>
```

---

## defineModel with Arguments

Demonstrates using `defineModel()` with an argument to create a two-way binding to a specific prop in the child component.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/v-model.md#_snippet_12

```vue
<!-- MyComponent.vue -->
<script setup>
const title = defineModel('title')
</script>

<template>
  <input type="text" v-model="title" />
</template>
```

---

## Props and Emits Declaration for v-model with Modifiers (Options API)

This JavaScript code defines the `props` and `emits` options for a Vue component that uses `v-model` with a modifier. It shows how to access the modifiers within the component's `created` lifecycle hook. It relies on the Vue Options API.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/v-model.md#_snippet_26

```javascript
export default {
  props: ['title', 'titleModifiers'],
  emits: ['update:title'],
  created() {
    console.log(this.titleModifiers) // { capitalize: true }
  }
}
```

---

## Native Input using v-model

Illustrates the basic usage of `v-model` on a native input element, which gets compiled into a `:value` binding and an `@input` event listener.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/v-model.md#_snippet_6

```vue-html
<input v-model="searchText" />
```

---

## Custom Input with Computed Property

Another way of implementing `v-model` within a custom input component is to use a writable `computed` property with both a getter and a setter.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/v-model.md#_snippet_10

```vue
<!-- CustomInput.vue -->
<script>
export default {
  props: ['modelValue'],
  emits: ['update:modelValue'],
  computed: {
    value: {
      get() {
        return this.modelValue
      },
      set(value) {
        this.$emit('update:modelValue', value)
      }
    }
  }
}
</script>

<template>
  <input v-model="value" />
</template>
```

---

## v-model Modifier Handling (Options API)

Explains how to handle custom `v-model` modifiers using the Options API in Vue.js. It defines a `modelModifiers` prop and demonstrates how to check for modifiers and change the emitted value. Requires Vue.js framework.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/v-model.md#_snippet_23

```vue
<script>
export default {
  props: {
    modelValue: String,
    modelModifiers: {
      default: () => ({})
    }
  },
  emits: ['update:modelValue'],
  methods: {
    emitValue(e) {
      let value = e.target.value
      if (this.modelModifiers.capitalize) {
        value = value.charAt(0).toUpperCase() + value.slice(1)
      }
      this.$emit('update:modelValue', value)
    }
  }
}
</script>

<template>
  <input type="text" :value="modelValue" @input="emitValue" />
</template>
```

---

## v-model Modifier Handling (Composition API - Pre 3.4)

Demonstrates how to handle custom v-model modifiers in Vue.js using the Composition API for versions prior to 3.4.  It defines a `modelModifiers` prop, checks for the `capitalize` modifier, and modifies the emitted value accordingly. Requires Vue.js and Composition API.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/v-model.md#_snippet_22

```vue
<script setup>
const props = defineProps({
  modelValue: String,
  modelModifiers: { default: () => ({}) }
})

const emit = defineEmits(['update:modelValue'])

function emitValue(e) {
  let value = e.target.value
  if (props.modelModifiers.capitalize) {
    value = value.charAt(0).toUpperCase() + value.slice(1)
  }
  emit('update:modelValue', value)
}
</script>

<template>
  <input type="text" :value="props.modelValue" @input="emitValue" />
</template>
```

---

## Implementing v-model pre-Vue 3.4

This is how you would implement the same child component shown above prior to 3.4. Involves defining a prop `modelValue` and emitting an `update:modelValue` event when the input changes.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/v-model.md#_snippet_3

```vue
<!-- Child.vue -->
<script setup>
const props = defineProps(['modelValue'])
const emit = defineEmits(['update:modelValue'])
</script>

<template>
  <input
    :value="props.modelValue"
    @input="emit('update:modelValue', $event.target.value)"
  />
</template>
```

---

## Multiple v-model Bindings (Composition API - Pre 3.4)

Demonstrates how to implement multiple v-model bindings in Vue.js using the Composition API for versions prior to 3.4.  It defines props for firstName and lastName, emits update events, and binds the values to input fields. Requires Vue.js and the Composition API.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/v-model.md#_snippet_18

```vue
<script setup>
defineProps({
  firstName: String,
  lastName: String
})

defineEmits(['update:firstName', 'update:lastName'])
</script>

<template>
  <input
    type="text"
    :value="firstName"
    @input="$emit('update:firstName', $event.target.value)"
  />
  <input
    type="text"
    :value="lastName"
    @input="$emit('update:lastName', $event.target.value)"
  />
</template>
```

---

## Multiple v-model Bindings with Different Arguments and Modifiers in Vue

This code snippet illustrates the usage of multiple `v-model` directives, each with a different argument and modifier. `first-name` with `capitalize` and `last-name` with `uppercase` are used as examples.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/v-model.md#_snippet_27

```vue-html
<UserName
  v-model:first-name.capitalize="first"
  v-model:last-name.uppercase="last"
/>
```

---

## Accessing v-model Modifiers (Pre 3.4 Composition API)

This Vue code snippet shows the older approach (pre Vue 3.4) for accessing v-model modifiers in the Composition API. It uses `defineProps` to declare props, including modifiers, and `defineEmits` for emitting update events.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/v-model.md#_snippet_29

```vue
<script setup>
const props = defineProps({
firstName: String,
lastName: String,
firstNameModifiers: { default: () => ({}) },
lastNameModifiers: { default: () => ({}) }
})
defineEmits(['update:firstName', 'update:lastName'])

console.log(props.firstNameModifiers) // { capitalize: true }
console.log(props.lastNameModifiers) // { uppercase: true }
</script>
```

---

## Parent component binding v-model attributes

Demonstrates how the parent component's `v-model` syntax is compiled into prop binding and event listener for the pre-Vue 3.4 implementation.  The `foo` variable is passed as `modelValue` to the child, and updates are handled via the `@update:modelValue` event.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/v-model.md#_snippet_4

```vue-html
<!-- Parent.vue -->
<Child
  :modelValue="foo"
  @update:modelValue="$event => (foo = $event)"
/>
```

---

## v-model Binding with Argument and Modifier in Vue

This code snippet demonstrates how to use v-model with both an argument (`title`) and a modifier (`capitalize`). The generated prop name will be `arg + "Modifiers"` (e.g., `titleModifiers`).

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/v-model.md#_snippet_25

```vue-html
<MyComponent v-model:title.capitalize="myText">
```

---

## v-model with Arguments

Shows how to use `v-model` with arguments on a component.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/v-model.md#_snippet_11

```vue-html
<MyComponent v-model:title="bookTitle" />
```

---

## Native Input v-model Expanded

Demonstrates the expanded form of v-model on a native input, showing the explicit value binding and input event handling.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/v-model.md#_snippet_7

```vue-html
<input
  :value="searchText"
  @input="searchText = $event.target.value"
/>
```

