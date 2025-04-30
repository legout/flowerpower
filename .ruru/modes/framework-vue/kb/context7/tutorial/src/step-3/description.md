# Vue.js Attribute Bindings

## Binding ID Attribute with v-bind

This snippet demonstrates how to bind the `id` attribute of a `div` element to a dynamic value using the `v-bind` directive in Vue.js. The `dynamicId` property from the component's state will be used to update the `id` attribute.

Source: https://github.com/vuejs/docs/blob/main/src/tutorial/src/step-3/description.md#_snippet_0

```vue-html
<div v-bind:id="dynamicId"></div>
```

