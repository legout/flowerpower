# Vue.js Render Function APIs Documentation

## Creating Components with h() in Vue.js

This snippet illustrates how to create Vue.js component VNodes using the `h()` function. It demonstrates passing props, single default slots, and named slots to components.

Source: https://github.com/vuejs/docs/blob/main/src/api/render-function.md#_snippet_1

```javascript
import Foo from './Foo.vue'

// passing props
h(Foo, {
  // equivalent of some-prop="hello"
  someProp: 'hello',
  // equivalent of @update="() => {}"
  onUpdate: () => {}
})

// passing single default slot
h(Foo, () => 'default slot')

// passing named slots
// notice the `null` is required to avoid
// slots object being treated as props
h(MyComponent, null, {
  default: () => 'default slot',
  foo: () => h('div', 'foo'),
  bar: () => [h('span', 'one'), h('span', 'two')]
})
```

---

## Merging Props with mergeProps() in Vue.js

This snippet demonstrates how to use the `mergeProps()` function in Vue.js to merge multiple props objects.  It showcases the special handling for `class`, `style`, and `onXxx` event listeners, where multiple listeners are merged into an array.

Source: https://github.com/vuejs/docs/blob/main/src/api/render-function.md#_snippet_2

```javascript
import { mergeProps } from 'vue'

const one = {
  class: 'foo',
  onClick: handlerA
}

const two = {
  class: { bar: true },
  onClick: handlerB
}

const merged = mergeProps(one, two)
/**
 {
   class: 'foo bar',
   onClick: [handlerA, handlerB]
 }
 */
```

---

## Resolving Component with resolveComponent() in Vue.js Options API

This snippet demonstrates resolving a registered component by name using `resolveComponent()` within the options API render function. It shows how to render the resolved component using the `h` function.

Source: https://github.com/vuejs/docs/blob/main/src/api/render-function.md#_snippet_5

```javascript
import { h, resolveComponent } from 'vue'

export default {
  render() {
    const ButtonCounter = resolveComponent('ButtonCounter')
    return h(ButtonCounter)
  }
}
```

---

## Adding Directives with withDirectives() in Vue.js

This snippet demonstrates how to add custom directives to VNodes using the `withDirectives()` function in Vue.js. It creates a VNode and wraps it with a custom directive, including a value, argument, and modifiers.

Source: https://github.com/vuejs/docs/blob/main/src/api/render-function.md#_snippet_6

```javascript
import { h, withDirectives } from 'vue'

// a custom directive
const pin = {
  mounted() {
    /* ... */
  },
  updated() {
    /* ... */
  }
}

// <div v-pin:top.animate="200"></div>
const vnode = withDirectives(h('div'), [
  [pin, 200, 'top', { animate: true }]
])
```

