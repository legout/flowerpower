# Vue.js Component Options: State, Props, Computed, and Methods

## Initializing Component Data with Data Function in Vue.js

This code demonstrates how to define the `data` option in a Vue.js component.  The `data` option is a function that returns a plain JavaScript object, which Vue will make reactive.  The returned object becomes accessible via `this.$data` and individual properties are proxied to the component instance (e.g., `this.a`).

Source: https://github.com/vuejs/docs/blob/main/src/api/options-state.md#_snippet_0

```javascript
export default {
  data() {
    return { a: 1 }
  },
  created() {
    console.log(this.a) // 1
    console.log(this.$data) // { a: 1 }
  }
}
```

---

## Defining Props with Validation and Options in Vue.js

This code demonstrates the object-based syntax for declaring props in Vue.js, allowing for type validation, default values, required status, and custom validators. Each prop is defined as a key-value pair, where the key is the prop name, and the value is an object containing options such as `type`, `default`, `required`, and `validator`.

Source: https://github.com/vuejs/docs/blob/main/src/api/options-state.md#_snippet_3

```javascript
export default {
  props: {
    // type check
    height: Number,
    // type check plus other validations
    age: {
      type: Number,
      default: 0,
      required: true,
      validator: (value) => {
        return value >= 0
      }
    }
  }
}
```

---

## Watch Option Usage Example JavaScript

Demonstrates how to use the `watch` option in a Vue.js component to observe changes in data properties, including nested properties and using different callback configurations.

Source: https://github.com/vuejs/docs/blob/main/src/api/options-state.md#_snippet_8

```javascript
export default {
  data() {
    return {
      a: 1,
      b: 2,
      c: {
        d: 4
      },
      e: 5,
      f: 6
    }
  },
  watch: {
    // watching top-level property
    a(val, oldVal) {
      console.log(`new: ${val}, old: ${oldVal}`)
    },
    // string method name
    b: 'someMethod',
    // the callback will be called whenever any of the watched object properties change regardless of their nested depth
    c: {
      handler(val, oldVal) {
        console.log('c changed')
      },
      deep: true
    },
    // watching a single nested property:
    'c.d': function (val, oldVal) {
      // do something
    },
    // the callback will be called immediately after the start of the observation
    e: {
      handler(val, oldVal) {
        console.log('e changed')
      },
      immediate: true
    },
    // you can pass array of callbacks, they will be called one-by-one
    f: [
      'handle1',
      function handle2(val, oldVal) {
        console.log('handle2 triggered')
      },
      {
        handler: function handle3(val, oldVal) {
          console.log('handle3 triggered')
        }
        /* ... */
      }
    ]
  },
  methods: {
    someMethod() {
      console.log('b changed')
    },
    handle1() {
      console.log('handle 1 triggered')
    }
  },
  created() {
    this.a = 3 // => new: 3, old: 1
  }
}
```

---

## Defining Simple Props in Vue.js

This snippet showcases the simple array-based syntax for declaring props in a Vue.js component. In this form, you provide an array of strings, each representing the name of a prop that the component accepts.  No type validation or default values are specified in this simple form.

Source: https://github.com/vuejs/docs/blob/main/src/api/options-state.md#_snippet_2

```javascript
export default {
  props: ['size', 'myMessage']
}
```

---

## Defining Methods in Vue.js

This code shows how to define methods within a Vue.js component using the `methods` option. Methods are functions that can be called from the component instance or within templates.  The `this` context of a method is automatically bound to the component instance.

Source: https://github.com/vuejs/docs/blob/main/src/api/options-state.md#_snippet_6

```javascript
export default {
  data() {
    return { a: 1 }
  },
  methods: {
    plus() {
      this.a++
    }
  },
  created() {
    this.plus()
    console.log(this.a) // => 2
  }
}
```

---

## Expose Option Usage Example JavaScript

Illustrates how to use the `expose` option in Vue.js component to control which methods are accessible to the parent component via template refs.

Source: https://github.com/vuejs/docs/blob/main/src/api/options-state.md#_snippet_13

```javascript
export default {
  // only `publicMethod` will be available on the public instance
  expose: ['publicMethod'],
  methods: {
    publicMethod() {
      // ...
    },
    privateMethod() {
      // ...
    }
  }
}
```

---

## Emits Option Object Syntax Example JavaScript

Shows how to use the `emits` option in Vue.js component with object syntax to define custom events and their corresponding validation functions.

Source: https://github.com/vuejs/docs/blob/main/src/api/options-state.md#_snippet_11

```javascript
export default {
  emits: {
    // no validation
    click: null,

    // with validation
    submit: (payload) => {
      if (payload.email && payload.password) {
        return true
      } else {
        console.warn(`Invalid submit event payload!`)
        return false
      }
    }
  }
}
```

---

## Accessing Component Instance in Data Function with Arrow Function

This example shows how to access the component instance within a `data` function defined using an arrow function. Since arrow functions do not bind `this`, the component instance is passed as the first argument (vm). This pattern is useful when accessing component props within the `data` function.

Source: https://github.com/vuejs/docs/blob/main/src/api/options-state.md#_snippet_1

```javascript
data: (vm) => ({ a: vm.myProp })
```

---

## Defining Readonly Computed Property in Vue.js

This example shows how to define a read-only computed property in a Vue.js component. The computed property `aDouble` returns the value of `this.a` multiplied by 2. Computed properties are cached and only re-evaluated when their dependencies change.

Source: https://github.com/vuejs/docs/blob/main/src/api/options-state.md#_snippet_4

```javascript
export default {
  data() {
    return { a: 1 }
  },
  computed: {
    // readonly
    aDouble() {
      return this.a * 2
    },
    // writable
    aPlus: {
      get() {
        return this.a + 1
      },
      set(v) {
        this.a = v - 1
      }
    }
  },
  created() {
    console.log(this.aDouble) // => 2
    console.log(this.aPlus) // => 2

    this.aPlus = 3
    console.log(this.a) // => 2
    console.log(this.aDouble) // => 4
  }
}
```

---

## Watch Option Interface Definition TypeScript

Defines the TypeScript interface for the `watch` option in Vue.js component options, including different types for watch callbacks and associated options like immediate, deep, and flush.

Source: https://github.com/vuejs/docs/blob/main/src/api/options-state.md#_snippet_7

```typescript
interface ComponentOptions {
  watch?: {
    [key: string]: WatchOptionItem | WatchOptionItem[]
  }
}

type WatchOptionItem = string | WatchCallback | ObjectWatchOptionItem

type WatchCallback<T> = (
  value: T,
  oldValue: T,
  onCleanup: (cleanupFn: () => void) => void
) => void

type ObjectWatchOptionItem = {
  handler: WatchCallback | string
  immediate?: boolean // default: false
  deep?: boolean // default: false
  flush?: 'pre' | 'post' | 'sync' // default: 'pre'
  onTrack?: (event: DebuggerEvent) => void
  onTrigger?: (event: DebuggerEvent) => void
}
```

---

## Emits Option Array Syntax Example JavaScript

Demonstrates how to use the `emits` option in Vue.js component with array syntax to declare custom events.

Source: https://github.com/vuejs/docs/blob/main/src/api/options-state.md#_snippet_10

```javascript
export default {
  emits: ['check'],
  created() {
    this.$emit('check')
  }
}
```

