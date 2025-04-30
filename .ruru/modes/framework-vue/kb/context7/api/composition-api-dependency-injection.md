# Vue.js Composition API: Dependency Injection

## Provide value with provide() in Vue.js

Demonstrates how to provide values using the `provide()` function in Vue.js Composition API. It shows providing static values, reactive values, and values with Symbol keys within a `<script setup>` block.

Source: https://github.com/vuejs/docs/blob/main/src/api/composition-api-dependency-injection.md#_snippet_0

```vue
<script setup>
import { ref, provide } from 'vue'
import { countSymbol } from './injectionSymbols'

// provide static value
provide('path', '/project/')

// provide reactive value
const count = ref(0)
provide('count', count)

// provide with Symbol keys
provide(countSymbol, count)
</script>
```

---

## Inject values with inject() in Vue.js

Illustrates how to inject provided values using the `inject()` function in Vue.js Composition API. It demonstrates injecting static values, reactive values, values with Symbol keys, values with default values, and values with default value factories within a `<script setup>` block.

Source: https://github.com/vuejs/docs/blob/main/src/api/composition-api-dependency-injection.md#_snippet_1

```vue
<script setup>
import { inject } from 'vue'
import { countSymbol } from './injectionSymbols'

// inject static value without default
const path = inject('path')

// inject reactive value
const count = inject('count')

// inject with Symbol keys
const count2 = inject(countSymbol)

// inject with default value
const bar = inject('path', '/default-path')

// inject with function default value
const fn = inject('function', () => {})

// inject with default value factory
const baz = inject('factory', () => new ExpensiveObject(), true)
</script>
```

---

## Type signature for provide() in TypeScript

Shows the TypeScript type signature for the `provide()` function in Vue.js Composition API. It takes a key (string or InjectionKey<T>) and a value of type T as arguments and returns void.

Source: https://github.com/vuejs/docs/blob/main/src/api/composition-api-dependency-injection.md#_snippet_2

```typescript
function provide<T>(key: InjectionKey<T> | string, value: T): void
```

