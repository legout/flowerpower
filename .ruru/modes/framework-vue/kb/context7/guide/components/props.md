# Vue.js Component Props Declaration and Usage

## Defining Boolean Prop (Options API)

This snippet demonstrates how to define a boolean prop named 'disabled' using the Options API in Vue.js.  When the 'disabled' attribute is present on the component, it's equivalent to passing `:disabled="true"`. When it's absent, it's equivalent to `:disabled="false"`.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/props.md#_snippet_25

```javascript
export default {
  props: {
    disabled: Boolean
  }
}
```

---

## Nullable Type Prop (Options API)

This snippet demonstrates how to define a prop that is required but can also accept a null value using Options API. The `id` prop is defined to be either a string or null, and it is marked as required.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/props.md#_snippet_23

```javascript
export default {
  props: {
    id: {
      type: [String, null],
      required: true
    }
  }
}
```

---

## Prop Validation (Options API)

This snippet demonstrates prop validation using the `props` option in Options API. It showcases specifying different types, required props, default values, and custom validators for props.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/props.md#_snippet_19

```javascript
export default {
  props: {
    // Basic type check
    //  (`null` and `undefined` values will allow any type)
    propA: Number,
    // Multiple possible types
    propB: [String, Number],
    // Required string
    propC: {
      type: String,
      required: true
    },
    // Required but nullable string
    propD: {
      type: [String, null],
      required: true
    },
    // Number with a default value
    propE: {
      type: Number,
      default: 100
    },
    // Object with a default value
    propF: {
      type: Object,
      // Object or array defaults must be returned from
      // a factory function. The function receives the raw
      // props received by the component as the argument.
      default(rawProps) {
        return { message: 'hello' }
      }
    },
    // Custom validator function
    // full props passed as 2nd argument in 3.4+
    propG: {
      validator(value, props) {
        // The value must match one of these strings
        return ['success', 'warning', 'danger'].includes(value)
      }
    },
    // Function with a default value
    propH: {
      type: Function,
      // Unlike object or array default, this is not a factory
      // function - this is a function to serve as a default value
      default() {
        return 'Default function'
      }
    }
  }
}
```

---

## Declaring Props with Type Validation (Options API)

This snippet illustrates how to declare props with type validation in a Vue component using the Options API. The component defines 'title' as a String type and 'likes' as a Number type. This provides runtime warnings in the console if incorrect types are passed as props.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/props.md#_snippet_3

```javascript
export default {
  props: {
    title: String,
    likes: Number
  }
}
```

---

## Declaring Props with the `props` option (Composition API)

This JavaScript snippet shows how to declare props using the `props` option in a Vue component when not using `<script setup>`. The component defines a 'foo' prop and logs its value within the `setup` function. The `setup` function receives the props as its first argument.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/props.md#_snippet_1

```javascript
export default {
  props: ['foo'],
  setup(props) {
    // setup() receives props as the first argument.
    console.log(props.foo)
  }
}
```

---

## Reactive Props Destructure Example with watchEffect

This example showcases reactive props destructuring in Vue 3.5+ within `<script setup>`. The `watchEffect` automatically re-runs when the destructured 'foo' prop changes due to compiler transformation. This snippet requires Vue 3.5 or higher for the reactive destructuring to work as expected.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/props.md#_snippet_6

```javascript
const props = defineProps(['foo'])

watchEffect(() => {
  // `foo` transformed to `props.foo` by the compiler
  console.log(props.foo)
})
```

---

## Using Boolean Prop in Template

This snippet shows how to use the boolean prop 'disabled' in a Vue.js template. The presence of the `disabled` attribute is interpreted as `true`, while its absence is interpreted as `false`.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/props.md#_snippet_26

```vue-html
<!-- equivalent of passing :disabled="true" -->
<MyComponent disabled />

<!-- equivalent of passing :disabled="false" -->
<MyComponent />
```

---

## Declaring Props with Type Validation (Composition API)

This snippet demonstrates how to declare props with type validation in a Vue component using the Composition API with `defineProps`. The component defines 'title' as a String type and 'likes' as a Number type.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/props.md#_snippet_4

```javascript
// in <script setup>
defineProps({
  title: String,
  likes: Number
})

```

```javascript
// in non-<script setup>
export default {
  props: {
    title: String,
    likes: Number
  }
}

```

---

## Prop Name Casing in props option (Options API)

Example of prop name casing using props options in Options API. The 'greetingMessage' is declared as a camelCase prop.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/props.md#_snippet_9

```javascript
export default {
  props: {
    greetingMessage: String
  }
}
```

---

## Using Prop as Initial Data (Composition API)

This snippet shows how to use a prop as the initial value for a local data property using Composition API. The `initialCounter` prop is used to initialize the `counter` ref, disconnecting it from future prop updates.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/props.md#_snippet_14

```javascript
const props = defineProps(['initialCounter'])

// counter only uses props.initialCounter as the initial value;
// it is disconnected from future prop updates.
const counter = ref(props.initialCounter)
```

---

## Prop Validation (Composition API)

This snippet demonstrates prop validation using the `defineProps` macro in Composition API. It shows how to specify different types, required props, default values, and custom validators for props.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/props.md#_snippet_18

```javascript
defineProps({
  // Basic type check
  //  (`null` and `undefined` values will allow any type)
  propA: Number,
  // Multiple possible types
  propB: [String, Number],
  // Required string
  propC: {
    type: String,
    required: true
  },
  // Required but nullable string
  propD: {
    type: [String, null],
    required: true
  },
  // Number with a default value
  propE: {
    type: Number,
    default: 100
  },
  // Object with a default value
  propF: {
    type: Object,
    // Object or array defaults must be returned from
    // a factory function. The function receives the raw
    // props received by the component as the argument.
    default(rawProps) {
      return { message: 'hello' }
    }
  },
  // Custom validator function
  // full props passed as 2nd argument in 3.4+
  propG: {
    validator(value, props) {
      // The value must match one of these strings
      return ['success', 'warning', 'danger'].includes(value)
    }
  },
  // Function with a default value
  propH: {
    type: Function,
    // Unlike object or array default, this is not a factory
    // function - this is a function to serve as a default value
    default() {
      return 'Default function'
    }
  }
})
```

---

## Defining Boolean Prop (Composition API)

This snippet demonstrates how to define a boolean prop named 'disabled' using the Composition API in Vue.js. When the 'disabled' attribute is present on the component, it's equivalent to passing `:disabled="true"`. When it's absent, it's equivalent to `:disabled="false"`.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/props.md#_snippet_24

```javascript
defineProps({
  disabled: Boolean
})
```

---

## Transforming Prop with Computed Property (Composition API)

This snippet shows how to transform a prop's value using a computed property in Composition API. The `size` prop is trimmed and converted to lowercase, and the `normalizedSize` computed property automatically updates when the `size` prop changes.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/props.md#_snippet_16

```javascript
const props = defineProps(['size'])

// computed property that auto-updates when the prop changes
const normalizedSize = computed(() => props.size.trim().toLowerCase())
```

---

## Reactive Props Destructure with Default Value

This example showcases reactive props destructuring and using default values with type based props declaration. If the `foo` prop is not provided it will default to 'hello'.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/props.md#_snippet_7

```typescript
const {{ foo = 'hello' }} = defineProps<{ foo?: string }>()
```

---

## Declaring Props with defineProps in Vue SFCs

This snippet demonstrates how to declare props in a Vue Single-File Component (SFC) using the `defineProps()` macro within `<script setup>`. It defines a prop named 'foo' and logs its value to the console. The component expects to receive a prop called 'foo'.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/props.md#_snippet_0

```vue
<script setup>
const props = defineProps(['foo'])

console.log(props.foo)
</script>
```

---

## Using Custom Class as Prop Type (Composition API)

This snippet demonstrates how to use a custom class `Person` as the type for a prop named `author` within Composition API. Vue will validate whether the prop's value is an instance of the class.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/props.md#_snippet_20

```javascript
defineProps({
  author: Person
})
```

---

## Post Object Example (Composition API)

Illustrates how to define the post object with 'id' and 'title' properties using composition API.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/props.md#_snippet_11

```javascript
const post = {
  id: 1,
  title: 'My Journey with Vue'
}
```

---

## Multiple Type Boolean Prop (Composition API)

This snippet demonstrates how Vue.js casts boolean props when multiple types are allowed using the Composition API. Boolean casting takes precedence unless String appears before Boolean in the type array. When String is defined first, boolean casting rule does not apply and an empty string will be passed if the attribute is present.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/props.md#_snippet_27

```javascript
// disabled will be casted to true
defineProps({
  disabled: [Boolean, Number]
})

// disabled will be casted to true
defineProps({
  disabled: [Boolean, String]
})

// disabled will be casted to true
defineProps({
  disabled: [Number, Boolean]
})

// disabled will be parsed as an empty string (disabled="")
defineProps({
  disabled: [String, Boolean]
})
```

---

## Multiple Type Boolean Prop (Options API)

This snippet demonstrates how Vue.js casts boolean props when multiple types are allowed using the Options API. Boolean casting takes precedence unless String appears before Boolean in the type array. When String is defined first, boolean casting rule does not apply and an empty string will be passed if the attribute is present.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/props.md#_snippet_28

```javascript
// disabled will be casted to true
export default {
  props: {
    disabled: [Boolean, Number]
  }
}

// disabled will be casted to true
export default {
  props: {
    disabled: [Boolean, String]
  }
}

// disabled will be casted to true
export default {
  props: {
    disabled: [Number, Boolean]
  }
}

// disabled will be parsed as an empty string (disabled="")
export default {
  props: {
    disabled: [String, Boolean]
  }
}
```

---

## Nullable Type Prop (Composition API)

This snippet demonstrates how to define a prop that is required but can also accept a null value using Composition API. The `id` prop is defined to be either a string or null, and it is marked as required.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/props.md#_snippet_22

```javascript
defineProps({
  id: {
    type: [String, null],
    required: true
  }
})
```

---

## Using Prop as Initial Data (Options API)

This snippet demonstrates how to use a prop as the initial value for a local data property using Options API. The `initialCounter` prop is used to initialize the `counter` data property, disconnecting it from future prop updates.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/props.md#_snippet_15

```javascript
export default {
  props: ['initialCounter'],
  data() {
    return {
      // counter only uses this.initialCounter as the initial value;
      // it is disconnected from future prop updates.
      counter: this.initialCounter
    }
  }
}
```

---

## Declaring Props with the `props` option (Options API)

This snippet showcases how to declare props using the `props` option in a Vue component (Options API). The component defines a 'foo' prop and logs its value within the `created` lifecycle hook. Props are accessible via `this` keyword within the component instance.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/props.md#_snippet_2

```javascript
export default {
  props: ['foo'],
  created() {
    // props are exposed on `this`
    console.log(this.foo)
  }
}
```

---

## Transforming Prop with Computed Property (Options API)

This snippet demonstrates how to transform a prop's value using a computed property in Options API. The `size` prop is trimmed and converted to lowercase, and the `normalizedSize` computed property automatically updates when the `size` prop changes.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/props.md#_snippet_17

```javascript
export default {
  props: ['size'],
  computed: {
    // computed property that auto-updates when the prop changes
    normalizedSize() {
      return this.size.trim().toLowerCase()
    }
  }
}
```

---

## Declaring Props using Type Annotations in Vue SFCs with TypeScript

This snippet demonstrates declaring props using type annotations within `<script setup lang="ts">` in a Vue SFC. It defines optional props 'title' (string) and 'likes' (number) using TypeScript syntax. This enables type checking and IDE support for the component's props.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/props.md#_snippet_5

```vue
<script setup lang="ts">
defineProps<{{
  title?: string
  likes?: number
}}>()
</script>
```

---

## Prop Name Casing in defineProps (Composition API)

Example of prop name casing using defineProps in Composition API. The 'greetingMessage' is declared as a camelCase prop.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/props.md#_snippet_8

```javascript
defineProps({
  greetingMessage: String
})
```

---

## Data Option Example (Options API)

Illustrates how to define the data option containing post object with 'id' and 'title' properties.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/props.md#_snippet_10

```javascript
export default {
  data() {
    return {
      post: {
        id: 1,
        title: 'My Journey with Vue'
      }
    }
  }
}
```

---

## Mutating Prop (Options API)

This snippet demonstrates the incorrect way to attempt mutating a prop directly within a component using Options API. The attempt to reassign the value of the prop `foo` within the `created` lifecycle hook will trigger a warning from Vue.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/props.md#_snippet_13

```javascript
export default {
  props: ['foo'],
  created() {
    // ❌ warning, props are readonly!
    this.foo = 'bar'
  }
}
```

