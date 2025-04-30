# Vue.js Component Event Emission

## Emitting Events with Composition API (JS) in Vue.js

This snippet illustrates how to declare and emit a custom event named 'response' from a Vue.js component using the Composition API with a standard JavaScript setup function. It utilizes the `emits` option to declare the event and the `emit` function (provided via the setup context) to trigger the event with a string argument.

Source: https://github.com/vuejs/docs/blob/main/src/tutorial/src/step-13/description.md#_snippet_1

```javascript
export default {
  // declare emitted events
  emits: ['response'],
  setup(props, { emit }) {
    // emit with argument
    emit('response', 'hello from child')
  }
}
```

---

## Emitting Events with Composition API (Script Setup) in Vue.js

This code snippet shows how to declare and emit a custom event named 'response' from a Vue.js component using the Composition API with `<script setup>`. The `defineEmits` function is used to declare the event, and the `emit` function is used to trigger the event, passing a string argument.

Source: https://github.com/vuejs/docs/blob/main/src/tutorial/src/step-13/description.md#_snippet_0

```vue
<script setup>
// declare emitted events
const emit = defineEmits(['response'])

// emit with argument
emit('response', 'hello from child')
</script>
```

---

## Listening for Emitted Events in Parent Component (HTML)

This code shows how a parent component listens for the 'response' event emitted by a child component using the `v-on` directive (shorthand `@`) in a standard HTML template.  The handler function receives the argument passed from the child and assigns it to a local state variable `childMsg`.

Source: https://github.com/vuejs/docs/blob/main/src/tutorial/src/step-13/description.md#_snippet_4

```vue-html
<child-comp @response="(msg) => childMsg = msg"></child-comp>
```

