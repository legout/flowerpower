# Vue.js Testing Guide

## Unit Test for Vue Composable (useCounter)

This snippet shows how to unit test a composable function like `useCounter`. It imports the composable, invokes it, and then asserts that the state and methods behave as expected. It leverages Vitest's `expect` function.

Source: https://github.com/vuejs/docs/blob/main/src/guide/scaling-up/testing.md#_snippet_14

```javascript
// counter.test.js
import { useCounter } from './counter.js'

test('useCounter', () => {
  const { count, increment } = useCounter()
  expect(count.value).toBe(0)

  increment()
  expect(count.value).toBe(1)
})
```

---

## Example Vue Composable (useCounter)

This defines a simple composable function `useCounter` in Vue that manages a counter state and provides an increment function. It uses Vue's reactivity API.

Source: https://github.com/vuejs/docs/blob/main/src/guide/scaling-up/testing.md#_snippet_13

```javascript
// counter.js
import { ref } from 'vue'

export function useCounter() {
  const count = ref(0)
  const increment = () => count.value++

  return {
    count,
    increment
  }
}
```

---

## Configure Vitest in Vite Configuration

This code snippet shows how to configure Vitest within the Vite configuration file (vite.config.js). It enables global test APIs and sets up happy-dom as the DOM simulation environment for testing.

Source: https://github.com/vuejs/docs/blob/main/src/guide/scaling-up/testing.md#_snippet_8

```javascript
// vite.config.js
import { defineConfig } from 'vite'

export default defineConfig({
  // ...
  test: {
    // enable jest-like global test APIs
    globals: true,
    // simulate DOM with happy-dom
    // (requires installing happy-dom as a peer dependency)
    environment: 'happy-dom'
  }
})
```

---

## Add Vitest Globals to TypeScript Configuration

This configures TypeScript to include vitest globals by adding `vitest/globals` to the `types` array in `tsconfig.json`. This allows you to use Vitest's test APIs without explicit imports.

Source: https://github.com/vuejs/docs/blob/main/src/guide/scaling-up/testing.md#_snippet_9

```json
{
  "compilerOptions": {
    "types": ["vitest/globals"]
  }
}
```

---

## Unit Testing Increment Function with Vitest

This Vitest code tests the `increment` function to ensure it behaves as expected. It includes tests to verify that the function increments the current number by 1, does not increment it over the maximum, and uses the default maximum of 10. It imports the `increment` function from `./helpers.js`.

Source: https://github.com/vuejs/docs/blob/main/src/guide/scaling-up/testing.md#_snippet_1

```js
// helpers.spec.js
import { increment } from './helpers'

describe('increment', () => {
  test('increments the current number by 1', () => {
    expect(increment(0, 10)).toBe(1)
  })

  test('does not increment the current number over the max', () => {
    expect(increment(10, 10)).toBe(10)
  })

  test('has a default max of 10', () => {
    expect(increment(10)).toBe(10)
  })
})
```

---

## Testing Stepper Component with Vue Test Utils

This snippet demonstrates testing a Stepper component using Vue Test Utils. It mounts the component with a `max` prop, checks the initial value, triggers a click on the increment button, and asserts the updated value. This example tests the component's behavior based on user interactions and prop input.

Source: https://github.com/vuejs/docs/blob/main/src/guide/scaling-up/testing.md#_snippet_4

```JavaScript
const valueSelector = '[data-testid=stepper-value]'
const buttonSelector = '[data-testid=increment]'

const wrapper = mount(Stepper, {
  props: {
    max: 1
  }
})

expect(wrapper.find(valueSelector).text()).toContain('0')

await wrapper.find(buttonSelector).trigger('click')

expect(wrapper.find(valueSelector).text()).toContain('1')
```

---

## Testing Vue Composables with Lifecycle Hooks and Provide/Inject

This example demonstrates how to test a Vue composable that relies on lifecycle hooks or Provide / Inject, using the `withSetup` helper.  It mocks the provide and triggers the unmount hook if needed.

Source: https://github.com/vuejs/docs/blob/main/src/guide/scaling-up/testing.md#_snippet_16

```javascript
import { withSetup } from './test-utils'
import { useFoo } from './foo'

test('useFoo', () => {
  const [result, app] = withSetup(() => useFoo(123))
  // mock provide for testing injections
  app.provide(...)
  // run assertions
  expect(result.foo.value).toBe(1)
  // trigger onUnmounted hook if needed
  app.unmount()
})
```

---

## Example Vue Component Test with Vitest

This snippet demonstrates a basic unit test for a Vue component using Vitest and @testing-library/vue. It renders the component, passes props, and asserts that the expected output is displayed.

Source: https://github.com/vuejs/docs/blob/main/src/guide/scaling-up/testing.md#_snippet_10

```javascript
// MyComponent.test.js
import { render } from '@testing-library/vue'
import MyComponent from './MyComponent.vue'

test('it should work', () => {
  const { getByText } = render(MyComponent, {
    props: {
      /* ... */
    }
  })

  // assert output
  getByText('...')
})
```

---

## Testing Stepper Component with Testing Library

This snippet demonstrates testing a Stepper component using Testing Library. It renders the component, retrieves the initial value, clicks the increment button, and asserts the updated value. Testing Library emphasizes testing components as a user would, focusing on DOM elements and user interactions.

Source: https://github.com/vuejs/docs/blob/main/src/guide/scaling-up/testing.md#_snippet_6

```JavaScript
const { getByText } = render(Stepper, {
  props: {
    max: 1
  }
})

getByText('0') // Implicit assertion that "0" is within the component

const button = getByRole('button', { name: /increment/i })

// Dispatch a click event to our increment button.
await fireEvent.click(button)

getByText('1')

await fireEvent.click(button)
```

---

## Add Test Script to Package.json

This code snippet adds a test script to the `package.json` file, allowing you to run Vitest tests using the command `npm test`.

Source: https://github.com/vuejs/docs/blob/main/src/guide/scaling-up/testing.md#_snippet_11

```json
{
  // ...
  "scripts": {
    "test": "vitest"
  }
}
```

