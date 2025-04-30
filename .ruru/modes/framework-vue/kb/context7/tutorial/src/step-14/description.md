# Vue.js Slots Documentation

## Rendering Slot Content in Child Component (HTML)

This code snippet shows how to define a slot in a child component using standard HTML. The `<slot></slot>` element acts as a placeholder where the parent component's slot content will be rendered.

Source: https://github.com/vuejs/docs/blob/main/src/tutorial/src/step-14/description.md#_snippet_3

```vue-html
<!-- in child template -->
<slot></slot>
```

---

## Defining Slot Content in Parent Component (HTML)

This code snippet demonstrates how to pass slot content from a parent component to a child component using standard HTML. The content between the opening and closing tags of the child component will be rendered in the child's slot.

Source: https://github.com/vuejs/docs/blob/main/src/tutorial/src/step-14/description.md#_snippet_1

```vue-html
<child-comp>
  This is some slot content!
</child-comp>
```

---

## Defining Fallback Content for a Slot

This code snippet demonstrates how to define fallback content for a slot. If the parent component does not provide any slot content, the fallback content within the `<slot>` element will be displayed.

Source: https://github.com/vuejs/docs/blob/main/src/tutorial/src/step-14/description.md#_snippet_4

```vue-html
<slot>Fallback content</slot>
```

---

## Defining Slot Content in Parent Component (SFC)

This code snippet demonstrates how to pass slot content from a parent component to a child component using Vue.js single-file components (SFC). The content between the opening and closing tags of the child component will be rendered in the child's slot.

Source: https://github.com/vuejs/docs/blob/main/src/tutorial/src/step-14/description.md#_snippet_0

```vue-html
<ChildComp>
  This is some slot content!
</ChildComp>
```

