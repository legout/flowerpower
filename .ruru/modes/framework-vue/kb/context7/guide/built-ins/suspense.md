# Vue.js Suspense Component

## Async setup() with <script setup>

This Vue.js code shows how to use top-level await expressions within a `<script setup>` block, making the component an async dependency. It fetches data and makes it available in the template.

Source: https://github.com/vuejs/docs/blob/main/src/guide/built-ins/suspense.md#_snippet_1

```vue
<script setup>
const res = await fetch(...)
const posts = await res.json()
</script>

<template>
  {{ posts }}
</template>
```

---

## Combining Suspense with Transition, KeepAlive and RouterView

This HTML snippet shows how to combine `<Suspense>` with `<Transition>`, `<KeepAlive>`, and `<RouterView>` components in Vue.js, ensuring they all work together correctly. The `<RouterView>` uses a slot prop to access the current component, which is then wrapped by `<Transition>`, `<KeepAlive>`, and `<Suspense>`.

Source: https://github.com/vuejs/docs/blob/main/src/guide/built-ins/suspense.md#_snippet_3

```vue-html
<RouterView v-slot="{ Component }">
  <template v-if="Component">
    <Transition mode="out-in">
      <KeepAlive>
        <Suspense>
          <!-- main content -->
          <component :is="Component"></component>

          <!-- loading state -->
          <template #fallback>
            Loading...
          </template>
        </Suspense>
      </KeepAlive>
    </Transition>
  </template>
</RouterView>
```

---

## Async setup() Hook

This JavaScript snippet demonstrates how to define an async setup() hook in a Vue.js component. The component fetches data asynchronously and returns it to be used in the template.

Source: https://github.com/vuejs/docs/blob/main/src/guide/built-ins/suspense.md#_snippet_0

```javascript
export default {
  async setup() {
    const res = await fetch(...)
    const posts = await res.json()
    return {
      posts
    }
  }
}
```

---

## Nested Suspense Component Usage

This HTML snippet demonstrates how to use nested `<Suspense>` components in Vue.js. It shows a scenario where an inner `<Suspense>` is used to handle async components nested within another async component.

Source: https://github.com/vuejs/docs/blob/main/src/guide/built-ins/suspense.md#_snippet_4

```vue-html
<Suspense>
  <component :is="DynamicAsyncOuter">
    <component :is="DynamicAsyncInner" />
  </component>
</Suspense>
```

---

## Nested Suspense with suspensible prop

This HTML snippet demonstrates the use of nested `<Suspense>` components in Vue.js with the `suspensible` prop. It shows how the parent `<Suspense>` can handle async dependencies for the nested component.

Source: https://github.com/vuejs/docs/blob/main/src/guide/built-ins/suspense.md#_snippet_5

```vue-html
<Suspense>
  <component :is="DynamicAsyncOuter">
    <Suspense suspensible> <!-- this -->
      <component :is="DynamicAsyncInner" />
    </Suspense>
  </component>
</Suspense>
```

---

## Suspense Component Usage

This HTML snippet demonstrates the basic usage of the `<Suspense>` component in Vue.js. It defines a default slot containing a component with potentially async dependencies and a fallback slot for the loading state.

Source: https://github.com/vuejs/docs/blob/main/src/guide/built-ins/suspense.md#_snippet_2

```vue-html
<Suspense>
  <!-- component with nested async dependencies -->
  <Dashboard />

  <!-- loading state via #fallback slot -->
  <template #fallback>
    Loading...
  </template>
</Suspense>
```

