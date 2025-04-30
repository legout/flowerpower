# Vue SFC Syntax Specification

## Vue SFC Example

This snippet illustrates the basic structure of a Vue Single-File Component (SFC) with template, script, and style blocks. It shows how to define a simple component with data and styling using HTML-like syntax.

Source: https://github.com/vuejs/docs/blob/main/src/api/sfc-spec.md#_snippet_0

```vue
<template>
  <div class="example">{{ msg }}</div>
</template>

<script>
export default {
  data() {
    return {
      msg: 'Hello world!'
    }
  }
}
</script>

<style>
.example {
  color: red;
}
</style>

<custom1>
  This could be e.g. documentation for the component.
</custom1>
```

---

## TypeScript in Vue SFC

This snippet demonstrates the use of TypeScript within a Vue Single-File Component's `<script>` block. The `lang="ts"` attribute specifies that the content should be treated as TypeScript code.

Source: https://github.com/vuejs/docs/blob/main/src/api/sfc-spec.md#_snippet_1

```vue-html
<script lang="ts">
  // use TypeScript
</script>
```

---

## Importing External Files in Vue SFC

This snippet demonstrates how to import content from external files into Vue Single-File Components using the `src` attribute in the template, script, and style blocks. Relative paths need to start with `./`.

Source: https://github.com/vuejs/docs/blob/main/src/api/sfc-spec.md#_snippet_3

```vue
<template src="./template.html"></template>
<style src="./style.css"></style>
<script src="./script.js"></script>
```

---

## Importing NPM Dependencies in Vue SFC

This snippet demonstrates importing resources from npm dependencies inside a Vue Single-File Component's style block, using the `src` attribute. Note: webpack module resolution rules apply here.

Source: https://github.com/vuejs/docs/blob/main/src/api/sfc-spec.md#_snippet_4

```vue
<!-- import a file from the installed "todomvc-app-css" npm package -->
<style src="todomvc-app-css/index.css" />
```

