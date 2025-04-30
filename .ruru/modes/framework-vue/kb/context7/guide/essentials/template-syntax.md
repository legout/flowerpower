# Vue.js Template Syntax Documentation

## Text Interpolation in Vue Template

This code snippet demonstrates text interpolation in a Vue template using the mustache syntax (double curly braces). The `msg` property from the component instance is dynamically rendered within the `<span>` element. The content will update whenever the `msg` property changes in the Vue component.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/template-syntax.md#_snippet_0

```vue-html
<span>Message: {{ msg }}</span>
```

---

## JavaScript Object for Dynamic Attribute Binding (Options API)

This JavaScript snippet shows how to define a data property `objectOfAttrs` in a Vue Options API component, which contains attributes intended for dynamic binding using the `v-bind` directive.  It provides values for `id` and `class` which can be dynamically bound to an HTML element.  This example is intended to be used with the `v-bind` directive without an argument.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/template-syntax.md#_snippet_8

```javascript
data() {
  return {
    objectOfAttrs: {
      id: 'container',
      class: 'wrapper'
    }
  }
}
```

---

## Same-name Shorthand for v-bind in Vue 3.4+

This snippet showcases the same-name shorthand for the `v-bind` directive, available in Vue 3.4 and later. When the attribute name matches the JavaScript value being bound, the attribute value can be omitted. This simplifies the syntax, making it more concise. This feature is similar to property shorthand when declaring objects in JavaScript.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/template-syntax.md#_snippet_4

```vue-html
<!-- same as :id="id" -->
<div :id></div>

<!-- this also works -->
<div v-bind:id></div>
```

---

## Attribute Binding using v-bind Directive in Vue

This code snippet demonstrates attribute binding using the `v-bind` directive in a Vue template.  The `id` attribute of the `<div>` element is dynamically bound to the `dynamicId` property of the component. When `dynamicId` changes, the `id` attribute will update accordingly.  If the bound value is `null` or `undefined`, the attribute will be removed from the rendered element.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/template-syntax.md#_snippet_2

```vue-html
<div v-bind:id="dynamicId"></div>
```

---

## Vue.js Dynamic v-bind Argument

Demonstrates how to use a JavaScript expression to dynamically determine the attribute bound by v-bind. The attribute name is determined by the value of `attributeName`. A shorthand notation is also shown. Requires a Vue component instance with a data property `attributeName`.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/template-syntax.md#_snippet_13

```vue-html
<a v-bind:[attributeName]="url"> ... </a>

<!-- shorthand -->
<a :[attributeName]="url"> ... </a>
```

---

## Vue.js v-on Modifier Example

Demonstrates the use of the `.prevent` modifier on the `v-on` directive. This modifier calls `event.preventDefault()` on the triggered event, preventing the default form submission behavior.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/template-syntax.md#_snippet_17

```vue-html
<form @submit.prevent="onSubmit">...</form>
```

---

## JavaScript Expressions in Vue Templates

This snippet demonstrates the usage of JavaScript expressions within Vue templates. It showcases basic arithmetic operations, ternary operators, string manipulation, and template literals. Expressions are evaluated in the context of the component instance, allowing dynamic rendering of data.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/template-syntax.md#_snippet_9

```vue-html
{{ number + 1 }}

{{ ok ? 'YES' : 'NO' }}

{{ message.split('').reverse().join('') }}

<div :id="`list-${id}`"></div>
```

---

## Boolean Attribute Binding with v-bind in Vue

This code snippet demonstrates how to bind boolean attributes using `v-bind` in Vue. The `disabled` attribute of the `<button>` element is bound to the `isButtonDisabled` property. The attribute will be included if `isButtonDisabled` is truthy; otherwise, it will be omitted. This offers dynamic control over boolean attributes based on component data.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/template-syntax.md#_snippet_5

```vue-html
<button :disabled="isButtonDisabled">Button</button>
```

---

## Directive Usage with v-if in Vue

This code demonstrates the usage of the `v-if` directive in Vue.  The `<p>` element will be rendered or removed from the DOM based on the truthiness of the `seen` property.  This provides a way to conditionally render elements based on component data.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/template-syntax.md#_snippet_10

```vue-html
<p v-if="seen">Now you see me</p>
```

---

## JavaScript Object for Dynamic Attribute Binding (Composition API)

This JavaScript snippet defines an object, `objectOfAttrs`, intended for dynamic attribute binding in Vue's Composition API.  It contains attributes like `id`, `class`, and `style` that can be dynamically applied to an HTML element using `v-bind`. This is used in conjunction with the `v-bind` directive without an argument.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/template-syntax.md#_snippet_7

```javascript
const objectOfAttrs = {
  id: 'container',
  class: 'wrapper',
  style: 'background-color:green'
}
```

---

## Vue.js Dynamic v-on Event Handler

Illustrates how to bind a handler to a dynamic event name using v-on. The event name is determined by the value of `eventName`. A shorthand is also demonstrated. Requires a Vue component instance with a data property `eventName` and a method `doSomething`.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/template-syntax.md#_snippet_14

```vue-html
<a v-on:[eventName]="doSomething"> ... </a>

<!-- shorthand -->
<a @[eventName]="doSomething"> ... </a>
```

