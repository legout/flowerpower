# Vue.js Reactivity API: Advanced

## markRaw() Usage in Vue.js

Demonstrates how to use `markRaw()` to prevent an object from being converted to a proxy. It shows that `isReactive(reactive(foo))` returns `false` when `foo` is marked as raw. Also demonstrates nested usage where a raw object is nested inside reactive objects.

Source: https://github.com/vuejs/docs/blob/main/src/api/reactivity-advanced.md#_snippet_7

```javascript
const foo = markRaw({})
console.log(isReactive(reactive(foo))) // false

// also works when nested inside other reactive objects
const bar = reactive({ foo })
console.log(isReactive(bar.foo)) // false
```

---

## Identity Hazard Example with markRaw()

Illustrates a potential identity hazard when using `markRaw()` with nested objects. While the top-level object is raw, nested objects are still reactive, leading to `foo.nested === bar.nested` evaluating to `false` because one is proxied and the other is not.

Source: https://github.com/vuejs/docs/blob/main/src/api/reactivity-advanced.md#_snippet_8

```javascript
const foo = markRaw({
  nested: {}
})

const bar = reactive({
  // although `foo` is marked as raw, foo.nested is not.
  nested: foo.nested
})

console.log(foo.nested === bar.nested) // false
```

---

## effectScope() Example in Vue.js

Shows how to create and use an `effectScope()` to manage reactive effects like `computed` and `watch`. It includes creating a scope, running effects within the scope, and stopping the scope to dispose of all effects.

Source: https://github.com/vuejs/docs/blob/main/src/api/reactivity-advanced.md#_snippet_9

```javascript
const scope = effectScope()

scope.run(() => {
  const doubled = computed(() => counter.value * 2)

  watch(doubled, () => console.log(doubled.value))

  watchEffect(() => console.log('Count: ', doubled.value))
})

// to dispose all effects in the scope
scope.stop()
```

---

## Type Definition of getCurrentScope() in TypeScript

Defines the TypeScript type signature for the `getCurrentScope()` function. It returns the current active EffectScope or undefined if there is none.

Source: https://github.com/vuejs/docs/blob/main/src/api/reactivity-advanced.md#_snippet_12

```typescript
function getCurrentScope(): EffectScope | undefined
```

---

## Shallow Readonly Usage

Illustrates how to use `shallowReadonly` to create an object where only root-level properties are readonly, not nested objects.

Source: https://github.com/vuejs/docs/blob/main/src/api/reactivity-advanced.md#_snippet_5

```javascript
const state = shallowReadonly({
  foo: 1,
  nested: {
    bar: 2
  }
})

// mutating state's own properties will fail
state.foo++

// ...but works on nested objects
isReadonly(state.nested) // false

// works
state.nested.bar++
```

---

## Custom Ref Implementation

Illustrates how to create a debounced ref using `customRef`, which allows explicit control over dependency tracking and update triggering, updating the value only after a certain timeout.

Source: https://github.com/vuejs/docs/blob/main/src/api/reactivity-advanced.md#_snippet_2

```javascript
import { customRef } from 'vue'

export function useDebouncedRef(value, delay = 200) {
  let timeout
  return customRef((track, trigger) => {
    return {
      get() {
        track()
        return value
      },
      set(newValue) {
        clearTimeout(timeout)
        timeout = setTimeout(() => {
          value = newValue
          trigger()
        }, delay)
      }
    }
  })
}
```

