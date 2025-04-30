# Vue.js Props: Passing Data from Parent to Child Components

## Passing Props to Child Component in HTML Template in Vue.js

Passes a dynamic prop named 'msg' to a child component named 'child-comp' using the `v-bind` shorthand syntax (':'). The value of the 'msg' prop is bound to the 'greeting' variable in the parent component's scope. This is the syntax to use within a non-SFC HTML template.

Source: https://github.com/vuejs/docs/blob/main/src/tutorial/src/step-12/description.md#_snippet_4

```vue-html
<child-comp :msg="greeting"></child-comp>
```

---

## Declaring Props in Options API in Vue.js

Declares a prop named 'msg' of type String in a Vue.js component using the Options API. The `props` option is an object where each key represents a prop name and the value specifies its type. The prop can then be accessed via `this.msg` within the component instance.

Source: https://github.com/vuejs/docs/blob/main/src/tutorial/src/step-12/description.md#_snippet_1

```javascript
// in child component
export default {
  props: {
    msg: String
  },
  setup(props) {
    // access props.msg
  }
}
```

---

## Declaring Props in SFC using Composition API in Vue.js

Declares a prop named 'msg' of type String in a Vue.js Single File Component using the Composition API. `defineProps()` is a compile-time macro that defines the props accepted by the component. The prop can then be accessed in the template or via the object returned by `defineProps()` within the script.

Source: https://github.com/vuejs/docs/blob/main/src/tutorial/src/step-12/description.md#_snippet_0

```vue
<!-- ChildComp.vue -->
<script setup>
const props = defineProps({
  msg: String
})
</script>
```

