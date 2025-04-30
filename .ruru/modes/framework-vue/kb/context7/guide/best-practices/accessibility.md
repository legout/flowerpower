# Vue.js Accessibility Guide

## Vue.js Form with aria-labelledby

This Vue.js code demonstrates using aria-labelledby to associate instructions with an input field.  The aria-labelledby attribute allows linking multiple IDs to provide comprehensive context and instructions for the input, enhancing accessibility.

Source: https://github.com/vuejs/docs/blob/main/src/guide/best-practices/accessibility.md#_snippet_12

```vue-html
<fieldset>
  <legend>Using aria-labelledby</legend>
  <label id="date-label" for="date">Current Date: </label>
  <input
    type="date"
    name="date"
    id="date"
    aria-labelledby="date-label date-instructions"
  />
  <p id="date-instructions">MM/DD/YYYY</p>
</fieldset>
```

---

## Using `aria-describedby` for Input Description

This code demonstrates how to use the `aria-describedby` attribute to provide a description for an input field. The `aria-describedby` attribute references the `id` of another element (usually a paragraph) to use its content as the description of the input field. This description provides additional information or instructions to the user.

Source: https://github.com/vuejs/docs/blob/main/src/guide/best-practices/accessibility.md#_snippet_9

```HTML
<form
  class="demo"
  action="/dataCollectionLocation"
  method="post"
  autocomplete="on"
>
  <h1 id="billing">Billing</h1>
  <div class="form-item">
    <label for="name">Full Name: </label>
    <input
      type="text"
      name="name"
      id="name"
      v-model="name"
      aria-labelledby="billing name"
      aria-describedby="nameDescription"
    />
    <p id="nameDescription">Please provide first and last name.</p>
  </div>
  <button type="submit">Submit</button>
</form>
```

---

## Semantic HTML Form Example

This code shows a basic HTML form structure using semantic elements. It leverages a `v-for` loop to dynamically generate form items based on the `formItems` data.  It also includes autocomplete functionality and a submit button.

Source: https://github.com/vuejs/docs/blob/main/src/guide/best-practices/accessibility.md#_snippet_5

```HTML
<form action="/dataCollectionLocation" method="post" autocomplete="on">
  <div v-for="item in formItems" :key="item.id" class="form-item">
    <label :for="item.id">{{ item.label }}: </label>
    <input
      :type="item.type"
      :id="item.id"
      :name="item.id"
      v-model="item.value"
    />
  </div>
  <button type="submit">Submit</button>
</form>
```

---

## Setting Focus After Route Change (Composition API)

This Vue.js Composition API snippet watches the route path and sets focus to the `backToTop` ref after each route change. It imports `ref`, `watch`, and `useRoute` from Vue and Vue Router. It defines a reactive reference for `backToTop` and utilizes the `watch` function to monitor the route path, calling `focus()` on the referenced element whenever the path changes.

Source: https://github.com/vuejs/docs/blob/main/src/guide/best-practices/accessibility.md#_snippet_3

```Vue
<script setup>
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const backToTop = ref()

watch(
  () => route.path,
  () => {
    backToTop.value.focus()
  }
)
</script>
```

---

## Adding a Skip Link in Vue

This code snippet adds a skip link to the top of the `App.vue` component, allowing users to skip repeated content and navigate directly to the main content area.  It includes HTML for the skip link and an anchor, along with a ref for managing focus.  The skip link is initially hidden and appears when focused.

Source: https://github.com/vuejs/docs/blob/main/src/guide/best-practices/accessibility.md#_snippet_0

```HTML
<span ref="backToTop" tabindex="-1" />
<ul class="skip-links">
  <li>
    <a href="#main" ref="skipLink" class="skip-link">Skip to main content</a>
  </li>
</ul>
```

---

## Vue.js Form with Accessible Placeholders

This code demonstrates a Vue.js form utilizing placeholders. It's crucial to ensure sufficient color contrast for placeholders to meet accessibility standards.  If the contrast is poor, it could be confused for pre-populated data.  This example shows how to set the color explicitly.

Source: https://github.com/vuejs/docs/blob/main/src/guide/best-practices/accessibility.md#_snippet_10

```vue-html
<form
  class="demo"
  action="/dataCollectionLocation"
  method="post"
  autocomplete="on"
>
  <div v-for="item in formItems" :key="item.id" class="form-item">
    <label :for="item.id">{{ item.label }}: </label>
    <input
      type="text"
      :id="item.id"
      :name="item.id"
      v-model="item.value"
      :placeholder="item.placeholder"
    />
  </div>
  <button type="submit">Submit</button>
</form>
```

---

## Setting Focus After Route Change (Options API)

This Vue.js Options API snippet watches the `$route` and sets focus to the `backToTop` ref after each route change.  It uses the `watch` property to detect route changes and then calls the `focus()` method on the referenced element, ensuring the user's focus is reset to the beginning of the page after navigation.

Source: https://github.com/vuejs/docs/blob/main/src/guide/best-practices/accessibility.md#_snippet_2

```Vue
<script>
export default {
  watch: {
    $route() {
      this.$refs.backToTop.focus()
    }
  }
}
</script>
```

---

## Semantic HTML Structure with Headings

This HTML snippet demonstrates the correct usage of headings within a semantic HTML structure. It includes `main`, `section`, and heading elements (`h1`, `h2`, `h3`) with appropriate ARIA attributes for accessibility.  The snippet illustrates how to nest headings correctly and use `aria-labelledby` for associating section titles with the heading elements.

Source: https://github.com/vuejs/docs/blob/main/src/guide/best-practices/accessibility.md#_snippet_4

```HTML
<main role="main" aria-labelledby="main-title">
  <h1 id="main-title">Main title</h1>
  <section aria-labelledby="section-title-1">
    <h2 id="section-title-1"> Section Title </h2>
    <h3>Section Subtitle</h3>
    <!-- Content -->
  </section>
  <section aria-labelledby="section-title-2">
    <h2 id="section-title-2"> Section Title </h2>
    <h3>Section Subtitle</h3>
    <!-- Content -->
    <h3>Section Subtitle</h3>
    <!-- Content -->
  </section>
</main>
```

---

## Vue.js Form with aria-describedby

This Vue.js code demonstrates using aria-describedby to associate instructions with an input field. The aria-describedby attribute provides additional information or instructions related to the input, improving accessibility.

Source: https://github.com/vuejs/docs/blob/main/src/guide/best-practices/accessibility.md#_snippet_13

```vue-html
<fieldset>
  <legend>Using aria-describedby</legend>
  <label id="dob" for="dob">Date of Birth: </label>
  <input type="date" name="dob" id="dob" aria-describedby="dob-instructions" />
  <p id="dob-instructions">MM/DD/YYYY</p>
</fieldset>
```

---

## Vue.js Form with Visually Hidden Label

This Vue.js code shows how to visually hide a label while maintaining accessibility using CSS classes.  This is appropriate when the input's purpose is clear from the surrounding context, like a search button.

Source: https://github.com/vuejs/docs/blob/main/src/guide/best-practices/accessibility.md#_snippet_14

```vue-html
<form role="search">
  <label for="search" class="hidden-visually">Search: </label>
  <input type="text" name="search" id="search" v-model="search" />
  <button type="submit">Search</button>
</form>
```

---

## CSS for Visually Hiding Elements

This CSS snippet provides a class that visually hides elements while keeping them accessible to assistive technologies. This technique is useful for labels or other content that is not needed visually but provides context for screen readers.

Source: https://github.com/vuejs/docs/blob/main/src/guide/best-practices/accessibility.md#_snippet_15

```css
.hidden-visually {
  position: absolute;
  overflow: hidden;
  white-space: nowrap;
  margin: 0;
  padding: 0;
  height: 1px;
  width: 1px;
  clip: rect(0 0 0 0);
  clip-path: inset(100%);
}
```

---

## Vue.js ARIA Hidden Example

This Vue.js code demonstrates the usage of `aria-hidden="true"` to hide an element from assistive technologies like screen readers. This is useful for decorative or duplicated content that doesn't need to be read aloud.

Source: https://github.com/vuejs/docs/blob/main/src/guide/best-practices/accessibility.md#_snippet_16

```vue-html
<p>This is not hidden from screen readers.</p>
<p aria-hidden="true">This is hidden from screen readers.</p>
```

