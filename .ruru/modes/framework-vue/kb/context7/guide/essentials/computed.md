# Vue.js Computed Properties

## Computed Property Definition (Options API)

This snippet demonstrates defining a computed property called `publishedBooksMessage` within the Options API. The computed property's getter function checks if the `author.books` array has any books and returns 'Yes' or 'No' accordingly. The `this` keyword refers to the component instance, allowing access to the component's data.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/computed.md#_snippet_3

```javascript
export default {
  data() {
    return {
      author: {
        name: 'John Doe',
        books: [
          'Vue 2 - Advanced Guide',
          'Vue 3 - Basic Guide',
          'Vue 4 - The Mystery'
        ]
      }
    }
  },
  computed: {
    // a computed getter
    publishedBooksMessage() {
      // `this` points to the component instance
      return this.author.books.length > 0 ? 'Yes' : 'No'
    }
  }
}
```

---

## Initializing Author Data (Composition API)

This snippet initializes author data using the Composition API with `reactive`. It imports `reactive` from 'vue' and creates a reactive object called `author` containing the author's name and books array. The `reactive` function makes the object's properties reactive, meaning changes to these properties will trigger updates in the component.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/computed.md#_snippet_1

```javascript
const author = reactive({
  name: 'John Doe',
  books: [
    'Vue 2 - Advanced Guide',
    'Vue 3 - Basic Guide',
    'Vue 4 - The Mystery'
  ]
})
```

---

## Writable Computed Property (Composition API)

This snippet defines a writable computed property `fullName` using the Composition API.  It imports `ref` and `computed`, creates reactive refs for `firstName` and `lastName`, and then defines the `fullName` computed property with a `get` and `set`. The getter combines the first and last names, and the setter splits the new value to update the individual refs. Destructuring assignment is used.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/computed.md#_snippet_12

```vue
<script setup>
import { ref, computed } from 'vue'

const firstName = ref('John')
const lastName = ref('Doe')

const fullName = computed({
  // getter
  get() {
    return firstName.value + ' ' + lastName.value
  },
  // setter
  set(newValue) {
    // Note: we are using destructuring assignment syntax here.
    [firstName.value, lastName.value] = newValue.split(' ')
  }
})
</script>
```

---

## Template with Computed Property

This code shows how to use a computed property within a Vue.js template.  It displays the value of the `publishedBooksMessage` computed property within a `<span>` element. Vue automatically updates the display whenever the computed property's dependencies change.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/computed.md#_snippet_4

```vue-html
<p>Has published books:</p>
<span>{{ publishedBooksMessage }}</span>
```

---

## Computed Property Definition (Composition API)

This snippet demonstrates defining a computed property using the Composition API in Vue.js. It imports `reactive` and `computed` from Vue, creates a reactive `author` object, and then defines a computed property `publishedBooksMessage` that returns 'Yes' if the author has books, and 'No' otherwise.  The computed property is automatically updated whenever `author.books` changes.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/computed.md#_snippet_5

```vue
<script setup>
import { reactive, computed } from 'vue'

const author = reactive({
  name: 'John Doe',
  books: [
    'Vue 2 - Advanced Guide',
    'Vue 3 - Basic Guide',
    'Vue 4 - The Mystery'
  ]
})

// a computed ref
const publishedBooksMessage = computed(() => {
  return author.books.length > 0 ? 'Yes' : 'No'
})
</script>

<template>
  <p>Has published books:</p>
  <span>{{ publishedBooksMessage }}</span>
</template>
```

---

## Writable Computed Property (Options API)

This code shows how to define a writable computed property `fullName` using the Options API. It includes both a `get` and a `set` function. The `get` function returns the concatenation of `firstName` and `lastName`, while the `set` function splits the new value and updates `firstName` and `lastName` accordingly.  Destructuring assignment is used in the setter.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/computed.md#_snippet_11

```javascript
export default {
  data() {
    return {
      firstName: 'John',
      lastName: 'Doe'
    }
  },
  computed: {
    fullName: {
      // getter
      get() {
        return this.firstName + ' ' + this.lastName
      },
      // setter
      set(newValue) {
        // Note: we are using destructuring assignment syntax here.
        [this.firstName, this.lastName] = newValue.split(' ')
      }
    }
  }
}
```

---

## Writable Computed Property with Previous Value (Composition API)

This code snippet shows a writable computed property where the getter accesses the previous value, and the setter updates the state. It is implemented using the Composition API in Vue.js. The getter returns the current count if it's less than or equal to 3, otherwise it returns the previous value.  The setter updates the count ref by multiplying the new value by 2.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/computed.md#_snippet_16

```vue
<script setup>
import { ref, computed } from 'vue'

const count = ref(2)

const alwaysSmall = computed({
  get(previous) {
    if (count.value <= 3) {
      return count.value
    }

    return previous
  },
  set(newValue) {
    count.value = newValue * 2
  }
})
</script>
```

---

## Initializing Author Data (Options API)

This code snippet initializes the author data with a name and an array of books using the Options API in Vue.js.  It defines the `data` property within the component's configuration object, returning an object that includes the author's name and a list of books.  This is used as the initial state for the component.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/computed.md#_snippet_0

```javascript
export default {
  data() {
    return {
      author: {
        name: 'John Doe',
        books: [
          'Vue 2 - Advanced Guide',
          'Vue 3 - Basic Guide',
          'Vue 4 - The Mystery'
        ]
      }
    }
  }
}
```

---

## Writable Computed Property with Previous Value (Options API)

This code snippet demonstrates a writable computed property where the getter accesses the previous value and the setter updates the state. It's implemented using the Options API in Vue.js.  The getter returns the current count if it's less than or equal to 3, otherwise it returns the previous value. The setter updates the count by multiplying the new value by 2.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/computed.md#_snippet_15

```javascript
export default {
  data() {
    return {
      count: 2
    }
  },
  computed: {
    alwaysSmall: {
      get(previous) {
        if (this.count <= 3) {
          return this.count
        }

        return previous;
      },
      set(newValue) {
        this.count = newValue * 2
      }
    }
  }
}
```

---

## Accessing Previous Value in Computed Property (Composition API)

This code snippet demonstrates how to access the previous value of a computed property using Vue.js Composition API.  The computed function receives the previous value as its first argument.  It returns the current count if it's less than or equal to 3, otherwise, it returns the previous value.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/computed.md#_snippet_14

```vue
<script setup>
import { ref, computed } from 'vue'

const count = ref(2)

// This computed will return the value of count when it's less or equal to 3.
// When count is >=4, the last value that fulfilled our condition will be returned
// instead until count is less or equal to 3
const alwaysSmall = computed((previous) => {
  if (count.value <= 3) {
    return count.value
  }

  return previous
})
</script>
```

---

## Accessing Previous Value in Computed Property (Options API)

This code snippet demonstrates how to access the previous value of a computed property's getter function in Vue.js Options API. The first argument of the getter provides the previous value. It returns the current count if it's less than or equal to 3, otherwise, it returns the previous value.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/computed.md#_snippet_13

```javascript
export default {
  data() {
    return {
      count: 2
    }
  },
  computed: {
    // This computed will return the value of count when it's less or equal to 3.
    // When count is >=4, the last value that fulfilled our condition will be returned
    // instead until count is less or equal to 3
    alwaysSmall(_, previous) {
      if (this.count <= 3) {
        return this.count
      }

      return previous
    }
  }
}
```

---

## Method Invocation in Template

This snippet shows how to invoke a method directly within a Vue.js template.  The template calls the `calculateBooksMessage()` method, and the returned value is displayed.  This approach is similar to using a computed property but does not provide caching.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/computed.md#_snippet_6

```vue-html
<p>{{ calculateBooksMessage() }}</p>
```

