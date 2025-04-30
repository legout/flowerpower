# Vue.js Animation Techniques

## Animate Number with Watcher (Composition API)

This snippet demonstrates animating a number using a watcher and GSAP (GreenSock Animation Platform) in Vue.js with the Composition API. It watches for changes in the `number` ref and uses GSAP to tween the `tweened.number` reactive property, providing a smooth animation effect.

Source: https://github.com/vuejs/docs/blob/main/src/guide/extras/animation.md#_snippet_8

```javascript
import { ref, reactive, watch } from 'vue'
import gsap from 'gsap'

const number = ref(0)
const tweened = reactive({
  number: 0
})

watch(number, (n) => {
  gsap.to(tweened, { duration: 0.5, number: Number(n) || 0 })
})
```

---

## Toggle CSS Class for Animation (Options API)

This snippet shows how to toggle a CSS class to trigger an animation in Vue.js using the Options API. It uses the `data` property to manage the disabled state and the `methods` property to define the `warnDisabled` function. The disabled state is bound to the `shake` class in the HTML template.

Source: https://github.com/vuejs/docs/blob/main/src/guide/extras/animation.md#_snippet_1

```javascript
export default {
  data() {
    return {
      disabled: false
    }
  },
  methods: {
    warnDisabled() {
      this.disabled = true
      setTimeout(() => {
        this.disabled = false
      }, 1500)
    }
  }
}
```

---

## Input Binding for Number Animation (Vue)

This Vue HTML snippet includes an input field bound to the `number` data property and displays the animated number (`tweened.number`) formatted to zero decimal places.  It utilizes `v-model.number` to ensure input is treated as a number.

Source: https://github.com/vuejs/docs/blob/main/src/guide/extras/animation.md#_snippet_9

```vue-html
Type a number: <input v-model.number="number" />
<p>{{ tweened.number.toFixed(0) }}</p>
```

---

## Dynamic Style Binding (Vue)

This Vue HTML snippet uses event binding (@mousemove) to call the `onMousemove` method and updates the background color of the div based on the `x` value, creating a state-driven animation effect.

Source: https://github.com/vuejs/docs/blob/main/src/guide/extras/animation.md#_snippet_6

```vue-html
<div
  @mousemove="onMousemove"
  :style="{ backgroundColor: `hsl(${x}, 80%, 50%)` }"
  class="movearea"
>
  <p>Move your mouse across this div...</p>
  <p>x: {{ x }}</p>
</div>
```

---

## Apply CSS Class based on Data Binding (Vue)

This Vue HTML snippet applies the 'shake' CSS class based on the `disabled` data property. When `disabled` is true, the `shake` class is added to the div, triggering the CSS animation.

Source: https://github.com/vuejs/docs/blob/main/src/guide/extras/animation.md#_snippet_2

```vue-html
<div :class="{ shake: disabled }">
  <button @click="warnDisabled">Click me</button>
  <span v-if="disabled">This feature is disabled!</span>
</div>
```

---

## Input Binding for Number Animation (Vue, Options API)

This Vue HTML snippet includes an input field bound to the `number` data property and displays the animated number (`tweened`) formatted to zero decimal places.  It utilizes `v-model.number` to ensure input is treated as a number, compatible with the Options API example.

Source: https://github.com/vuejs/docs/blob/main/src/guide/extras/animation.md#_snippet_11

```vue-html
Type a number: <input v-model.number="number" />
<p>{{ tweened.toFixed(0) }}</p>
```

