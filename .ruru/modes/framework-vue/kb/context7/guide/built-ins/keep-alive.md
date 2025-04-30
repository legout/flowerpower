# Vue.js KeepAlive Component Documentation

## KeepAlive Basic Usage

Illustrates how to wrap a dynamic component with `<KeepAlive>` to cache the component instance and persist its state when switching away from it. This prevents the component from being unmounted and recreated.

Source: https://github.com/vuejs/docs/blob/main/src/guide/built-ins/keep-alive.md#_snippet_1

```vue-html
<!-- Inactive components will be cached! -->
<KeepAlive>
  <component :is="activeComponent" />
</KeepAlive>
```

---

## Dynamic Component Usage

Demonstrates the basic usage of a dynamic component in Vue.js using the `<component>` special element and the `:is` attribute to bind to an active component.

Source: https://github.com/vuejs/docs/blob/main/src/guide/built-ins/keep-alive.md#_snippet_0

```vue-html
<component :is="activeComponent" />
```

---

## KeepAlive Include String

Demonstrates how to use the `include` prop with a comma-delimited string to specify which components should be cached by `<KeepAlive>`.  Only components with names matching 'a' or 'b' will be cached.

Source: https://github.com/vuejs/docs/blob/main/src/guide/built-ins/keep-alive.md#_snippet_2

```vue-html
<!-- comma-delimited string -->
<KeepAlive include="a,b">
  <component :is="view" />
</KeepAlive>
```

---

## activated / deactivated (Options API)

Illustrates the usage of the `activated` and `deactivated` lifecycle hooks in a component using the Options API. These hooks are called when a component is activated (re-inserted from the cache) and deactivated (removed from the DOM into the cache), respectively. They are also called on mount and unmount.

Source: https://github.com/vuejs/docs/blob/main/src/guide/built-ins/keep-alive.md#_snippet_7

```js
export default {
  activated() {
    // called on initial mount
    // and every time it is re-inserted from the cache
  },
  deactivated() {
    // called when removed from the DOM into the cache
    // and also when unmounted
  }
}
```

---

## onActivated / onDeactivated (Composition API)

Demonstrates the usage of `onActivated` and `onDeactivated` lifecycle hooks in a component using the Composition API. These hooks are called when a component is activated (re-inserted from the cache) and deactivated (removed from the DOM into the cache), respectively. They are also called on mount and unmount.

Source: https://github.com/vuejs/docs/blob/main/src/guide/built-ins/keep-alive.md#_snippet_6

```vue
<script setup>
import { onActivated, onDeactivated } from 'vue'

onActivated(() => {
  // called on initial mount
  // and every time it is re-inserted from the cache
})

onDeactivated(() => {
  // called when removed from the DOM into the cache
  // and also when unmounted
})
</script>
```

---

## KeepAlive Max Instances

Explains how to limit the maximum number of component instances cached by `<KeepAlive>` using the `max` prop.  In this example, a maximum of 10 component instances will be cached using an LRU (Least Recently Used) cache replacement policy.

Source: https://github.com/vuejs/docs/blob/main/src/guide/built-ins/keep-alive.md#_snippet_5

```vue-html
<KeepAlive :max="10">
  <component :is="activeComponent" />
</KeepAlive>
```

---

## KeepAlive Include Regex

Shows how to use the `include` prop with a regular expression to define which components should be cached by `<KeepAlive>`. The regular expression is bound using `v-bind`.

Source: https://github.com/vuejs/docs/blob/main/src/guide/built-ins/keep-alive.md#_snippet_3

```vue-html
<!-- regex (use `v-bind`) -->
<KeepAlive :include="/a|b/">
  <component :is="view" />
</KeepAlive>
```

---

## KeepAlive Include Array

Illustrates how to use the `include` prop with an array to specify which components should be cached by `<KeepAlive>`. The array is bound using `v-bind`.

Source: https://github.com/vuejs/docs/blob/main/src/guide/built-ins/keep-alive.md#_snippet_4

```vue-html
<!-- Array (use `v-bind`) -->
<KeepAlive :include="['a', 'b']">
  <component :is="view" />
</KeepAlive>
```

