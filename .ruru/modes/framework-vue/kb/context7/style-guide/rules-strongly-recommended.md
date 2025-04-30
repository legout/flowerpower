# Vue.js Style Guide - Priority B Rules

## Good Prop Use in SFC (kebab-case or camelCase)

Shows proper usage of props in Single-File Components (SFC) using either kebab-case or camelCase but emphasizing consistency within the project.

Source: https://github.com/vuejs/docs/blob/main/src/style-guide/rules-strongly-recommended.md#_snippet_27

```vue-html
// for SFC - please make sure your casing is consistent throughout the project
// you can use either convention but we don't recommend mixing two different casing styles
<WelcomeMessage greeting-text="hi"/>
// or
<WelcomeMessage greetingText="hi"/>
```

---

## Good Component Name (PascalCase)

Shows correct practice of defining a component's name using PascalCase. Component names should use PascalCase in JS/JSX.

Source: https://github.com/vuejs/docs/blob/main/src/style-guide/rules-strongly-recommended.md#_snippet_19

```js
export default {
  name: 'MyComponent'
  // ...
}
```

---

## Good Computed Property (options API)

Demonstrates how to move a complex expression into a computed property within a Vue.js component's options API. The computed property handles the logic and returns a value that can be easily used in the template.

Source: https://github.com/vuejs/docs/blob/main/src/style-guide/rules-strongly-recommended.md#_snippet_35

```js
// The complex expression has been moved to a computed property
computed: {
  normalizedFullName() {
    return this.fullName.split(' ')
      .map(word => word[0].toUpperCase() + word.slice(1))
      .join(' ')
  }
}
```

---

## Good Component Tag Everywhere

Demonstrates the correct usage of kebab-case for a component tag, which can be applied consistently everywhere, though PascalCase is generally preferred for Single-File Components and string templates.

Source: https://github.com/vuejs/docs/blob/main/src/style-guide/rules-strongly-recommended.md#_snippet_11

```vue-html
<!-- Everywhere -->
<my-component></my-component>
```

---

## Bad Component Name (camelCase)

Shows bad practice of defining a component's name using camelCase. Component names should use PascalCase in JS/JSX.

Source: https://github.com/vuejs/docs/blob/main/src/style-guide/rules-strongly-recommended.md#_snippet_14

```js
export default {
  name: 'myComponent'
  // ...
}
```

---

## Good Simple Computed Properties (composition API)

Illustrates the recommended practice of breaking down a complex computed property into smaller, simpler computed properties using the Composition API for improved readability, testability, and adaptability.

Source: https://github.com/vuejs/docs/blob/main/src/style-guide/rules-strongly-recommended.md#_snippet_40

```js
const basePrice = computed(
  () => manufactureCost.value / (1 - profitMargin.value)
)

const discount = computed(
  () => basePrice.value * (discountPercent.value || 0)
)

const finalPrice = computed(() => basePrice.value - discount.value)
```

---

## Self-closing Vue Components in SFC and JSX

This vue-html snippet illustrates the correct way to use self-closing tags for Vue components that have no content within Single-File Components (SFCs), string templates, and JSX. It uses the self-closing tag syntax `/>` for components like `<MyComponent/>` in these contexts.

Source: https://github.com/vuejs/docs/blob/main/src/style-guide/rules-strongly-recommended.md#_snippet_2

```vue-html
<!-- In Single-File Components, string templates, and JSX -->
<MyComponent/>
```

---

## Bad Prop Use in in-DOM Template (camelCase)

Shows bad practice of using camelCase when using props in in-DOM templates. For in-DOM templates kebab-case should be used.

Source: https://github.com/vuejs/docs/blob/main/src/style-guide/rules-strongly-recommended.md#_snippet_24

```vue-html
// for in-DOM templates
<welcome-message greetingText="hi"></welcome-message>
```

---

## Bad Complex Computed Property (composition API)

Shows bad practice of creating complex computed properties instead of breaking them into simpler ones using composition API.

Source: https://github.com/vuejs/docs/blob/main/src/style-guide/rules-strongly-recommended.md#_snippet_38

```js
const price = computed(() => {
  const basePrice = manufactureCost.value / (1 - profitMargin.value)
  return basePrice - basePrice * (discountPercent.value || 0)
})
```

---

## Self-closing Vue Components in in-DOM templates

This vue-html snippet shows how to properly use self-closing tags for Vue components that have no content when using in-DOM templates.  In in-DOM templates, components should not be self-closing and require a closing tag

Source: https://github.com/vuejs/docs/blob/main/src/style-guide/rules-strongly-recommended.md#_snippet_3

```vue-html
<!-- In in-DOM templates -->
<my-component></my-component>
```

---

## Good Prop Declaration (camelCase Composition API)

Illustrates the correct usage of camelCase for prop declaration inside a Vue component's composition API. Prop names should always be camelCase when declared in JavaScript.

Source: https://github.com/vuejs/docs/blob/main/src/style-guide/rules-strongly-recommended.md#_snippet_26

```js
const props = defineProps({
  greetingText: String
})
```

---

## Vue v-on Directive: Longhand (Preferred)

Demonstrates the alternative preferred practice of using only the longhand notation (`v-on:`) for the `v-on` directive. Consistency is maintained, leading to improved readability.

Source: https://github.com/vuejs/docs/blob/main/src/style-guide/rules-strongly-recommended.md#_snippet_51

```vue-html
<input
  v-on:input="onInput"
  v-on:focus="onFocus"
>
```

---

## Vue v-slot Directive: Mixed Shorthand (Discouraged)

Demonstrates the discouraged practice of mixing shorthand and longhand notations for the `v-slot` directive. Consistency is crucial for readability and maintainability.

Source: https://github.com/vuejs/docs/blob/main/src/style-guide/rules-strongly-recommended.md#_snippet_47

```vue-html
<template v-slot:header>
  <h1>Here might be a page title</h1>
</template>

<template #footer>
  <p>Here's some contact info</p>
</template>
```

---

## HTML Attribute Value: No Quotes (Discouraged)

Demonstrates the discouraged practice of omitting quotes for HTML attribute values, which can lead to reduced readability and potential issues with spaces in attribute values. This example uses the `type` attribute of an input element without quotes.

Source: https://github.com/vuejs/docs/blob/main/src/style-guide/rules-strongly-recommended.md#_snippet_41

```vue-html
<input type=text>
```

---

## Bad Complex Expression in Template

Illustrates the bad practice of including complex expressions directly within a Vue.js template. Complex expressions should be refactored into computed properties or methods for better readability and maintainability.

Source: https://github.com/vuejs/docs/blob/main/src/style-guide/rules-strongly-recommended.md#_snippet_33

```vue-html
{{\n  fullName.split(' ').map((word) => {\n    return word[0].toUpperCase() + word.slice(1)\n  }).join(' ')\n}}
```

---

## Good Component Registration (PascalCase)

Illustrates correct usage of PascalCase for component registration using `app.component` in Vue.js. This aligns with JavaScript class naming conventions.

Source: https://github.com/vuejs/docs/blob/main/src/style-guide/rules-strongly-recommended.md#_snippet_16

```js
app.component('MyComponent', {
  // ...
})
```

---

## Bad Multi-Attribute Component (single line)

Illustrates the bad practice of defining a component with multiple attributes on a single line. Elements with multiple attributes should span multiple lines for better readability.

Source: https://github.com/vuejs/docs/blob/main/src/style-guide/rules-strongly-recommended.md#_snippet_30

```vue-html
<MyComponent foo="a" bar="b" baz="c"/>
```

---

## Good Simple Computed Properties (options API)

Illustrates the recommended practice of breaking down a complex computed property into smaller, simpler computed properties for improved readability, testability, and adaptability.

Source: https://github.com/vuejs/docs/blob/main/src/style-guide/rules-strongly-recommended.md#_snippet_39

```js
computed: {
  basePrice() {
    return this.manufactureCost / (1 - this.profitMargin)
  },

  discount() {
    return this.basePrice * (this.discountPercent || 0)
  },

  finalPrice() {
    return this.basePrice - this.discount
  }
}
```

