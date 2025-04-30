# Vue.js Component Basics

## Using a Component (Options API) Vue

Demonstrates how to import and register a child component (ButtonCounter.vue) within a parent component using the Options API. The `components` option registers the imported `ButtonCounter` making it available for use in the template.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/component-basics.md#_snippet_4

```vue
<script>
import ButtonCounter from './ButtonCounter.vue'

export default {
  components: {
    ButtonCounter
  }
}
</script>

<template>
  <h1>Here is a child component!</h1>
  <ButtonCounter />
</template>
```

---

## Defining a Component (Options API) JavaScript

Defines a Vue component as a plain JavaScript object using the Options API. The `data` option initializes the `count` property. The `template` option provides an inlined HTML string that displays a button which, when clicked, increments the value of count.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/component-basics.md#_snippet_2

```javascript
export default {
  data() {
    return {
      count: 0
    }
  },
  template: `
    <button @click="count++">
      You clicked me {{ count }} times.
    </button>`
}
```

---

## Defining a Component (Composition API) Vue

Defines a Vue component using the Composition API within a Single-File Component (SFC).  It imports the `ref` function from Vue and uses it to create a reactive `count` variable initialized to 0.  The template displays the current value of `count` and increments it on button click.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/component-basics.md#_snippet_1

```vue
<script setup>
import { ref } from 'vue'

const count = ref(0)
</script>

<template>
  <button @click="count++">You clicked me {{ count }} times.</button>
</template>
```

---

## Accessing Props in Options API setup function

This snippet shows how to access props within the `setup` function of a Vue component using the Options API. The `props` object is passed as the first argument to the `setup` function.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/component-basics.md#_snippet_11

```js
export default {
  props: ['title'],
  setup(props) {
    console.log(props.title)
  }
}
```

---

## Defining a Component (Options API) Vue

Defines a Vue component using the Options API within a Single-File Component (SFC). It exports a default object with a `data` option that initializes the `count` property to 0. The template uses the `count` data property and increments it on button click.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/component-basics.md#_snippet_0

```vue
<script>
export default {
  data() {
    return {
      count: 0
    }
  }
}
</script>

<template>
  <button @click="count++">You clicked me {{ count }} times.</button>
</template>
```

---

## Defining a Component (Composition API) JavaScript

Defines a Vue component as a plain JavaScript object using the Composition API. It imports the `ref` function from Vue, initializes a reactive `count` variable using `ref(0)`, and exposes `count` through the `setup` function's return value. The template uses an inlined HTML string to display a button that increments `count` on click.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/component-basics.md#_snippet_3

```javascript
import { ref } from 'vue'

export default {
  setup() {
    const count = ref(0)
    return { count }
  },
  template: `
    <button @click="count++">
      You clicked me {{ count }} times.
    </button>`
  // Can also target an in-DOM template:
  // template: '#my-template-element'
}
```

---

## Declaring Props in Composition API Vue Component

This snippet demonstrates how to declare props in a Vue component using the Composition API with script setup. It uses `defineProps` to declare the 'title' prop and renders it in the template.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/component-basics.md#_snippet_9

```vue
<!-- BlogPost.vue -->
<script setup>
defineProps(['title'])
</script>

<template>
  <h4>{{ title }}</h4>
</template>
```

---

## AlertBox Component with Slot in Vue

Defines a Vue component named `AlertBox` that uses a `<slot>` element. The `<slot>` element allows the component to accept and render content passed to it from its parent. The component template defines a styled div containing a heading and a slot for dynamic content.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/component-basics.md#_snippet_27

```vue
<!-- AlertBox.vue -->
<template>
  <div class="alert-box">
    <strong>This is an Error for Demo Purposes</strong>
    <slot />
  </div>
</template>

<style scoped>
.alert-box {
  /* ... */
}
</style>
```

---

## Passing Props via HTML Attributes

This snippet shows how to pass prop values to a Vue component using HTML attributes. It passes the 'title' prop to the BlogPost component.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/component-basics.md#_snippet_12

```html
<BlogPost title="My journey with Vue" />
<BlogPost title="Blogging with Vue" />
<BlogPost title="Why Vue is so fun" />
```

---

## Using a Component (Composition API) Vue

Shows how to import and use a child component (ButtonCounter.vue) within a parent component using the Composition API with `<script setup>`.  The imported component is automatically available in the template.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/component-basics.md#_snippet_5

```vue
<script setup>
import ButtonCounter from './ButtonCounter.vue'
</script>

<template>
  <h1>Here is a child component!</h1>
  <ButtonCounter />
</template>
```

---

## Reusing Components Vue-HTML

Demonstrates the reusability of components by displaying the ButtonCounter component multiple times.  Each instance of the component maintains its own independent state.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/component-basics.md#_snippet_6

```vue-html
<h1>Here are many child components!</h1>
<ButtonCounter />
<ButtonCounter />
<ButtonCounter />
```

---

## Defining Posts Array in Composition API

This snippet demonstrates how to define an array of posts using `ref` in a Vue component using the Composition API.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/component-basics.md#_snippet_14

```js
const posts = ref([
  { id: 1, title: 'My journey with Vue' },
  { id: 2, title: 'Blogging with Vue' },
  { id: 3, title: 'Why Vue is so fun' }
])
```

---

## Incorrect Self-Closing Tag Example in Vue (In-DOM)

Illustrates the problem that occurs when using a self-closing tag for a component in in-DOM templates. The browser incorrectly interprets the subsequent element as content within the component, leading to unexpected rendering.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/component-basics.md#_snippet_33

```vue-html
<my-component /> <!-- we intend to close the tag here... -->
<span>hello</span>
```

---

## Defining Posts Array in Options API

This snippet demonstrates how to define an array of posts in the data property of a Vue component using the Options API.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/component-basics.md#_snippet_13

```js
export default {
  // ...
  data() {
    return {
      posts: [
        { id: 1, title: 'My journey with Vue' },
        { id: 2, title: 'Blogging with Vue' },
        { id: 3, title: 'Why Vue is so fun' }
      ]
    }
  }
}
```

---

## Emitting Events in Options API setup function

Shows how to emit custom events using `ctx.emit` within the setup function when using the Options API.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/component-basics.md#_snippet_25

```js
export default {
  emits: ['enlarge-text'],
  setup(props, ctx) {
    ctx.emit('enlarge-text')
  }
}
```

