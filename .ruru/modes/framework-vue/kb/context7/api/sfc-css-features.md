# Vue.js SFC CSS Features

## CSS Modules with Composition API - JavaScript

Illustrates how to access CSS Modules classes within the `setup()` function using the `useCssModule` API. This allows for dynamic class binding based on component state. Accepts the module name as argument.

Source: https://github.com/vuejs/docs/blob/main/src/api/sfc-css-features.md#_snippet_9

```javascript
import { useCssModule } from 'vue'

// inside setup() scope...
// default, returns classes for <style module>
useCssModule()

// named, returns classes for <style module="classes">
useCssModule('classes')
```

---

## Scoped CSS Example - Vue

Demonstrates how to use the `scoped` attribute in a `<style>` tag to apply CSS only to the current component. The styles are transformed using PostCSS to add a unique attribute to the elements and selectors.

Source: https://github.com/vuejs/docs/blob/main/src/api/sfc-css-features.md#_snippet_0

```vue
<style scoped>
.example {
  color: red;
}
</style>

<template>
  <div class="example">hi</div>
</template>
```

---

## v-bind() in CSS with Script Setup - Vue

Illustrates the usage of `v-bind()` within a `<script setup>` block. JavaScript expressions are supported within the `v-bind()` function (must be wrapped in quotes). The color property is reactively updated.

Source: https://github.com/vuejs/docs/blob/main/src/api/sfc-css-features.md#_snippet_12

```vue
<script setup>
import { ref } from 'vue'
const theme = ref({
    color: 'red',
})
</script>

<template>
  <p>hello</p>
</template>

<style scoped>
p {
  color: v-bind('theme.color');
}
</style>
```

---

## v-bind() in CSS - Vue

Demonstrates how to use the `v-bind()` CSS function to link CSS values to dynamic component state. The CSS value is reactively updated whenever the bound data property changes.

Source: https://github.com/vuejs/docs/blob/main/src/api/sfc-css-features.md#_snippet_11

```vue
<template>
  <div class="text">hello</div>
</template>

<script>
export default {
  data() {
    return {
      color: 'red'
    }
  }
}
</script>

<style>
.text {
  color: v-bind(color);
}
</style>
```

---

## CSS Modules Example - Vue

Shows how to use CSS Modules with the `<style module>` tag.  The resulting CSS classes are exposed as an object under the `$style` key, providing a way to scope CSS and avoid naming collisions. Requires CSS Modules support via a preprocessor or bundler plugin.

Source: https://github.com/vuejs/docs/blob/main/src/api/sfc-css-features.md#_snippet_7

```vue
<template>
  <p :class="$style.red">This should be red</p>
</template>

<style module>
.red {
  color: red;
}
</style>
```

---

## Mixing Local and Global Styles - Vue

Demonstrates how to include both scoped and non-scoped styles within the same component by using separate `<style>` tags. This allows for a combination of component-specific and global styles.

Source: https://github.com/vuejs/docs/blob/main/src/api/sfc-css-features.md#_snippet_6

```vue
<style>
/* global styles */
</style>

<style scoped>
/* local styles */
</style>
```

---

## Deep Selectors Compiled - CSS

Shows the compiled output of the deep selector example, demonstrating how the `:deep()` pseudo-class is transformed to target elements without the scoping attribute.

Source: https://github.com/vuejs/docs/blob/main/src/api/sfc-css-features.md#_snippet_3

```css
.a[data-v-f3f3eg9] .b {
  /* ... */
}
```

---

## Global Selectors in Scoped CSS - Vue

Illustrates how to use the `:global` pseudo-class to apply a CSS rule globally, bypassing the scoping mechanism. This is useful for applying styles to elements outside the component's scope.

Source: https://github.com/vuejs/docs/blob/main/src/api/sfc-css-features.md#_snippet_5

```vue
<style scoped>
:global(.red) {
  color: red;
}
</style>
```

---

## Scoped CSS Compiled - Vue

Shows the compiled output of the scoped CSS example, demonstrating how PostCSS adds a unique `data-v` attribute to both the CSS selectors and the HTML elements, ensuring style encapsulation.

Source: https://github.com/vuejs/docs/blob/main/src/api/sfc-css-features.md#_snippet_1

```vue
<style>
.example[data-v-f3f3eg9] {
  color: red;
}
</style>

<template>
  <div class="example" data-v-f3f3eg9>hi</div>
</template>
```

