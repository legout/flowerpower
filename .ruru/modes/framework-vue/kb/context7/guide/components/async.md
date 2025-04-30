# Async Components in Vue.js

## Async Component with Dynamic Import

This snippet shows how to use `defineAsyncComponent` with ES module dynamic import. Bundlers like Vite and webpack support this syntax and will use it as bundle split points.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/async.md#_snippet_1

```javascript
import { defineAsyncComponent } from 'vue'

const AsyncComp = defineAsyncComponent(() =>
  import('./components/MyComponent.vue')
)
```

---

## Async Component with Loading and Error States

This snippet shows how to configure loading and error components for an async component using the `defineAsyncComponent` options.  It configures loadingComponent, delay, errorComponent, and timeout.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/async.md#_snippet_5

```javascript
const AsyncComp = defineAsyncComponent({
  // the loader function
  loader: () => import('./Foo.vue'),

  // A component to use while the async component is loading
  loadingComponent: LoadingComponent,
  // Delay before showing the loading component. Default: 200ms.
  delay: 200,

  // A component to use if the load fails
  errorComponent: ErrorComponent,
  // The error component will be displayed if a timeout is
  // provided and exceeded. Default: Infinity.
  timeout: 3000
})
```

---

## Globally Registering Async Component

This snippet demonstrates how to register an async component globally using `app.component()`. This makes the component available throughout the application.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/async.md#_snippet_2

```javascript
app.component('MyComponent', defineAsyncComponent(() =>
  import('./components/MyComponent.vue')
))
```

---

## Locally Registering Async Component (Composition API)

This snippet demonstrates how to register an async component locally using the composition API with `<script setup>`. The component is only available within the scope of the parent component.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/async.md#_snippet_4

```vue
<script setup>
import { defineAsyncComponent } from 'vue'

const AdminPage = defineAsyncComponent(() =>
  import('./components/AdminPageComponent.vue')
)
</script>

<template>
  <AdminPage />
</template>
```

---

## Async Component with Hydrate on Interaction

This snippet demonstrates how to use `hydrateOnInteraction` with an async component for lazy hydration, hydrating when specified event(s) are triggered on the component element(s).

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/async.md#_snippet_9

```javascript
import { defineAsyncComponent, hydrateOnInteraction } from 'vue'

const AsyncComp = defineAsyncComponent({
  loader: () => import('./Comp.vue'),
  hydrate: hydrateOnInteraction('click')
})
```

```javascript
hydrateOnInteraction(['wheel', 'mouseover'])
```

---

## Defining Basic Async Component

This snippet demonstrates the basic usage of `defineAsyncComponent` to load a component asynchronously. It shows how to use a Promise to resolve the component definition.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/async.md#_snippet_0

```javascript
import { defineAsyncComponent } from 'vue'

const AsyncComp = defineAsyncComponent(() => {
  return new Promise((resolve, reject) => {
    // ...load component from server
    resolve(/* loaded component */)
  })
})
// ... use `AsyncComp` like a normal component
```

---

## Async Component with Hydrate on Idle

This snippet demonstrates how to use `hydrateOnIdle` with an async component for lazy hydration, which hydrates via `requestIdleCallback`.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/async.md#_snippet_6

```javascript
import { defineAsyncComponent, hydrateOnIdle } from 'vue'

const AsyncComp = defineAsyncComponent({
  loader: () => import('./Comp.vue'),
  hydrate: hydrateOnIdle(/* optionally pass a max timeout */)
})
```

---

## Async Component with Hydrate on Visible

This snippet demonstrates how to use `hydrateOnVisible` with an async component for lazy hydration, hydrating when element(s) become visible via `IntersectionObserver`.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/async.md#_snippet_7

```javascript
import { defineAsyncComponent, hydrateOnVisible } from 'vue'

const AsyncComp = defineAsyncComponent({
  loader: () => import('./Comp.vue'),
  hydrate: hydrateOnVisible()
})
```

```javascript
hydrateOnVisible({ rootMargin: '100px' })
```

---

## Async Component with Custom Hydration Strategy

This snippet demonstrates how to define and use a custom hydration strategy for an async component, providing fine-grained control over the hydration process.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/async.md#_snippet_10

```typescript
import { defineAsyncComponent, type HydrationStrategy } from 'vue'

const myStrategy: HydrationStrategy = (hydrate, forEachElement) => {
  // forEachElement is a helper to iterate through all the root elements
  // in the component's non-hydrated DOM, since the root can be a fragment
  // instead of a single element
  forEachElement(el => {
    // ...
  })
  // call `hydrate` when ready
  hydrate()
  return () => {
    // return a teardown function if needed
  }
}

const AsyncComp = defineAsyncComponent({
  loader: () => import('./Comp.vue'),
  hydrate: myStrategy
})
```

