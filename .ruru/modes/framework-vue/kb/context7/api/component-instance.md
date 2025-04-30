# Vue.js Component Instance Properties and Methods

## Component Refs Type Definition (TypeScript)

This TypeScript interface defines the type for the `$refs` property, an object of DOM elements and component instances registered via template refs.

Source: https://github.com/vuejs/docs/blob/main/src/api/component-instance.md#_snippet_8

```typescript
interface ComponentPublicInstance {
  $refs: { [name: string]: Element | ComponentPublicInstance | null }
}
```

---

## Component Force Update Type Definition (TypeScript)

This TypeScript interface defines the `$forceUpdate` method for forcing the component instance to re-render. It should be rarely needed given Vue's fully automatic reactivity system.

Source: https://github.com/vuejs/docs/blob/main/src/api/component-instance.md#_snippet_14

```typescript
interface ComponentPublicInstance {
  $forceUpdate(): void
}
```

---

## Component Watch Examples (JavaScript)

These JavaScript examples demonstrate different ways to use the `$watch` method: watching a property name, a dot-delimited path, and a complex expression using a getter function. It also shows how to stop a watcher.

Source: https://github.com/vuejs/docs/blob/main/src/api/component-instance.md#_snippet_11

```javascript
this.$watch('a', (newVal, oldVal) => {})

```

```javascript
this.$watch('a.b', (newVal, oldVal) => {})

```

```javascript
this.$watch(
  // every time the expression `this.a + this.b` yields
  // a different result, the handler will be called.
  // It's as if we were watching a computed property
  // without defining the computed property itself.
  () => this.a + this.b,
  (newVal, oldVal) => {}
)
```

```javascript
const unwatch = this.$watch('a', cb)

// later...
unwatch()
```

---

## Component Options Type Definition (TypeScript)

This TypeScript interface defines the type for the `$options` property, which exposes the resolved component options used for instantiating the current component instance. It's the merge result of global mixins, component `extends` base, and component mixins.

Source: https://github.com/vuejs/docs/blob/main/src/api/component-instance.md#_snippet_3

```typescript
interface ComponentPublicInstance {
  $options: ComponentOptions
}
```

---

## Component Emit Type Definition (TypeScript)

This TypeScript interface defines the `$emit` method for triggering custom events on the current component instance. It takes an event name and any number of additional arguments to be passed to the listener's callback function.

Source: https://github.com/vuejs/docs/blob/main/src/api/component-instance.md#_snippet_12

```typescript
interface ComponentPublicInstance {
  $emit(event: string, ...args: any[]): void
}
```

---

## Component Props Type Definition (TypeScript)

This TypeScript interface defines the type for the `$props` property on a Vue component instance.  It holds the resolved props declared using the `props` option. The component instance proxies access to properties on this props object.

Source: https://github.com/vuejs/docs/blob/main/src/api/component-instance.md#_snippet_1

```typescript
interface ComponentPublicInstance {
  $props: object
}
```

