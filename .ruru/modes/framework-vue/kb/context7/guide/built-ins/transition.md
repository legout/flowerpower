# Vue.js Transition Component

## Creating a Reusable Transition Component in Vue

This snippet demonstrates how to create a reusable transition component in Vue by wrapping the built-in `<Transition>` component. It passes down the slot content, allowing the reusable component to transition any content passed to it.  The example highlights the importance of avoiding `<style scoped>` for styling the slot content.

Source: https://github.com/vuejs/docs/blob/main/src/guide/built-ins/transition.md#_snippet_19

```vue
<!-- MyTransition.vue -->
<script>
// JavaScript hooks logic...
</script>

<template>
  <!-- wrap the built-in Transition component -->
  <Transition
    name="my-transition"
    @enter="onEnter"
    @leave="onLeave">
    <slot></slot> <!-- pass down slot content -->
  </Transition>
</template>

<style>
/*
  Necessary CSS...
  Note: avoid using <style scoped> here since it
  does not apply to slot content.
*/
</style>
```

---

## Transition Hooks in Composition API JavaScript

This snippet showcases how to implement JavaScript transition hooks within Vue's Composition API. Each function corresponds to a specific stage in the transition lifecycle, such as before the element is inserted, during the animation, and after the animation has completed.  The `done` callback is crucial for JavaScript-only transitions to signal the end of the animation.

Source: https://github.com/vuejs/docs/blob/main/src/guide/built-ins/transition.md#_snippet_16

```javascript
// called before the element is inserted into the DOM.
// use this to set the "enter-from" state of the element
function onBeforeEnter(el) {}

// called one frame after the element is inserted.
// use this to start the entering animation.
function onEnter(el, done) {
  // call the done callback to indicate transition end
  // optional if used in combination with CSS
  done()
}

// called when the enter transition has finished.
function onAfterEnter(el) {}

// called when the enter transition is cancelled before completion.
function onEnterCancelled(el) {}

// called before the leave hook.
// Most of the time, you should just use the leave hook
function onBeforeLeave(el) {}

// called when the leave transition starts.
// use this to start the leaving animation.
function onLeave(el, done) {
  // call the done callback to indicate transition end
  // optional if used in combination with CSS
  done()
}

// called when the leave transition has finished and the
// element has been removed from the DOM.
function onAfterLeave(el) {}

// only available with v-show transitions
function onLeaveCancelled(el) {}
```

---

## Transition with Key Attribute - Options API - Vue

This snippet demonstrates how to force a transition by using the `key` attribute on a span element inside the `<Transition>` component. The `count` data property is incremented every second, causing the span to re-render with a different key and triggering the transition. This example uses Vue 2/3's Options API.

Source: https://github.com/vuejs/docs/blob/main/src/guide/built-ins/transition.md#_snippet_26

```vue
<script>
export default {
  data() {
    return {
      count: 1,
      interval: null 
    }
  },
  mounted() {
    this.interval = setInterval(() => {
      this.count++;
    }, 1000)
  },
  beforeDestroy() {
    clearInterval(this.interval)
  }
}
</script>

<template>
  <Transition>
    <span :key="count">{{ count }}</span>
  </Transition>
</template>
```

---

## Basic Transition Example Vue HTML

A basic example demonstrating the use of the `<Transition>` component with `v-if` to toggle the visibility of a paragraph element. When the `show` data property changes, the transition is triggered.

Source: https://github.com/vuejs/docs/blob/main/src/guide/built-ins/transition.md#_snippet_0

```vue-html
<button @click="show = !show">Toggle</button>
<Transition>
  <p v-if="show">hello</p>
</Transition>
```

---

## Transition with Key Attribute - Composition API - Vue

This snippet demonstrates how to force a transition by using the `key` attribute on a span element inside the `<Transition>` component.  The `count` ref is incremented every second, causing the span to re-render with a different key and triggering the transition. This uses Vue 3's Composition API.

Source: https://github.com/vuejs/docs/blob/main/src/guide/built-ins/transition.md#_snippet_25

```vue
<script setup>
import { ref } from 'vue';
const count = ref(0);

setInterval(() => count.value++, 1000);
</script>

<template>
  <Transition>
    <span :key="count">{{ count }}</span>
  </Transition>
</template>
```

---

## Transition Between Elements in Vue HTML

This snippet shows how to transition between two elements using `v-if` / `v-else` / `v-else-if` directives within a `<Transition>` component. The key is ensuring that only one element is visible at any given time to enable smooth transitions between them.

Source: https://github.com/vuejs/docs/blob/main/src/guide/built-ins/transition.md#_snippet_21

```vue-html
<Transition>
  <button v-if="docState === 'saved'">Edit</button>
  <button v-else-if="docState === 'edited'">Save</button>
  <button v-else-if="docState === 'editing'">Cancel</button>
</Transition>
```

---

## Advanced Transition Vue HTML

A more advanced example of using the `<Transition>` component with a named transition. This example toggles the visibility of a paragraph using `v-if` and applies a slide-fade animation.

Source: https://github.com/vuejs/docs/blob/main/src/guide/built-ins/transition.md#_snippet_4

```vue-html
<Transition name="slide-fade">
  <p v-if="show">hello</p>
</Transition>
```

---

## Vue Transition for Nested Elements in HTML

This Vue.js transition component wraps a nested structure.  The transition classes will be applied to the outer div, but the CSS rules target the inner element for animation.

Source: https://github.com/vuejs/docs/blob/main/src/guide/built-ins/transition.md#_snippet_10

```vue-html
<Transition name="nested">
  <div v-if="show" class="outer">
    <div class="inner">
      Hello
    </div>
  </div>
</Transition>
```

---

## Vue Transition with Custom CSS Classes in HTML

This example demonstrates the use of custom CSS classes for transitions using the `enter-active-class` and `leave-active-class` props. It assumes that Animate.css is included and uses its animation classes.

Source: https://github.com/vuejs/docs/blob/main/src/guide/built-ins/transition.md#_snippet_8

```vue-html
<!-- assuming Animate.css is included on the page -->
<Transition
  name="custom-classes"
  enter-active-class="animate__animated animate__tada"
  leave-active-class="animate__animated animate__bounceOutRight"
>
  <p v-if="show">hello</p>
</Transition>
```

---

## Dynamic Transition Name - Vue HTML

This code shows how to dynamically set the `name` prop of the `<Transition>` component. This allows you to use different CSS transitions based on the current state. `transitionName` is a variable in the Vue component's data or state that determines which CSS transition to apply.

Source: https://github.com/vuejs/docs/blob/main/src/guide/built-ins/transition.md#_snippet_24

```html
<Transition :name="transitionName">
  <!-- ... -->
</Transition>
```

---

## Transition Modes in Vue HTML

This snippet demonstrates how to use the `mode` prop on the `<Transition>` component to control the timing of entering and leaving animations. Setting `mode="out-in"` ensures that the leaving element is animated out before the entering element is animated in, preventing layout issues and creating a cleaner transition.

Source: https://github.com/vuejs/docs/blob/main/src/guide/built-ins/transition.md#_snippet_22

```vue-html
<Transition mode="out-in">
  ...
</Transition>
```

---

## Applying Transition on Appear in Vue HTML

This snippet shows how to apply a transition on the initial render of a node by adding the `appear` prop to the `<Transition>` component. This is useful for animating elements as they initially appear on the page.

Source: https://github.com/vuejs/docs/blob/main/src/guide/built-ins/transition.md#_snippet_20

```vue-html
<Transition appear>
  ...
</Transition>
```

---

## Basic Transition CSS

CSS styles for a basic fade transition. Defines the active and to/from states using `opacity` and `transition` properties. The `v-enter-active` and `v-leave-active` classes specify the duration and easing for the transition.

Source: https://github.com/vuejs/docs/blob/main/src/guide/built-ins/transition.md#_snippet_1

```css
/* we will explain what these classes do next! */
.v-enter-active,
.v-leave-active {
  transition: opacity 0.5s ease;
}

.v-enter-from,
.v-leave-to {
  opacity: 0;
}
```

---

## Vue Transition Component with CSS Animations in HTML

This Vue.js component wraps a paragraph element with a v-if directive within a <Transition> component.  The `show` data property controls the visibility of the paragraph, triggering the transition when it changes. This example uses the default transition class naming convention.

Source: https://github.com/vuejs/docs/blob/main/src/guide/built-ins/transition.md#_snippet_6

```vue-html
<Transition name="bounce">
  <p v-if="show" style="text-align: center;">
    Hello here is some bouncy text!
  </p>
</Transition>
```

---

## Transition Between Dynamic Components - Vue HTML

This snippet demonstrates how to use the `<Transition>` component to animate transitions between dynamic components in Vue. The `mode="out-in"` ensures that the exiting component is fully transitioned out before the entering component is transitioned in.  The `activeComponent` prop determines which component is rendered.

Source: https://github.com/vuejs/docs/blob/main/src/guide/built-ins/transition.md#_snippet_23

```html
<Transition name="fade" mode="out-in">
  <component :is="activeComponent"></component>
</Transition>
```

---

## CSS Animation Definitions

This CSS defines the animation applied to the element during the enter and leave transitions.  It uses the `animation` property to apply a keyframe animation named `bounce-in` with a duration of 0.5 seconds. The `reverse` keyword is used for the leave animation to play the animation in reverse.

Source: https://github.com/vuejs/docs/blob/main/src/guide/built-ins/transition.md#_snippet_7

```css
.bounce-enter-active {
  animation: bounce-in 0.5s;
}
.bounce-leave-active {
  animation: bounce-in 0.5s reverse;
}
@keyframes bounce-in {
  0% {
    transform: scale(0);
  }
  50% {
    transform: scale(1.25);
  }
  100% {
    transform: scale(1);
  }
}
```

