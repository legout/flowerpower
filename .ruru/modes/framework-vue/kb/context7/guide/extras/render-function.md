# Vue.js Render Functions and JSX

## Dynamic Component Rendering - JavaScript

This snippet shows how to dynamically render components using the `h()` function based on a condition. It imports `Foo` and `Bar` components and conditionally renders either `Foo` or `Bar` based on the value of `ok.value`.

Source: https://github.com/vuejs/docs/blob/main/src/guide/extras/render-function.md#_snippet_20

```JavaScript
import Foo from './Foo.vue'
import Bar from './Bar.jsx'

function render() {
  return ok.value ? h(Foo) : h(Bar)
}
```

---

## v-if Equivalent Render Function - JavaScript (Composition API)

Shows the equivalent of the `v-if` directive using a render function with Composition API. Uses a ternary operator to conditionally render different vnodes.

Source: https://github.com/vuejs/docs/blob/main/src/guide/extras/render-function.md#_snippet_4

```js
h('div', [ok.value ? h('div', 'yes') : h('span', 'no')])
```

---

## Rendering Slots in Composition API - JSX

This JSX code shows how to access and render slots. It accesses the default and named slots, passing props to the named slot.

Source: https://github.com/vuejs/docs/blob/main/src/guide/extras/render-function.md#_snippet_23

```JSX
// default
<div>{slots.default()}</div>

// named
<div>{slots.footer({ text: props.message })}</div>
```

---

## Declaring Render Functions in Options API - JavaScript

Shows how to declare a render function using the `render` option in the Options API. The render function returns a vnode, string, or an array of vnodes, and has access to the component instance via `this`.

Source: https://github.com/vuejs/docs/blob/main/src/guide/extras/render-function.md#_snippet_2

```js
import { h } from 'vue'

export default {
  data() {
    return {
      msg: 'hello'
    }
  },
  render() {
    return h('div', this.msg)
  }
}
```

```js
export default {
  render() {
    return 'hello world!'
  }
}
```

```js
import { h } from 'vue'

export default {
  render() {
    // use an array to return multiple root nodes
    return [
      h('div'),
      h('div'),
      h('div')
    ]
  }
}
```

---

## v-for Equivalent Render Function - JavaScript (Options API)

Demonstrates the equivalent of the `v-for` directive using a render function with Options API. Uses `map` to iterate over an array and generate a list of vnodes.

Source: https://github.com/vuejs/docs/blob/main/src/guide/extras/render-function.md#_snippet_10

```js
h(
  'ul',
  this.items.map(({ id, text }) => {
    return h('li', { key: id }, text)
  })
)
```

---

## Creating Vnodes with h() - JavaScript

Demonstrates how to create virtual DOM nodes (vnodes) using the `h()` function in Vue.js. The `h()` function accepts the element type, props, and children as arguments.

Source: https://github.com/vuejs/docs/blob/main/src/guide/extras/render-function.md#_snippet_0

```js
import { h } from 'vue'

const vnode = h(
  'div', // type
  { id: 'foo', class: 'bar' }, // props
  [
    /* children */
  ]
)
```

---

## Rendering Scoped Slots - Child Component - JavaScript

This code demonstrates the child component providing data to the scoped slot via a function call.

Source: https://github.com/vuejs/docs/blob/main/src/guide/extras/render-function.md#_snippet_29

```JavaScript
// child component
export default {
  setup(props, { slots }) {
    const text = ref('hi')
    return () => h('div', null, slots.default({ text: text.value }))
  }
}
```

---

## Using v-model - Composition API - JavaScript

This code shows how to implement `v-model` functionality in a component using the Composition API and the `h()` function. It handles the `modelValue` prop and emits the `update:modelValue` event.

Source: https://github.com/vuejs/docs/blob/main/src/guide/extras/render-function.md#_snippet_33

```JavaScript
export default {
  props: ['modelValue'],
  emits: ['update:modelValue'],
  setup(props, { emit }) {
    return () =>
      h(SomeComponent, {
        modelValue: props.modelValue,
        'onUpdate:modelValue': (value) => emit('update:modelValue', value)
      })
  }
}
```

---

## Creating Template Refs - Composition API (3.5+) - JavaScript

This code snippet shows how to create a template ref using `useTemplateRef()` (Vue 3.5+) in the Composition API. The ref name is passed as a string prop to the vnode.

Source: https://github.com/vuejs/docs/blob/main/src/guide/extras/render-function.md#_snippet_36

```JavaScript
import { h, useTemplateRef } from 'vue'

export default {
  setup() {
    const divEl = useTemplateRef('my-div')

    // <div ref="my-div">
    return () => h('div', { ref: 'my-div' })
  }
}
```

---

## v-for Equivalent Render Function - JavaScript (Composition API)

Demonstrates the equivalent of the `v-for` directive using a render function with Composition API. Uses `map` to iterate over an array and generate a list of vnodes.

Source: https://github.com/vuejs/docs/blob/main/src/guide/extras/render-function.md#_snippet_8

```js
h(
  'ul',
  // assuming `items` is a ref with array value
  items.value.map(({ id, text }) => {
    return h('li', { key: id }, text)
  })
)
```

---

## v-on Equivalent JSX - JSX

Demonstrates how to handle events using JSX by passing an `onClick` prop. Event listeners are passed as `onXxx` props.

Source: https://github.com/vuejs/docs/blob/main/src/guide/extras/render-function.md#_snippet_13

```jsx
<button
  onClick={(event) => {
    /* ... */
  }}
>
  Click Me
</button>
```

---

## Using v-model - Options API - JavaScript

This code shows how to implement `v-model` functionality in a component using the Options API and the `h()` function. It handles the `modelValue` prop and emits the `update:modelValue` event.

Source: https://github.com/vuejs/docs/blob/main/src/guide/extras/render-function.md#_snippet_34

```JavaScript
export default {
  props: ['modelValue'],
  emits: ['update:modelValue'],
  render() {
    return h(SomeComponent, {
      modelValue: this.modelValue,
      'onUpdate:modelValue': (value) => this.$emit('update:modelValue', value)
    })
  }
}
```

---

## Dynamic Component Rendering - JSX

This snippet shows how to dynamically render components using JSX based on a condition. It imports `Foo` and `Bar` components and conditionally renders either `Foo` or `Bar` based on the value of `ok.value`.

Source: https://github.com/vuejs/docs/blob/main/src/guide/extras/render-function.md#_snippet_21

```JSX
function render() {
  return ok.value ? <Foo /> : <Bar />
}
```

---

## Passing Slots to Components - JavaScript

This code shows how to pass slots to a component using the `h()` function. It demonstrates passing both a single default slot and named slots as functions within an object. The `null` argument is required to avoid the slots object being treated as props.

Source: https://github.com/vuejs/docs/blob/main/src/guide/extras/render-function.md#_snippet_26

```JavaScript
// single default slot
h(MyComponent, () => 'hello')

// named slots
// notice the `null` is required to avoid
// the slots object being treated as props
h(MyComponent, null, {
  default: () => 'default slot',
  foo: () => h('div', 'foo'),
  bar: () => [h('span', 'one'), h('span', 'two')]
})
```

---

## v-on Equivalent Render Function - JavaScript

Demonstrates how to handle events using a render function by passing an `onClick` prop. Event listeners are passed as `onXxx` props.

Source: https://github.com/vuejs/docs/blob/main/src/guide/extras/render-function.md#_snippet_12

```js
h(
  'button',
  {
    onClick(event) {
      /* ... */
    }
  },
  'Click Me'
)
```

---

## Typing Anonymous Functional Component Vue.js TypeScript

This code snippet demonstrates how to type an anonymous functional component in Vue.js using TypeScript. It defines the props and emits for the component, along with the component's rendering logic that includes an onClick event that emits a message.

Source: https://github.com/vuejs/docs/blob/main/src/guide/extras/render-function.md#_snippet_43

```TypeScript
import type { FunctionalComponent } from 'vue'

type FComponentProps = {
  message: string
}

type Events = {
  sendMessage(message: string): void
}

const FComponent: FunctionalComponent<FComponentProps, Events> = (
  props,
  context
) => {
  return (
    <button onClick={() => context.emit('sendMessage', props.message)}>
        {props.message} {' '}
    </button>
  )
}

FComponent.props = {
  message: {
    type: String,
    required: true
  }
}

FComponent.emits = {
  sendMessage: (value) => typeof value === 'string'
}
```

---

## Rendering Built-in Components - Options API - JavaScript

This snippet demonstrates importing and rendering built-in components like `Transition` using the Options API and the `h()` function. These components need to be explicitly imported to be used.

Source: https://github.com/vuejs/docs/blob/main/src/guide/extras/render-function.md#_snippet_32

```JavaScript
import { h, KeepAlive, Teleport, Transition, TransitionGroup } from 'vue'

export default {
  render () {
    return h(Transition, { mode: 'out-in' }, /* ... */)
  }
}
```

---

## Rendering Components with JSX

This code snippet demonstrates how to render Vue components using JSX. It imports `Foo` and `Bar` components and renders them within a `div` element.

Source: https://github.com/vuejs/docs/blob/main/src/guide/extras/render-function.md#_snippet_19

```JSX
function render() {
  return (
    <div>
      <Foo />
      <Bar />
    </div>
  )
}
```

---

## Functional Component Render Function - JavaScript

Demonstrates how to define a simple functional component using a render function. These are ideal for stateless, UI-focused components.

Source: https://github.com/vuejs/docs/blob/main/src/guide/extras/render-function.md#_snippet_3

```js
function Hello() {
  return 'hello world!'
}
```

---

## Passing Slots to Components - JSX

This code shows how to pass slots to a component using JSX. It demonstrates passing both a single default slot and named slots as functions within an object.

Source: https://github.com/vuejs/docs/blob/main/src/guide/extras/render-function.md#_snippet_27

```JSX
// default
<MyComponent>{() => 'hello'}</MyComponent>

// named
<MyComponent>{{
  default: () => 'default slot',
  foo: () => <div>foo</div>,
  bar: () => [<span>one</span>, <span>two</span>]
}}</MyComponent>
```

---

## Event Modifiers - Render Function - JavaScript

Shows how to use event modifiers like `.capture`, `.once` and `.passive` within render functions. Modifiers are concatenated to the event name in camelCase.

Source: https://github.com/vuejs/docs/blob/main/src/guide/extras/render-function.md#_snippet_14

```js
h('input', {
  onClickCapture() {
    /* listener in capture mode */
  },
  onKeyupOnce() {
    /* triggers only once */
  },
  onMouseoverOnceCapture() {
    /* once + capture */
  }
})
```

---

## Rendering Scoped Slots - Parent Component - JavaScript

This code demonstrates rendering a scoped slot in the parent component using the Composition API and the `h()` function. It passes a slot function to the child component that receives data from the child.

Source: https://github.com/vuejs/docs/blob/main/src/guide/extras/render-function.md#_snippet_28

```JavaScript
// parent component
export default {
  setup() {
    return () => h(MyComp, null, {
      default: ({ text }) => h('p', text)
    })
  }
}
```

---

## Rendering Built-in Components - Composition API - JavaScript

This snippet demonstrates importing and rendering built-in components like `Transition` using the Composition API and the `h()` function. These components need to be explicitly imported to be used.

Source: https://github.com/vuejs/docs/blob/main/src/guide/extras/render-function.md#_snippet_31

```JavaScript
import { h, KeepAlive, Teleport, Transition, TransitionGroup } from 'vue'

export default {
  setup () {
    return () => h(Transition, { mode: 'out-in' }, /* ... */)
  }
}
```

---

## Applying Custom Directives - JavaScript

This code demonstrates how to apply custom directives to a vnode using the `withDirectives` helper function and the `h()` function. It showcases creating a custom directive and applying it with arguments and modifiers.

Source: https://github.com/vuejs/docs/blob/main/src/guide/extras/render-function.md#_snippet_35

```JavaScript
import { h, withDirectives } from 'vue'

// a custom directive
const pin = {
  mounted() { /* ... */ },
  updated() { /* ... */ }
}

// <div v-pin:top.animate="200"></div>
const vnode = withDirectives(h('div'), [
  [pin, 200, 'top', { animate: true }]
])
```

---

## Functional Component Definition - Options API - JavaScript

This code shows how to define a functional component, where the first argument will be `props` and the second argument is the `context` containing attrs, emit, and slots.

Source: https://github.com/vuejs/docs/blob/main/src/guide/extras/render-function.md#_snippet_40

```JavaScript
function MyComponent(props, context) {
  // ...
}
```

---

## v-if Equivalent Render Function - JavaScript (Options API)

Shows the equivalent of the `v-if` directive using a render function with Options API. Uses a ternary operator to conditionally render different vnodes.

Source: https://github.com/vuejs/docs/blob/main/src/guide/extras/render-function.md#_snippet_6

```js
h('div', [this.ok ? h('div', 'yes') : h('span', 'no')])
```

---

## Creating Template Refs - Composition API (pre 3.5) - JavaScript

This code snippet shows how to create a template ref using `ref()` in the Composition API, before Vue 3.5. The ref object itself is passed as a prop to the vnode.

Source: https://github.com/vuejs/docs/blob/main/src/guide/extras/render-function.md#_snippet_37

```JavaScript
import { h, ref } from 'vue'

export default {
  setup() {
    const divEl = ref()

    // <div ref="divEl">
    return () => h('div', { ref: divEl })
  }
}
```

---

## Typing Named Functional Component Vue.js TypeScript

This code snippet demonstrates how to type a named functional component in Vue.js using TypeScript. It defines the props and emits for the component, along with the component's rendering logic that includes an onClick event that emits a message.

Source: https://github.com/vuejs/docs/blob/main/src/guide/extras/render-function.md#_snippet_42

```TypeScript
import type { SetupContext } from 'vue'
type FComponentProps = {
  message: string
}

type Events = {
  sendMessage(message: string): void
}

function FComponent(
  props: FComponentProps,
  context: SetupContext<Events>
) {
  return (
    <button onClick={() => context.emit('sendMessage', props.message)}>
        {props.message} {' '}
    </button>
  )
}

FComponent.props = {
  message: {
    type: String,
    required: true
  }
}

FComponent.emits = {
  sendMessage: (value: unknown) => typeof value === 'string'
}
```

---

## Functional Component Props and Emits - JavaScript

This code demonstrates how to define `props` and `emits` for a functional component by adding them as properties to the function.  `inheritAttrs` can be set to `false` to disable attribute inheritance.

Source: https://github.com/vuejs/docs/blob/main/src/guide/extras/render-function.md#_snippet_41

```JavaScript
MyComponent.props = ['value']
MyComponent.emits = ['click']
MyComponent.inheritAttrs = false
```

---

## Declaring Render Functions in Composition API - JavaScript

Shows how to declare a render function within the `setup()` hook when using the Composition API. The render function returns a vnode, string, or an array of vnodes.

Source: https://github.com/vuejs/docs/blob/main/src/guide/extras/render-function.md#_snippet_1

```js
import { ref, h } from 'vue'

export default {
  props: {
    /* ... */
  },
  setup(props) {
    const count = ref(1)

    // return the render function
    return () => h('div', props.msg + count.value)
  }
}
```

```js
export default {
  setup() {
    return () => 'hello world!'
  }
}
```

```js
import { h } from 'vue'

export default {
  setup() {
    // use an array to return multiple root nodes
    return () => [
      h('div'),
      h('div'),
      h('div')
    ]
  }
}
```

---

## withModifiers Helper - Render Function - JavaScript

Demonstrates how to use the `withModifiers` helper function to apply event modifiers like `.self` within render functions.

Source: https://github.com/vuejs/docs/blob/main/src/guide/extras/render-function.md#_snippet_16

```js
import { withModifiers } from 'vue'

h('div', {
  onClick: withModifiers(() => {}, ['self'])
})
```

