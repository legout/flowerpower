# Vue.js Component Events

## Declaring Emitted Events using defineEmits Vue

This snippet shows how to declare emitted events using `defineEmits()` macro in the Composition API. The component declares that it will emit `inFocus` and `submit` events.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/events.md#_snippet_10

```Vue
<script setup>
defineEmits(['inFocus', 'submit'])
</script>
```

---

## Emitting events with defineEmits in Composition API Vue

This snippet shows how to declare and use `defineEmits` within `<script setup>` to create an emit function, which can then be used to emit events.  This is an alternate method that is used for emitting events within the setup script.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/events.md#_snippet_11

```Vue
<script setup>
const emit = defineEmits(['inFocus', 'submit'])

function buttonClick() {
  emit('submit')
}
</script>
```

---

## Declaring Emitted Events with Type Annotations (Composition API) TypeScript

This snippet demonstrates using type annotations with `defineEmits` in `<script setup>` to declare emitted events with TypeScript. It specifies the event names and their argument types.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/events.md#_snippet_16

```TypeScript
<script setup lang="ts">
const emit = defineEmits<{
  (e: 'change', id: number): void
  (e: 'update', value: string): void
}>()
</script>
```

---

## Handling Event Arguments in Composition API Vue JavaScript

This snippet demonstrates handling event arguments within the Composition API. The function `increaseCount` receives the event argument `n` and adds it to the reactive `count.value`.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/events.md#_snippet_9

```JavaScript
function increaseCount(n) {
  count.value += n
}
```

---

## Listening to Events with .once Modifier Vue HTML

This snippet demonstrates how to use the `.once` modifier with `v-on` to ensure that a listener is only triggered once. The `callback` function is executed only the first time `MyComponent` emits `some-event`.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/events.md#_snippet_4

```Vue-HTML
<MyComponent @some-event.once="callback" />
```

---

## Listening to Events in Parent Component Vue HTML

This snippet shows how a parent component can listen to a custom event emitted by a child component using `v-on` (shorthand `@`). When `MyComponent` emits `some-event`, the `callback` function is executed.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/events.md#_snippet_3

```Vue-HTML
<MyComponent @some-event="callback" />
```

---

## Validating Emitted Events (Options API) JavaScript

This snippet shows how to validate emitted events in the Options API. The `submit` event expects a payload with `email` and `password` properties and validates the payload at runtime, logging a warning if the validation fails.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/events.md#_snippet_19

```JavaScript
export default {
  emits: {
    // No validation
    click: null,

    // Validate submit event
    submit: ({ email, password }) => {
      if (email && password) {
        return true
      } else {
        console.warn('Invalid submit event payload!')
        return false
      }
    }
  },
  methods: {
    submitForm(email, password) {
      this.$emit('submit', { email, password })
    }
  }
}
```

---

## Declaring Emitted Events with Payload Type (Options API) JavaScript

This snippet shows how to declare emitted events with payload type validation in the Options API. The `submit` event expects a payload with `email` and `password` properties and validates the payload at runtime.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/events.md#_snippet_17

```JavaScript
export default {
  emits: {
    submit(payload: { email: string, password: string }) {
      // return `true` or `false` to indicate
      // validation pass / fail
    }
  }
}
```

---

## Emitting Events in Options API Vue JavaScript

This snippet demonstrates how to emit a custom event from a Vue.js component's method using the `this.$emit()` method within the Options API. The `submit` method, when called, emits the 'someEvent' event.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/events.md#_snippet_2

```JavaScript
export default {
  methods: {
    submit() {
      this.$emit('someEvent')
    }
  }
}
```

---

## Validating Emitted Events (Composition API) Vue

This snippet shows how to validate emitted events in the Composition API. The `submit` event expects a payload with `email` and `password` properties and validates the payload at runtime, logging a warning if the validation fails.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/events.md#_snippet_18

```Vue
<script setup>
const emit = defineEmits({
  // No validation
  click: null,

  // Validate submit event
  submit: ({ email, password }) => {
    if (email && password) {
      return true
    } else {
      console.warn('Invalid submit event payload!')
      return false
    }
  }
})

function submitForm(email, password) {
  emit('submit', { email, password })
}
</script>
```

---

## Listening to Event Arguments with Inline Arrow Function Vue HTML

This snippet demonstrates listening for an event and accessing its argument using an inline arrow function. When the `increase-by` event is emitted by `MyButton`, the provided value `n` is added to the `count` variable.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/events.md#_snippet_6

```Vue-HTML
<MyButton @increase-by="(n) => count += n" />
```

---

## Listening to Event Arguments with Method Vue HTML

This snippet shows how to listen for an event and pass its argument to a method. When the `increase-by` event is emitted, the `increaseCount` method is called with the event's argument.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/events.md#_snippet_7

```Vue-HTML
<MyButton @increase-by="increaseCount" />
```

---

## Handling Event Arguments in Options API Vue JavaScript

This snippet demonstrates how to handle an event argument passed to a method in the Options API. The `increaseCount` method receives the event argument `n` and adds it to `this.count`.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/events.md#_snippet_8

```JavaScript
methods: {
  increaseCount(n) {
    this.count += n
  }
}
```

---

## Emitting events using setup context in Options API JavaScript

This snippet shows how to emit events using the `emit` function available on the `setup()` context in the Options API. This is an alternate method that is used for emitting events when using an explicit `setup` function.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/events.md#_snippet_13

```JavaScript
export default {
  emits: ['inFocus', 'submit'],
  setup(props, ctx) {
    ctx.emit('submit')
  }
}
```

---

## Declaring Emitted Events with Payload Type (Composition API) TypeScript

This snippet demonstrates how to declare emitted events with payload type validation in the Composition API using TypeScript. The `submit` event expects a payload with `email` and `password` properties and validates the payload at runtime.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/events.md#_snippet_15

```TypeScript
<script setup lang="ts">
const emit = defineEmits({
  submit(payload: { email: string, password: string }) {
    // return `true` or `false` to indicate
    // validation pass / fail
  }
})
</script>
```

---

## Destructuring emit from setup context in Options API JavaScript

This snippet demonstrates how to destructure the `emit` function from the `setup()` context, providing a more concise way to emit events within the Options API.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/events.md#_snippet_14

```JavaScript
export default {
  emits: ['inFocus', 'submit'],
  setup(props, { emit }) {
    emit('submit')
  }
}
```

---

## Declaring Emitted Events using emits Option JavaScript

This snippet shows how to declare emitted events using the `emits` option in the Options API. The component declares that it will emit `inFocus` and `submit` events.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/events.md#_snippet_12

```JavaScript
export default {
  emits: ['inFocus', 'submit']
}
```

---

## Import onMounted and Handle Hash Redirects Vue

This script imports the `onMounted` function from Vue and checks if the code is running in a browser environment. If so, it checks the URL hash and redirects to a different page if the hash matches certain outdated values related to v-model usage. This ensures that users with old links are directed to the correct content.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/events.md#_snippet_0

```Vue
<script setup>
import { onMounted } from 'vue'

if (typeof window !== 'undefined') {
  const hash = window.location.hash

  // The docs for v-model used to be part of this page. Attempt to redirect outdated links.
  if ([
    '#usage-with-v-model',
    '#v-model-arguments',
    '#multiple-v-model-bindings',
    '#handling-v-model-modifiers'
  ].includes(hash)) {
    onMounted(() => {
      window.location = './v-model.html' + hash
    })
  }
}
</script>
```

