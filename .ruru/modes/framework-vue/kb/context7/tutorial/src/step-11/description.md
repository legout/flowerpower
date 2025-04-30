# Vue.js Component Usage and Registration

## Importing Child Component (Composition API)

This snippet demonstrates how to import a child component in a Vue.js application using the Composition API. It assumes the component is defined in a Single-File Component (SFC) named ChildComp.vue. This is a necessary step before the component can be used in the template of the parent component.

Source: https://github.com/vuejs/docs/blob/main/src/tutorial/src/step-11/description.md#_snippet_0

```JavaScript
import ChildComp from './ChildComp.vue'
```

---

## Using Child Component in Template (SFC)

This snippet shows how to use a registered child component within the template of a parent component in a Vue.js SFC. The child component is rendered using its tag name.  It requires the child component to be previously imported and registered in the parent component.

Source: https://github.com/vuejs/docs/blob/main/src/tutorial/src/step-11/description.md#_snippet_2

```HTML
<ChildComp />
```

