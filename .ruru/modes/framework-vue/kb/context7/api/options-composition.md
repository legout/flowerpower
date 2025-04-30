# Vue.js Component Options: Composition

## Mixins Option: Basic Usage (Vue.js)

Demonstrates how to use the `mixins` option to include shared logic in a Vue.js component. Mixins can contain component options such as lifecycle hooks, which are merged with the component's own options.

Source: https://github.com/vuejs/docs/blob/main/src/api/options-composition.md#_snippet_8

```javascript
const mixin = {
  created() {
    console.log(1)
  }
}

createApp({
  created() {
    console.log(2)
  },
  mixins: [mixin]
})

// => 1
// => 2
```

---

## Inject Option: Renaming Injection (Vue.js)

Shows how to inject a property with a different name using the `from` property in the `inject` option in Vue.js.  This allows you to map an injected property to a different local property name.

Source: https://github.com/vuejs/docs/blob/main/src/api/options-composition.md#_snippet_6

```javascript
const Child = {
  inject: {
    foo: {
      from: 'bar',
      default: 'foo'
    }
  }
}
```

---

## Inject Option: Data Entry (Vue.js)

Shows how to use an injected value as a data entry in a Vue.js component. This allows a component to initialize its data with values provided by ancestor components.

Source: https://github.com/vuejs/docs/blob/main/src/api/options-composition.md#_snippet_4

```javascript
const Child = {
  inject: ['foo'],
  data() {
    return {
      bar: this.foo
    }
  }
}
```

---

## Extends Option: Composition API Usage (Vue.js)

Shows how to use `extends` with Composition API by calling the base component's setup function within the extending component's setup function, and then merging the returned objects.

Source: https://github.com/vuejs/docs/blob/main/src/api/options-composition.md#_snippet_10

```javascript
import Base from './Base.js'
export default {
  extends: Base,
  setup(props, ctx) {
    return {
      ...Base.setup(props, ctx),
      // local bindings
    }
  }
}
```

---

## Provide Option: Basic Usage (Vue.js)

Demonstrates the basic usage of the `provide` option in Vue.js to provide values that can be injected by descendant components. It uses both a string key and a Symbol key for providing values.

Source: https://github.com/vuejs/docs/blob/main/src/api/options-composition.md#_snippet_0

```javascript
const s = Symbol()

export default {
  provide: {
    foo: 'foo',
    [s]: 'bar'
  }
}
```

---

## Inject Option: Optional Injection (Vue.js)

Demonstrates how to make an injected dependency optional by providing a default value using the object syntax for the `inject` option in Vue.js.

Source: https://github.com/vuejs/docs/blob/main/src/api/options-composition.md#_snippet_5

```javascript
const Child = {
  inject: {
    foo: { default: 'foo' }
  }
}
```

---

## Inject Option: Factory Function for Defaults (Vue.js)

Illustrates the usage of a factory function for non-primitive default values when using the `inject` option in Vue.js. This avoids value sharing between multiple component instances, which is important for objects and arrays.

Source: https://github.com/vuejs/docs/blob/main/src/api/options-composition.md#_snippet_7

```javascript
const Child = {
  inject: {
    foo: {
      from: 'bar',
      default: () => [1, 2, 3]
    }
  }
}
```

