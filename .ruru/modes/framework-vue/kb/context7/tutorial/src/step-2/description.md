# Vue.js Declarative Rendering

## Component setup with reactive and ref in Vue.js

This code snippet shows how to set up a Vue component using the `setup()` function. It declares reactive state with `reactive()` and `ref()`, and returns them as properties to be used in the template.

Source: https://github.com/vuejs/docs/blob/main/src/tutorial/src/step-2/description.md#_snippet_2

```javascript
setup() {
  const counter = reactive({ count: 0 })
  const message = ref('Hello World!')
  return {
    counter,
    message
  }
}
```

---

## Rendering Dynamic Text in Vue.js Template

This snippet demonstrates how to render dynamic text in a Vue.js template using mustache syntax. It displays the value of the `message` property from the component's data option.

Source: https://github.com/vuejs/docs/blob/main/src/tutorial/src/step-2/description.md#_snippet_7

```vue-html
<h1>{{ message }}</h1>
```

---

## Rendering Dynamic Text in Vue.js Template

This snippet demonstrates how to render dynamic text in a Vue.js template using mustache syntax. It displays the value of the `message` ref and the `counter.count` property.

Source: https://github.com/vuejs/docs/blob/main/src/tutorial/src/step-2/description.md#_snippet_3

```vue-html
<h1>{{ message }}</h1>
<p>Count is: {{ counter.count }}</p>
```

