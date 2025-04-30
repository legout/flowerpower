# Vue.js Built-in Components API

## KeepAlive Basic Usage - Vue HTML

This example demonstrates the basic usage of the `<KeepAlive>` component. It wraps a dynamic component (`<component :is="view">`), caching the component instance when it's not active.

Source: https://github.com/vuejs/docs/blob/main/src/api/built-in-components.md#_snippet_6

```vue-html
<KeepAlive>
  <component :is="view"></component>
</KeepAlive>
```

---

## KeepAlive with v-if / v-else - Vue HTML

This example shows how to use `<KeepAlive>` with `v-if` and `v-else` directives. Only one component should be rendered at a time within the `<KeepAlive>` component.

Source: https://github.com/vuejs/docs/blob/main/src/api/built-in-components.md#_snippet_7

```vue-html
<KeepAlive>
  <comp-a v-if="a > 1"></comp-a>
  <comp-b v-else></comp-b>
</KeepAlive>
```

---

## KeepAlive with Include / Exclude - Vue HTML

This example showcases the usage of the `include` prop of `<KeepAlive>`. It caches only the components whose names match the specified string, RegExp, or array of strings and RegExps. The `exclude` prop works similarly, but it excludes matching components from being cached.

Source: https://github.com/vuejs/docs/blob/main/src/api/built-in-components.md#_snippet_9

```vue-html
<!-- comma-delimited string -->
<KeepAlive include="a,b">
  <component :is="view"></component>
</KeepAlive>

<!-- regex (use `v-bind`) -->
<KeepAlive :include="/a|b/">
  <component :is="view"></component>
</KeepAlive>

<!-- Array (use `v-bind`) -->
<KeepAlive :include="['a', 'b']">
  <component :is="view"></component>
</KeepAlive>
```

---

## KeepAlive with Max - Vue HTML

This example shows the usage of the `max` prop of the `<KeepAlive>` component. The `max` prop limits the maximum number of component instances to cache. Once the limit is reached, the least recently used cached component instance will be destroyed to make room for a new one.

Source: https://github.com/vuejs/docs/blob/main/src/api/built-in-components.md#_snippet_10

```vue-html
<KeepAlive :max="10">
  <component :is="view"></component>
</KeepAlive>
```

---

## Dynamic Component Transition - Vue HTML

This example uses the `<Transition>` component with a dynamic component (`<component :is="view">`). It also specifies a `name` for CSS class generation, sets the `mode` to `out-in` for a specific transition order, and uses `appear` to animate on initial render.

Source: https://github.com/vuejs/docs/blob/main/src/api/built-in-components.md#_snippet_3

```vue-html
<Transition name="fade" mode="out-in" appear>
  <component :is="view"></component>
</Transition>
```

---

## Transition with Event Listener - Vue HTML

This example demonstrates how to listen to transition events, specifically the `@after-enter` event. When the transition completes after entering, the `onTransitionComplete` method will be called.

Source: https://github.com/vuejs/docs/blob/main/src/api/built-in-components.md#_snippet_4

```vue-html
<Transition @after-enter="onTransitionComplete">
  <div v-show="ok">toggled content</div>
</Transition>
```

---

## Import Transition Component in Render Function - JavaScript

This code snippet demonstrates how to import the `Transition` component from Vue.js for use within a render function. It's necessary to explicitly import built-in components when using render functions.

Source: https://github.com/vuejs/docs/blob/main/src/api/built-in-components.md#_snippet_0

```javascript
import { h, Transition } from 'vue'

h(Transition, {
  /* props */
})
```

---

## KeepAlive with Transition - Vue HTML

This example demonstrates the combined usage of `<Transition>` and `<KeepAlive>`. The `<KeepAlive>` component caches the dynamic component, and the `<Transition>` component applies transition effects when the component is toggled.

Source: https://github.com/vuejs/docs/blob/main/src/api/built-in-components.md#_snippet_8

```vue-html
<Transition>
  <KeepAlive>
    <component :is="view"></component>
  </KeepAlive>
</Transition>
```

---

## Teleport with Target Selector - Vue HTML

This example shows how to use the `to` prop of the `<Teleport>` component to specify the target container where the teleported content will be rendered. The target can be a CSS selector string or an actual DOM element. These examples demonstrate different types of CSS selectors.

Source: https://github.com/vuejs/docs/blob/main/src/api/built-in-components.md#_snippet_11

```vue-html
<Teleport to="#some-id" />
<Teleport to=".some-class" />
<Teleport to="[data-teleport]" />
```

