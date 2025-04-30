# Vue Reactivity in Depth

## Pseudo-code for Vue Reactivity with Proxy and Getter/Setter

Illustrates the core concepts of Vue's reactivity system using pseudo-code.  It showcases how `reactive()` uses Proxies to intercept property access and trigger dependency tracking (`track()`) and updates (`trigger()`).  Similarly, `ref()` uses getter/setters for reactive primitive values. This snippet highlights the key mechanisms behind Vue's reactivity.

Source: https://github.com/vuejs/docs/blob/main/src/guide/extras/reactivity-in-depth.md#_snippet_2

```javascript
function reactive(obj) {
  return new Proxy(obj, {
    get(target, key) {
      track(target, key)
      return target[key]
    },
    set(target, key, value) {
      target[key] = value
      trigger(target, key)
    }
  })
}

function ref(value) {
  const refObject = {
    get value() {
      track(refObject, 'value')
      return value
    },
    set value(newValue) {
      value = newValue
      trigger(refObject, 'value')
    }
  }
  return refObject
}
```

---

## Component Debugging Hooks (Options API)

This snippet demonstrates how to use `renderTracked` and `renderTriggered` lifecycle hooks in Vue's Options API to debug component re-renders. A debugger statement is placed within the callbacks to interactively inspect the dependencies being tracked and triggering updates. This only works in development mode.

Source: https://github.com/vuejs/docs/blob/main/src/guide/extras/reactivity-in-depth.md#_snippet_10

```javascript
export default {
  renderTracked(event) {
    debugger
  },
  renderTriggered(event) {
    debugger
  }
}
```

---

## Integrating XState with Vue (JavaScript)

This JavaScript code provides a composable function `useMachine` that integrates XState with Vue. It creates a state machine, a shallow ref to hold the current state, and uses the `interpret` function from XState to manage the state machine's lifecycle.  It returns the current state and a send function to send events to the state machine.

Source: https://github.com/vuejs/docs/blob/main/src/guide/extras/reactivity-in-depth.md#_snippet_15

```javascript
import { createMachine, interpret } from 'xstate'
import { shallowRef } from 'vue'

export function useMachine(options) {
  const machine = createMachine(options)
  const state = shallowRef(machine.initialState)
  const service = interpret(machine)
    .onTransition((newState) => (state.value = newState))
    .start()
  const send = (event) => service.send(event)

  return [state, send]
}
```

---

## Vue Reactivity with ref and computed

Demonstrates how to use Vue's `computed` property to create a reactive value that automatically updates when its dependencies change. This is a more declarative approach than using `watchEffect` for simple calculations.

Source: https://github.com/vuejs/docs/blob/main/src/guide/extras/reactivity-in-depth.md#_snippet_7

```javascript
import { ref, computed } from 'vue'

const A0 = ref(0)
const A1 = ref(1)
const A2 = computed(() => A0.value + A1.value)

A0.value = 2
```

---

## Computed Property Debugging (JavaScript)

This JavaScript code shows how to debug computed properties using the `onTrack` and `onTrigger` options. The `onTrack` callback is triggered when a reactive property or ref is tracked as a dependency, and the `onTrigger` callback is triggered when a dependency is mutated.  These options only work in development mode.

Source: https://github.com/vuejs/docs/blob/main/src/guide/extras/reactivity-in-depth.md#_snippet_12

```javascript
const plusOne = computed(() => count.value + 1, {
  onTrack(e) {
    // triggered when count.value is tracked as a dependency
    debugger
  },
  onTrigger(e) {
    // triggered when count.value is mutated
    debugger
  }
})

// access plusOne, should trigger onTrack
console.log(plusOne.value)

// mutate count.value, should trigger onTrigger
count.value++
```

---

## Vue Reactivity with ref and watchEffect

Illustrates Vue's reactivity system using `ref` to create reactive variables and `watchEffect` to automatically update `A2` when `A0` or `A1` changes. This showcases a basic reactive effect in Vue.

Source: https://github.com/vuejs/docs/blob/main/src/guide/extras/reactivity-in-depth.md#_snippet_6

```javascript
import { ref, watchEffect } from 'vue'

const A0 = ref(0)
const A1 = ref(1)
const A2 = ref()

watchEffect(() => {
  // tracks A0 and A1
  A2.value = A0.value + A1.value
})

// triggers the effect
A0.value = 2
```

---

## JavaScript whenDepsChange Function for Reactive Effect

Shows the `whenDepsChange()` function that wraps the `update` function and sets the `activeEffect` before running the update, enabling dependency tracking. This creates a reactive effect that automatically re-runs when its dependencies change.

Source: https://github.com/vuejs/docs/blob/main/src/guide/extras/reactivity-in-depth.md#_snippet_5

```javascript
function whenDepsChange(update) {
  const effect = () => {
    activeEffect = effect
    update()
    activeEffect = null
  }
  effect()
}
```

---

## Integrating Immer with Vue (JavaScript)

This JavaScript code provides a composable function `useImmer` that integrates Immer with Vue. It uses a shallow ref to hold the immutable state and the `produce` function from Immer to update the state immutably. This composable returns the state and an update function.

Source: https://github.com/vuejs/docs/blob/main/src/guide/extras/reactivity-in-depth.md#_snippet_14

```javascript
import { produce } from 'immer'
import { shallowRef } from 'vue'

export function useImmer(baseState) {
  const state = shallowRef(baseState)
  const update = (updater) => {
    state.value = produce(state.value, updater)
  }

  return [state, update]
}
```

---

## Creating Angular-style Signals in Vue

This code snippet demonstrates how to create Angular-style signals in Vue using `shallowRef`. It exports a `signal` function that returns a function which acts as a getter and also has `set` and `update` methods for modifying the reactive value.

Source: https://github.com/vuejs/docs/blob/main/src/guide/extras/reactivity-in-depth.md#_snippet_17

```JavaScript
import { shallowRef } from 'vue'

export function signal(initialValue) {
  const r = shallowRef(initialValue)
  const s = () => r.value
  s.set = (value) => {
    r.value = value
  }
  s.update = (updater) => {
    r.value = updater(r.value)
  }
  return s
}
```

---

## Creating Solid-style Signals in Vue

This code snippet demonstrates how to create Solid-style signals in Vue using `shallowRef` and `triggerRef`. It exports a `createSignal` function that returns a getter and a setter for a reactive value. The setter includes an option to disable equality checks and trigger updates manually.

Source: https://github.com/vuejs/docs/blob/main/src/guide/extras/reactivity-in-depth.md#_snippet_16

```JavaScript
import { shallowRef, triggerRef } from 'vue'

export function createSignal(value, options) {
  const r = shallowRef(value)
  const get = () => r.value
  const set = (v) => {
    r.value = typeof v === 'function' ? v(r.value) : v
    if (options?.equals === false) triggerRef(r)
  }
  return [get, set]
}
```

---

## Debugger Event Type (TypeScript)

This TypeScript code defines the structure of the `DebuggerEvent` object passed to the component debugging hooks. It includes information about the reactive effect, target object, operation type (track or trigger), key, and related values.

Source: https://github.com/vuejs/docs/blob/main/src/guide/extras/reactivity-in-depth.md#_snippet_11

```typescript
type DebuggerEvent = {
  effect: ReactiveEffect
  target: object
  type:
    | TrackOpTypes /* 'get' | 'has' | 'iterate' */
    | TriggerOpTypes /* 'set' | 'add' | 'delete' | 'clear' */
  key: any
  newValue?: any
  oldValue?: any
  oldTarget?: Map<any, any> | Set<any>
}
```

