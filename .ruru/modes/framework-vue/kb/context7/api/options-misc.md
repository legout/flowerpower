# Vue.js Component Options: Misc

## Disable attribute inheritance (Composition API)

This code demonstrates disabling attribute inheritance for a Vue component using the Composition API within `<script setup>`. It uses `defineProps`, `defineEmits`, and `defineOptions` to achieve the same effect as the Options API example.

Source: https://github.com/vuejs/docs/blob/main/src/api/options-misc.md#_snippet_3

```vue
<script setup>
defineProps(['label', 'value'])
defineEmits(['input'])
defineOptions({
  inheritAttrs: false
})
</script>

<template>
  <label>
    {{ label }}
    <input
      v-bind="$attrs"
      v-bind:value="value"
      v-on:input="$emit('input', $event.target.value)"
    />
  </label>
</template>
```

---

## Registering a Custom Directive

This JavaScript code demonstrates how to register a custom directive named `focus` within a Vue.js component. The directive automatically focuses the element it's bound to when the component is mounted.

Source: https://github.com/vuejs/docs/blob/main/src/api/options-misc.md#_snippet_7

```javascript
export default {
  directives: {
    // enables v-focus in template
    focus: {
      mounted(el) {
        el.focus()
      }
    }
  }
}
```

---

## Using a Custom Directive in Template

This HTML code demonstrates how to use the custom directive `v-focus` in a Vue.js template. It binds the directive to an input element, causing it to automatically focus when the component is mounted.

Source: https://github.com/vuejs/docs/blob/main/src/api/options-misc.md#_snippet_8

```vue-html
<input v-focus>
```

---

## Components Option Type Definition

Defines the type for the `components` option in Vue.js component options. This option allows registering components to be made available to the component instance.

Source: https://github.com/vuejs/docs/blob/main/src/api/options-misc.md#_snippet_4

```typescript
interface ComponentOptions {
  components?: { [key: string]: Component }
}
```

---

## Registering Components

This JavaScript code shows how to register components within a Vue.js component's `components` option. It demonstrates both shorthand registration and registering under a different name.

Source: https://github.com/vuejs/docs/blob/main/src/api/options-misc.md#_snippet_5

```javascript
import Foo from './Foo.vue'
import Bar from './Bar.vue'

export default {
  components: {
    // shorthand
    Foo,
    // register under a different name
    RenamedBar: Bar
  }
}
```

