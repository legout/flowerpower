# Vue.js Reactivity API Utilities Documentation

## Converting Reactive Object to Refs in Vue.js (toRefs)

The `toRefs` function converts a reactive object to a plain object where each property is a ref pointing to the corresponding property of the original reactive object. This enables destructuring without losing reactivity.

Source: https://github.com/vuejs/docs/blob/main/src/api/reactivity-utilities.md#_snippet_4

```typescript
function toRefs<T extends object>(
  object: T
): {
  [K in keyof T]: ToRef<T[K]>
}

type ToRef = T extends Ref ? T : Ref<T>
```

```javascript
const state = reactive({
  foo: 1,
  bar: 2
})

const stateAsRefs = toRefs(state)
/*
Type of stateAsRefs: {
  foo: Ref<number>,
  bar: Ref<number>
}
*/

// The ref and the original property is "linked"
state.foo++
console.log(stateAsRefs.foo.value) // 2

stateAsRefs.foo.value++
console.log(state.foo) // 3
```

```javascript
function useFeatureX() {
  const state = reactive({
    foo: 1,
    bar: 2
  })

  // ...logic operating on state

  // convert to refs when returning
  return toRefs(state)
}

// can destructure without losing reactivity
const { foo, bar } = useFeatureX()
```

---

## Creating a Ref from Value/Getter/Reactive Prop in Vue.js (toRef)

The `toRef` function creates a ref from a value, getter, or reactive object property. In the case of an object property, the created ref is synced with the original property, enabling two-way data binding.

Source: https://github.com/vuejs/docs/blob/main/src/api/reactivity-utilities.md#_snippet_2

```typescript
// normalization signature (3.3+)
function toRef<T>(
  value: T
): T extends () => infer R
  ? Readonly<Ref<R>>
  : T extends Ref
  ? T
  : Ref<UnwrapRef<T>>

// object property signature
function toRef<T extends object, K extends keyof T>(
  object: T,
  key: K,
  defaultValue?: T[K]
): ToRef<T[K]>

type ToRef<T> = T extends Ref ? T : Ref<T>
```

```javascript
// returns existing refs as-is
toRef(existingRef)

// creates a readonly ref that calls the getter on .value access
toRef(() => props.foo)

// creates normal refs from non-function values
// equivalent to ref(1)
toRef(1)
```

```javascript
const state = reactive({
  foo: 1,
  bar: 2
})

// a two-way ref that syncs with the original property
const fooRef = toRef(state, 'foo')

// mutating the ref updates the original
fooRef.value++
console.log(state.foo) // 2

// mutating the original also updates the ref
state.foo++
console.log(fooRef.value) // 3
```

```javascript
const fooRef = ref(state.foo)
```

```vue
<script setup>
import { toRef } from 'vue'

const props = defineProps(/* ... */)

// convert `props.foo` into a ref, then pass into
// a composable
useSomeFeature(toRef(props, 'foo'))

// getter syntax - recommended in 3.3+
useSomeFeature(toRef(() => props.foo))
</script>
```

---

## Unwrapping a Ref Value in Vue.js (unref)

The `unref` function returns the inner value of a ref, or the value itself if it's not a ref. It's a utility to simplify accessing the underlying value, ensuring that you are working with a plain value regardless of whether it's wrapped in a ref.

Source: https://github.com/vuejs/docs/blob/main/src/api/reactivity-utilities.md#_snippet_1

```typescript
function unref<T>(ref: T | Ref<T>): T
```

```typescript
function useFoo(x: number | Ref<number>) {
  const unwrapped = unref(x)
  // unwrapped is guaranteed to be number now
}
```

---

## Normalizing to Values from Refs/Getters in Vue.js (toValue)

The `toValue` function normalizes a source into a plain value. If the source is a ref, it returns the inner value. If the source is a getter function, it invokes and returns the result.

Source: https://github.com/vuejs/docs/blob/main/src/api/reactivity-utilities.md#_snippet_3

```typescript
function toValue<T>(source: T | Ref<T> | (() => T)): T
```

```javascript
toValue(1) //       --> 1
toValue(ref(1)) //  --> 1
toValue(() => 1) // --> 1
```

```typescript
import type { MaybeRefOrGetter } from 'vue'

function useFeature(id: MaybeRefOrGetter<number>) {
  watch(() => toValue(id), id => {
    // react to id changes
  })
}

// this composable supports any of the following:
useFeature(1)
useFeature(ref(1))
useFeature(() => 1)
```

---

## Checking if Object is Readonly in Vue.js (isReadonly)

The `isReadonly` function checks if a given value is a readonly object, including proxies created by `readonly()` and `shallowReadonly()`, as well as computed refs without a setter.

Source: https://github.com/vuejs/docs/blob/main/src/api/reactivity-utilities.md#_snippet_7

```typescript
function isReadonly(value: unknown): boolean
```

---

## Checking if Object is Reactive in Vue.js (isReactive)

The `isReactive` function checks if a given value is a proxy created by `reactive()` or `shallowReactive()`.

Source: https://github.com/vuejs/docs/blob/main/src/api/reactivity-utilities.md#_snippet_6

```typescript
function isReactive(value: unknown): boolean
```

