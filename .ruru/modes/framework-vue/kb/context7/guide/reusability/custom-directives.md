# Vue.js Custom Directives Documentation

## Registering Custom Directive (Options API) JavaScript

Demonstrates local registration of a custom directive `highlight` using the `directives` option in a Vue component defined with the Options API.  The directive adds the `is-highlight` class to the element during the `mounted` hook.

Source: https://github.com/vuejs/docs/blob/main/src/guide/reusability/custom-directives.md#_snippet_2

```javascript
const highlight = {
  mounted: (el) => el.classList.add('is-highlight')
}

export default {
  directives: {
    // enables v-highlight in template
    highlight
  }
}
```

---

## Using Custom Directive in Template (Options API) HTML

Shows how to use the locally registered `v-highlight` directive within a Vue template. This is used with the Options API.

Source: https://github.com/vuejs/docs/blob/main/src/guide/reusability/custom-directives.md#_snippet_3

```vue-html
<p v-highlight>This sentence is important!</p>
```

---

## Using Custom Directive in Template (Composition API) Vue

Demonstrates the use of a custom directive `v-highlight` within a Vue template using the Composition API and `<script setup>`. The directive adds the `is-highlight` class to the paragraph element.

Source: https://github.com/vuejs/docs/blob/main/src/guide/reusability/custom-directives.md#_snippet_1

```vue
<script setup>
// enables v-highlight in templates
const vHighlight = {
  mounted: (el) => {
    el.classList.add('is-highlight')
  }
}
</script>

<template>
  <p v-highlight>This sentence is important!</p>
</template>
```

---

## Registering Custom Directive vFocus (Options API) JavaScript

Demonstrates the local registration of the `focus` directive using the `directives` option in a Vue component when using the Options API.  This directive calls the `focus()` method on the element when it is mounted.

Source: https://github.com/vuejs/docs/blob/main/src/guide/reusability/custom-directives.md#_snippet_7

```javascript
const focus = {
  mounted: (el) => el.focus()
}

export default {
  directives: {
    // enables v-focus in template
    focus
  }
}
```

---

## Custom Directive on Component Usage HTML

Demonstrates using a custom directive on a Vue component.  The directive will be applied to the component's root node.

Source: https://github.com/vuejs/docs/blob/main/src/guide/reusability/custom-directives.md#_snippet_16

```vue-html
<MyComponent v-demo="test" />
```

---

## Initializing Custom Directive vFocus (Composition API) Vue

Defines a custom directive `vFocus` within a `<script setup>` block. This directive focuses the element it's bound to when the element is mounted.

Source: https://github.com/vuejs/docs/blob/main/src/guide/reusability/custom-directives.md#_snippet_6

```vue
<script setup>
// enables v-focus in templates
const vFocus = {
  mounted: (el) => el.focus()
}
</script>

<template>
  <input v-focus />
</template>
```

---

## Initializing Custom Directive with Script Setup (Composition API) Vue

Defines a custom directive `vHighlight` within a `<script setup>` block. This directive adds the class `is-highlight` to the element it is bound to when the element is mounted.

Source: https://github.com/vuejs/docs/blob/main/src/guide/reusability/custom-directives.md#_snippet_0

```vue
const vHighlight = {
  mounted: el => {
    el.classList.add('is-highlight')
  }
}
```

---

## Dynamic Directive Argument HTML

Demonstrates the usage of a dynamic argument in a custom directive.  The argument passed to the directive will be dynamically updated based on the `arg` property in the component's state.

Source: https://github.com/vuejs/docs/blob/main/src/guide/reusability/custom-directives.md#_snippet_11

```vue-html
<div v-example:[arg]="value"></div>
```

---

## Function Shorthand Directive Definition JavaScript

Defines a custom directive using the function shorthand, which combines the `mounted` and `updated` hooks into a single function.  This example sets the color style of the element to the value passed to the directive.

Source: https://github.com/vuejs/docs/blob/main/src/guide/reusability/custom-directives.md#_snippet_13

```javascript
app.directive('color', (el, binding) => {
  // this will be called for both `mounted` and `updated`
  el.style.color = binding.value
})
```

---

## Object Literals Directive Usage HTML

Illustrates how to pass an object literal as the value to a custom directive.

Source: https://github.com/vuejs/docs/blob/main/src/guide/reusability/custom-directives.md#_snippet_14

```vue-html
<div v-demo="{ color: 'white', text: 'hello!' }"></div>
```

---

## Using Custom Directive vFocus in Template (Options API) HTML

Shows how to use the locally registered `v-focus` directive in a Vue template using the Options API.  The directive will automatically focus the input element.

Source: https://github.com/vuejs/docs/blob/main/src/guide/reusability/custom-directives.md#_snippet_8

```vue-html
<input v-focus />
```

