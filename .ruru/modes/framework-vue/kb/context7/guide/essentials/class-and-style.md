# Vue.js Class and Style Bindings Documentation

## Computed classObject (Options API)

Defines a computed property within Vue's Options API that returns a class object. The class object is dynamically constructed based on the component's data properties, allowing for complex class binding logic.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/class-and-style.md#_snippet_8

```javascript
data() {
  return {
    isActive: true,
    error: null
  }
},
computed: {
  classObject() {
    return {
      active: this.isActive && !this.error,
      'text-danger': this.error && this.error.type === 'fatal'
    }
  }
}
```

---

## Style Properties data properties (Options API)

Defines data properties within Vue's Options API to store style properties such as 'activeColor' and 'fontSize'. These properties can then be bound to the `style` attribute for dynamic styling.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/class-and-style.md#_snippet_21

```javascript
data() {
  return {
    activeColor: 'red',
    fontSize: 30
  }
}
```

---

## Computed classObject (Composition API)

Creates a computed property using Vue's Composition API that returns a class object based on reactive values.  This enables more complex logic for determining class application.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/class-and-style.md#_snippet_7

```javascript
const isActive = ref(true)
const error = ref(null)

const classObject = computed(() => ({
  active: isActive.value && !error.value,
  'text-danger': error.value && error.value.type === 'fatal'
}))
```

---

## Reactive classObject (Composition API)

Defines a reactive object using Vue's Composition API to represent a class object.  The 'active' and 'text-danger' properties control the presence of corresponding CSS classes.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/class-and-style.md#_snippet_4

```javascript
const classObject = reactive({
  active: true,
  'text-danger': false
})
```

---

## Binding to Reactive Style Object (Vue)

Binds the `style` attribute to a reactive style object, dynamically applying styles based on the object's properties. This provides a cleaner way to manage style bindings in the template.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/class-and-style.md#_snippet_26

```vue-html
<div :style="styleObject"></div>
```

---

## Binding HTML Class with static class (Vue)

Demonstrates how to bind classes using the object syntax in Vue, combining a static class with dynamically toggled classes based on the `isActive` and `hasError` data properties.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/class-and-style.md#_snippet_3

```vue-html
<div
  class="static"
  :class="{ active: isActive, 'text-danger': hasError }"
></div>
```

---

## Multiple Style Values (Vue)

Shows how to provide an array of multiple values for a single style property. The browser will choose the last supported value from the array.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/class-and-style.md#_snippet_29

```vue-html
<div :style="{ display: ['-webkit-box', '-ms-flexbox', 'flex'] }"></div>
```

---

## Component Usage with Class Binding (Vue)

Illustrates how to use class binding when utilizing a Vue component. The 'active' class is dynamically added based on the 'isActive' property.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/class-and-style.md#_snippet_17

```vue-html
<MyComponent :class="{ active: isActive }" />
```

---

## Binding Style to Array (Vue)

Binds the `style` attribute to an array of style objects. This merges multiple style objects and applies them to the same element, useful for applying multiple sets of styles.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/class-and-style.md#_snippet_28

```vue-html
<div :style="[baseStyles, overridingStyles]"></div>
```

---

## Component Template using $attrs (Vue)

Shows how to use `$attrs` in a Vue component's template to bind inherited attributes, including the `class` attribute, to a specific element. This is necessary when the component has multiple root elements.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/class-and-style.md#_snippet_18

```vue-html
<!-- MyComponent template using $attrs -->
<p :class="$attrs.class">Hi!</p>
<span>This is a child component</span>
```

---

## Binding HTML Class to Computed Object (Vue)

Binds the `class` attribute to a computed property that returns a class object. This allows for dynamic class determination based on complex logic and reactive dependencies.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/class-and-style.md#_snippet_9

```vue-html
<div :class="classObject"></div>
```

---

## Component Usage with Class and $attrs (Vue)

Demonstrates using a component with a class attribute and how that attribute is passed down and applied using `$attrs` in the component's template.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/class-and-style.md#_snippet_19

```html
<MyComponent class="baz" />
```

---

## Conditional Class in Array (Vue)

Uses a ternary expression within an array binding for the `class` attribute.  This allows conditionally applying a class based on a truthy value.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/class-and-style.md#_snippet_13

```vue-html
<div :class="[isActive ? activeClass : '', errorClass]"></div>
```

---

## isActive and hasError data properties (Options API)

Defines data properties within Vue's Options API to manage the 'active' and 'hasError' states. These properties are used to conditionally apply CSS classes to a DOM element.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/class-and-style.md#_snippet_2

```javascript
data() {
  return {
    isActive: true,
    hasError: false
  }
}
```

---

## Binding to Reactive classObject (Vue)

Binds the `class` attribute to a reactive `classObject`, dynamically applying classes based on the object's properties. This provides a cleaner way to manage class bindings in the template.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/class-and-style.md#_snippet_6

```vue-html
<div :class="classObject"></div>
```

---

## Object Syntax in Array Binding (Vue)

Combines object and array syntax for `class` binding.  This allows conditional application of classes using the object syntax within an array.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/class-and-style.md#_snippet_14

```vue-html
<div :class="[{ [activeClass]: isActive }, errorClass]"></div>
```

---

## Reactive isActive and hasError (Composition API)

Defines reactive variables using Vue's Composition API to control the 'active' and 'text-danger' classes. These variables are used to dynamically update the class list of an element.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/class-and-style.md#_snippet_1

```javascript
const isActive = ref(true)
const hasError = ref(false)
```

---

## Reactive Class Names (Composition API)

Defines reactive variables using Vue's Composition API to store CSS class names as strings. These variables can be used in array syntax to dynamically apply classes.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/class-and-style.md#_snippet_10

```javascript
const activeClass = ref('active')
const errorClass = ref('text-danger')
```

---

## Reactive Style Properties (Composition API)

Defines reactive variables using Vue's Composition API to store style properties like 'activeColor' and 'fontSize'. These variables can be used to dynamically style an element.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/class-and-style.md#_snippet_20

```javascript
const activeColor = ref('red')
const fontSize = ref(30)
```

---

## Style Object data property (Options API)

Defines a data property within Vue's Options API that holds an object representing inline styles. This allows for dynamic style application based on the properties within the object.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/class-and-style.md#_snippet_25

```javascript
data() {
  return {
    styleObject: {
      color: 'red',
      fontSize: '13px'
    }
  }
}
```

