# Vue.js TransitionGroup Component

## JavaScript Hooks for Staggered Transitions with GSAP

This JavaScript snippet uses the GSAP library to animate the enter transition of list items with a delay based on their index. The `onEnter` function is called when an item is entering the list, and the GSAP `to` method is used to animate the item's opacity and height.

Source: https://github.com/vuejs/docs/blob/main/src/guide/built-ins/transition-group.md#_snippet_4

```javascript
function onEnter(el, done) {
  gsap.to(el, {
    opacity: 1,
    height: '1.6em',
    delay: el.dataset.index * 0.15,
    onComplete: done
  })
}
```

---

## Basic TransitionGroup Usage in Vue.js

This snippet demonstrates how to use the `<TransitionGroup>` component in Vue.js to apply enter/leave transitions to a `v-for` list. It specifies the name and tag attributes for basic styling.

Source: https://github.com/vuejs/docs/blob/main/src/guide/built-ins/transition-group.md#_snippet_0

```vue-html
<TransitionGroup name="list" tag="ul">
  <li v-for="item in items" :key="item">
    {{ item }}
  </li>
</TransitionGroup>
```

---

## Staggering List Transitions with Data Attributes

This snippet shows how to add a `data-index` attribute to each list item, which is used later in JavaScript to stagger the animations. The `css` prop is set to `false` to disable CSS transitions, and event listeners for `before-enter`, `enter`, and `leave` are added.

Source: https://github.com/vuejs/docs/blob/main/src/guide/built-ins/transition-group.md#_snippet_3

```vue-html
<TransitionGroup
  tag="ul"
  :css="false"
  @before-enter="onBeforeEnter"
  @enter="onEnter"
  @leave="onLeave"
>
  <li
    v-for="(item, index) in computedList"
    :key="item.msg"
    :data-index="index"
  >
    {{ item.msg }}
  </li>
</TransitionGroup>
```

---

## CSS Transitions for Move Animations in Lists

This CSS snippet extends the previous example to include move transitions, making the list items move smoothly when their order changes. It also addresses layout issues by positioning leaving items absolutely.

Source: https://github.com/vuejs/docs/blob/main/src/guide/built-ins/transition-group.md#_snippet_2

```css
.list-move, /* apply transition to moving elements */
.list-enter-active,
.list-leave-active {
  transition: all 0.5s ease;
}

.list-enter-from,
.list-leave-to {
  opacity: 0;
  transform: translateX(30px);
}

/* ensure leaving items are taken out of layout flow so that moving
   animations can be calculated correctly. */
.list-leave-active {
  position: absolute;
}
```

