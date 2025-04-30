# Vue.js Component Lifecycle Options

## Initializing created Lifecycle Hook in Vue.js

Defines the `created` lifecycle hook, which is called after a Vue.js component instance has finished processing all state-related options, such as reactive data, computed properties, methods, and watchers. The mounting phase has not yet started when this hook is called.

Source: https://github.com/vuejs/docs/blob/main/src/api/options-lifecycle.md#_snippet_1

```typescript
interface ComponentOptions {
  created?(this: ComponentPublicInstance): void
}
```

---

## ServerPrefetch Example - JavaScript

Demonstrates the usage of the 'serverPrefetch' lifecycle hook within a Vue.js component to pre-fetch data on the server. If the component is dynamically rendered on the client, the data is fetched in the 'mounted' hook. The `fetchOnServer` and `fetchOnClient` functions are assumed to exist and perform the actual data fetching.

Source: https://github.com/vuejs/docs/blob/main/src/api/options-lifecycle.md#_snippet_14

```JavaScript
export default {
  data() {
    return {
      data: null
    }
  },
  async serverPrefetch() {
    // component is rendered as part of the initial request
    // pre-fetch data on server as it is faster than on the client
    this.data = await fetchOnServer(/* ... */)
  },
  async mounted() {
    if (!this.data) {
      // if data is null on mount, it means the component
      // is dynamically rendered on the client. Perform a
      // client-side fetch instead.
      this.data = await fetchOnClient(/* ... */)
    }
  }
}
```

---

## Initializing beforeUpdate Lifecycle Hook in Vue.js

Defines the `beforeUpdate` lifecycle hook, which is called right before a Vue.js component is about to update its DOM tree due to a reactive state change. This hook can be used to access the DOM state before Vue updates the DOM. This hook is not called during server-side rendering.

Source: https://github.com/vuejs/docs/blob/main/src/api/options-lifecycle.md#_snippet_4

```typescript
interface ComponentOptions {
  beforeUpdate?(this: ComponentPublicInstance): void
}
```

---

## Initializing updated Lifecycle Hook in Vue.js

Defines the `updated` lifecycle hook, which is called after a Vue.js component has updated its DOM tree due to a reactive state change. This hook is called after any DOM update of the component. This hook is not called during server-side rendering.

Source: https://github.com/vuejs/docs/blob/main/src/api/options-lifecycle.md#_snippet_5

```typescript
interface ComponentOptions {
  updated?(this: ComponentPublicInstance): void
}
```

---

## Initializing beforeUnmount Lifecycle Hook in Vue.js

Defines the `beforeUnmount` lifecycle hook, which is called right before a Vue.js component instance is to be unmounted. When this hook is called, the component instance is still fully functional. This hook is not called during server-side rendering.

Source: https://github.com/vuejs/docs/blob/main/src/api/options-lifecycle.md#_snippet_6

```typescript
interface ComponentOptions {
  beforeUnmount?(this: ComponentPublicInstance): void
}
```

---

## Initializing mounted Lifecycle Hook in Vue.js

Defines the `mounted` lifecycle hook, which is called after a Vue.js component has been mounted. The component is considered mounted when all synchronous child components have been mounted and its DOM tree has been created and inserted into the parent container. This hook is not called during server-side rendering.

Source: https://github.com/vuejs/docs/blob/main/src/api/options-lifecycle.md#_snippet_3

```typescript
interface ComponentOptions {
  mounted?(this: ComponentPublicInstance): void
}
```

---

## Initializing unmounted Lifecycle Hook in Vue.js

Defines the `unmounted` lifecycle hook, which is called after a Vue.js component has been unmounted. Use this hook to clean up manually created side effects such as timers, DOM event listeners, or server connections. This hook is not called during server-side rendering.

Source: https://github.com/vuejs/docs/blob/main/src/api/options-lifecycle.md#_snippet_7

```typescript
interface ComponentOptions {
  unmounted?(this: ComponentPublicInstance): void
}
```

---

## Initializing renderTracked Lifecycle Hook in Vue.js

Defines the `renderTracked` lifecycle hook, which is called when a reactive dependency has been tracked by the component's render effect. This hook is development-mode-only and not called during server-side rendering. It provides debugging information about the reactive effect.

Source: https://github.com/vuejs/docs/blob/main/src/api/options-lifecycle.md#_snippet_9

```typescript
interface ComponentOptions {
  renderTracked?(this: ComponentPublicInstance, e: DebuggerEvent): void
}

type DebuggerEvent = {
  effect: ReactiveEffect
  target: object
  type: TrackOpTypes /* 'get' | 'has' | 'iterate' */
  key: any
}
```

