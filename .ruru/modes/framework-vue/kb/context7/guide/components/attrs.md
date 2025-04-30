# Vue.js Fallthrough Attributes Documentation

## Binding Fallthrough Attributes with v-bind Vue HTML

This example shows how to bind fallthrough attributes to a specific element within the component using `v-bind="$attrs"`. This is often used when attribute inheritance is disabled.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/attrs.md#_snippet_7

```vue-html
<div class="btn-wrapper">
  <button class="btn" v-bind="$attrs">Click Me</button>
</div>
```

---

## Accessing Fallthrough Attributes in Script Setup Vue

This code shows how to access fallthrough attributes using `useAttrs()` in `<script setup>`. The `attrs` object will contain all the fallthrough attributes.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/attrs.md#_snippet_10

```vue
<script setup>
import { useAttrs } from 'vue'

const attrs = useAttrs()
</script>
```

---

## Disabling Attribute Inheritance with defineOptions Vue

This snippet shows how to disable automatic attribute inheritance in a component using `defineOptions` within `<script setup>`. Setting `inheritAttrs` to `false` prevents automatic attribute application to the root element.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/attrs.md#_snippet_5

```vue
<script setup>
defineOptions({
  inheritAttrs: false
})
// ...setup logic
</script>
```

---

## Binding Fallthrough Attributes in Multi-Root Component Vue HTML

This example demonstrates how to explicitly bind `$attrs` to a specific element in a multi-root component to resolve the fallthrough attribute warning.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/attrs.md#_snippet_9

```vue-html
<header>...</header>
<main v-bind="$attrs">...</main>
<footer>...</footer>
```

---

## Accessing Fallthrough Attributes in Template Vue HTML

This shows how to access fallthrough attributes in a component's template using `$attrs`. This allows you to manually bind the attributes to specific elements.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/attrs.md#_snippet_6

```vue-html
<span>Fallthrough attributes: {{ $attrs }}</span>
```

---

## Using Component with Fallthrough Attribute Vue HTML

This demonstrates how a parent component uses the `<MyButton>` component and passes a `class` attribute. Since `<MyButton>` doesn't declare `class` as a prop, it is a fallthrough attribute.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/attrs.md#_snippet_1

```vue-html
<MyButton class="large" />
```

---

## Accessing Fallthrough Attributes in Options API Javascript

This code shows how to access fallthrough attributes in the Options API using `this.$attrs`. This property is available in the component instance.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/attrs.md#_snippet_12

```javascript
export default {
  created() {
    console.log(this.$attrs)
  }
}
```

