# Vue.js Component Slots

## Using a Component with Slots Vue.js

This code snippet demonstrates how to use the `<FancyButton>` component, passing "Click me!" as slot content. The content is rendered within the `<slot>` element defined in the `<FancyButton>` component's template.  The slot content is rendered where the `<slot>` element is placed.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/slots.md#_snippet_1

```vue-html
<FancyButton>
  Click me! <!-- slot content -->
</FancyButton>
```

---

## BaseLayout Template with Named Slots (Vue)

This example demonstrates a BaseLayout component with named slots for the header, main content, and footer. The `name` attribute on the `<slot>` element defines the slot's name, allowing the parent component to target specific sections of the layout.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/slots.md#_snippet_10

```vue-html
<div class="container">
  <header>
    <slot name="header"></slot>
  </header>
  <main>
    <slot></slot>
  </main>
  <footer>
    <slot name="footer"></slot>
  </footer>
</div>
```

---

## Passing Content to Named Slots (Vue)

This snippet shows how to pass content to named slots in a parent component using the `<template v-slot:header>` syntax (or the shorthand `<template #header>`). Each `<template>` targets a specific slot in the `BaseLayout` component.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/slots.md#_snippet_11

```vue-html
<BaseLayout>
  <template #header>
    <h1>Here might be a page title</h1>
  </template>

  <template #default>
    <p>A paragraph for the main content.</p>
    <p>And another one.</p>
  </template>

  <template #footer>
    <p>Here's some contact info</p>
  </template>
</BaseLayout>
```

---

## Passing Complex Slot Content Vue.js

This code snippet demonstrates passing more complex slot content to the `<FancyButton>` component, including a `<span>` element with inline styling and an `AwesomeIcon` component.  The parent can provide arbitrary template code as slot content.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/slots.md#_snippet_4

```vue-html
<FancyButton>
  <span style="color:red">Click me!</span>
  <AwesomeIcon name="plus" />
</FancyButton>
```

---

## Using a Component with Fallback Content Vue.js

This code snippet shows how to use the `<SubmitButton>` component without providing any slot content. In this case, the fallback content defined in the component will be rendered.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/slots.md#_snippet_6

```vue-html
<SubmitButton />
```

---

## Using Named Scoped Slots in Vue.js

This code demonstrates how to use named scoped slots in a Vue.js component.  It defines three named slots (header, default, and footer) and passes slot props to each.  The v-slot directive is used to access these props within the template.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/slots.md#_snippet_21

```vue-html
<MyComponent>
  <template #header="headerProps">
    {{ headerProps }}
  </template>

  <template #default="defaultProps">
    {{ defaultProps }}
  </template>

  <template #footer="footerProps">
    {{ footerProps }}
  </template>
</MyComponent>
```

---

## Passing Props to Named Scoped Slots in Vue.js

This snippet illustrates how to pass props to a named scoped slot in Vue.js. It uses the <slot> tag with the `name` attribute to specify the slot name and passes the `message` prop. Note that the `name` attribute is reserved and will not be available in the slot props.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/slots.md#_snippet_22

```vue-html
<slot name="header" message="hello"></slot>
```

---

## Using Scoped Slots in FancyList Component

This code demonstrates how to use scoped slots within a `FancyList` component. It utilizes a template with the `#item` shorthand for `v-slot:item` to define the structure for each item in the list. The component exposes `body`, `username`, and `likes` as slot props.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/slots.md#_snippet_26

```vue-html
<FancyList :api-url="url" :per-page="10">
  <template #item="{ body, username, likes }">
    <div class="item">
      <p>{{ body }}</p>
      <p>by {{ username }} | {{ likes }} likes</p>
    </div>
  </template>
</FancyList>
```

---

## Dynamic Slot Names (Vue)

This snippet demonstrates the usage of dynamic slot names using dynamic directive arguments on `v-slot`. The slot name is determined by the `dynamicSlotName` variable, allowing for more flexible slot content rendering.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/slots.md#_snippet_16

```vue-html
<base-layout>
  <template v-slot:[dynamicSlotName]>
    ...
  </template>

  <!-- with shorthand -->
  <template #[dynamicSlotName]>
    ...
  </template>
</base-layout>
```

---

## Receiving Scoped Slot Props (Vue)

This snippet demonstrates how to receive props passed from a child component to a scoped slot. The `v-slot` directive is used on the child component tag, and its value (`slotProps`) contains the props passed from the child.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/slots.md#_snippet_18

```vue-html
<MyComponent v-slot="slotProps">
  {{ slotProps.text }} {{ slotProps.count }}
</MyComponent>
```

---

## Rendered HTML with Named Slots

This is the final rendered HTML output after passing content to the named slots of the BaseLayout component. It demonstrates how the content from the parent component is inserted into the corresponding slots in the child component.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/slots.md#_snippet_13

```html
<div class="container">
  <header>
    <h1>Here might be a page title</h1>
  </header>
  <main>
    <p>A paragraph for the main content.</p>
    <p>And another one.</p>
  </main>
  <footer>
    <p>Here's some contact info</p>
  </footer>
</div>
```

---

## Defining a Component with Slots Vue.js

This code snippet demonstrates how to define a Vue.js component (`FancyButton`) that uses a `<slot>` element as a slot outlet.  The slot outlet indicates where the parent-provided slot content should be rendered within the component's template. The class `fancy-btn` provides custom styling for the button.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/slots.md#_snippet_0

```vue-html
<button class="fancy-btn">
  <slot></slot> <!-- slot outlet -->
</button>
```

---

## Overriding Fallback Content with Slots Vue.js

This code snippet shows how to use the `<SubmitButton>` component and override the fallback content by providing the slot content "Save".

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/slots.md#_snippet_8

```vue-html
<SubmitButton>Save</SubmitButton>
```

---

## Passing Content to Named Slots (Vue) - Implicit Default

This example demonstrates how to pass content to the default slot implicitly by placing non-`<template>` nodes directly within the `BaseLayout` component. The content outside of `<template>` elements will be rendered in the default slot.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/slots.md#_snippet_12

```vue-html
<BaseLayout>
  <template #header>
    <h1>Here might be a page title</h1>
  </template>

  <!-- implicit default slot -->
  <p>A paragraph for the main content.</p>
  <p>And another one.</p>

  <template #footer>
    <p>Here's some contact info</p>
  </template>
</BaseLayout>
```

---

## Card Component with Conditional Slots (Vue)

This example showcases a Card component with conditional rendering of slots using `v-if` and the `$slots` property. If content is provided for a slot (header, default, or footer), the corresponding section within the card is rendered.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/slots.md#_snippet_15

```vue-html
<template>
  <div class="card">
    <div v-if="$slots.header" class="card-header">
      <slot name="header" />
    </div>
    
    <div v-if="$slots.default" class="card-content">
      <slot />
    </div>
    
    <div v-if="$slots.footer" class="card-footer">
      <slot name="footer" />
    </div>
  </div>
</template>
```

---

## Correct Usage of Default Scoped Slot with Template

This example demonstrates the correct way to use the default scoped slot with an explicit `<template>` tag when mixing it with named slots. Using the template tag clarifies the scope of the `message` prop, indicating that it's not available within the named `footer` slot.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/slots.md#_snippet_25

```vue-html
<MyComponent>
  <!-- Use explicit default slot -->
  <template #default="{ message }">
    <p>{{ message }}</p>
  </template>

  <template #footer>
    <p>Here's some contact info</p>
  </template>
</MyComponent>
```

---

## Rendered HTML with Slots Vue.js

This snippet shows the final rendered HTML after using the `<FancyButton>` component with the slot content "Click me!".  The content has been inserted into the location of the slot, and the element has the `fancy-btn` class.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/slots.md#_snippet_2

```html
<button class="fancy-btn">Click me!</button>
```

---

## Destructuring Scoped Slot Props (Vue)

This example demonstrates how to use destructuring in `v-slot` to directly access specific props passed from the child component to the scoped slot.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/slots.md#_snippet_20

```vue-html
<MyComponent v-slot="{ text, count }">
  {{ text }} {{ count }}
</MyComponent>
```

---

## Rendering Scoped Slots in FancyList Component

This code snippet shows how the `FancyList` component renders the scoped slot multiple times for each item in the list. It uses `v-for` to iterate over the `items` array and passes the current item data as slot props to the named slot 'item' using `v-bind`.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/slots.md#_snippet_27

```vue-html
<ul>
  <li v-for="item in items">
    <slot name="item" v-bind="item"></slot>
  </li>
</ul>
```

---

## Passing Props to a Scoped Slot (Vue)

This example shows how to pass data from a child component to a slot using attributes on the `<slot>` element. These attributes become available as props within the slot's scope in the parent component.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/slots.md#_snippet_17

```vue-html
<!-- <MyComponent> template -->
<div>
  <slot :text="greetingMessage" :count="1"></slot>
</div>
```

---

## Defining Fallback Content for Slots Vue.js

This code snippet shows how to define fallback content for a slot in the `<SubmitButton>` component. If the parent component doesn't provide any slot content, the default content "Submit" will be rendered.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/slots.md#_snippet_5

```vue-html
<button type="submit">
  <slot>
    Submit <!-- fallback content -->
  </slot>
</button>
```

---

## JavaScript Analogy for Named Slots

This JavaScript code provides an analogy to explain how named slots work. It simulates passing slot fragments as properties to a `BaseLayout` function, which then renders them in different places within the layout.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/slots.md#_snippet_14

```js
// passing multiple slot fragments with different names
BaseLayout({
  header: `...`,
  default: `...`,
  footer: `...`
})

// <BaseLayout> renders them in different places
function BaseLayout(slots) {
  return `<div class="container">
      <header>${slots.header}</header>
      <main>${slots.default}</main>
      <footer>>${slots.footer}</footer>
    </div>`
}
```

---

## Rendered HTML with Fallback Content Vue.js

This snippet shows the rendered HTML when the `<SubmitButton>` component is used without providing slot content.  The fallback content "Submit" is rendered within the `<button>` element.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/slots.md#_snippet_7

```html
<button type="submit">Submit</button>
```

---

## Rendered HTML with Overridden Slot Content Vue.js

This snippet shows the rendered HTML when the `<SubmitButton>` component's fallback content is overridden by the slot content "Save".  The provided content "Save" is rendered within the `<button>` element.

Source: https://github.com/vuejs/docs/blob/main/src/guide/components/slots.md#_snippet_9

```html
<button type="submit">Save</button>
```

