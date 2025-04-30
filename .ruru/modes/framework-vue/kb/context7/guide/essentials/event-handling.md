# Vue.js Event Handling

## Reactive Count Initialization (Options API)

Defines a reactive data property `count` within a Vue component using the Options API. This property is initialized to 0 and bound to an event handler. The Options API allows defining component logic through the `data` property and other options.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/event-handling.md#_snippet_1

```javascript
data() {
  return {
    count: 0
  }
}
```

---

## Method Handler Definition (Options API)

Defines a `greet` method within a Vue component using the Options API. It accesses the component's `name` data property to construct a greeting message. `this` refers to the current Vue instance. The method also handles the native DOM event object.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/event-handling.md#_snippet_4

```javascript
data() {
  return {
    name: 'Vue.js'
  }
},
methods: {
  greet(event) {
    // `this` inside methods points to the current active instance
    alert(`Hello ${this.name}!`)
    // `event` is the native DOM event
    if (event) {
      alert(event.target.tagName)
    }
  }
}
```

---

## Event Handler Definition (Options API)

Defines a `warn` method within the `methods` object of a Vue component. It receives a `message` and an `event` object, preventing the default behavior if an event object is passed. This showcases how to access and handle the native event object within a method handler using the Options API.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/event-handling.md#_snippet_11

```javascript
methods: {
  warn(message, event) {
    // now we have access to the native event
    if (event) {
      event.preventDefault()
    }
    alert(message)
  }
}
```

---

## Vue.js Key Modifiers Example

Demonstrates how to use key modifiers in Vue.js to listen for specific keyboard events. The `@keyup.enter` modifier ensures that the `submit` method is only called when the Enter key is pressed. Similarly `@keyup.page-down` ensures `onPageDown` is only called when the PageDown key is pressed.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/event-handling.md#_snippet_13

```vue-html
<!-- only call `submit` when the `key` is `Enter` -->
<input @keyup.enter="submit" />
```

```vue-html
<input @keyup.page-down="onPageDown" />
```

---

## Bind Click Event to Method Handler

This snippet demonstrates how to bind a click event to a method handler named `greet` using the `@click` directive in a Vue template. When the button is clicked, the `greet` method defined in the component will be executed. The method name is referenced directly without parentheses.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/event-handling.md#_snippet_5

```vue-html
<!-- `greet` is the name of the method defined above -->
<button @click="greet">Greet</button>
```

---

## Binding Alt + Enter Key Combination in Vue.js

This code snippet demonstrates how to bind a Vue.js method to the `keyup` event of an input element, triggering the method only when the Alt key and Enter key are pressed simultaneously. The `clear` method will be called when the user releases the Enter key while holding down the Alt key.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/event-handling.md#_snippet_14

```vue-html
<!-- Alt + Enter -->
<input @keyup.alt.enter="clear" />
```

---

## Method Definition with Argument (Options API)

Defines a `say` method within the `methods` object of a Vue component using the Options API. It takes a `message` argument and displays it in an alert. This showcases how to pass custom arguments to methods called from inline event handlers.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/event-handling.md#_snippet_7

```javascript
methods: {
  say(message) {
    alert(message)
  }
}
```

---

## Method Handler Definition (Composition API)

Defines a method `greet` using Vue's Composition API.  It accesses a reactive variable `name` to construct a greeting message. It also accesses the native DOM event object. This showcases how to define event handlers as methods within a Vue component using the Composition API.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/event-handling.md#_snippet_3

```javascript
const name = ref('Vue.js')

function greet(event) {
  alert(`Hello ${name.value}!`)
  // `event` is the native DOM event
  if (event) {
    alert(event.target.tagName)
  }
}
```

---

## Calling Method with Argument in Inline Handler

This snippet demonstrates how to call a method with a custom argument from an inline handler in a Vue template.  The `@click` directive is used to bind the click event to the `say` method, passing the string 'hello' or 'bye' as an argument. Each button calls the same method but with a different argument.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/event-handling.md#_snippet_8

```vue-html
<button @click="say('hello')">Say hello</button>
<button @click="say('bye')">Say bye</button>
```

---

## Accessing Event Argument in Inline Handlers

Demonstrates how to access the original DOM event in an inline handler. The first button utilizes the `$event` special variable to pass the event object to the `warn` method.  The second button uses an inline arrow function to achieve the same result. Both approaches provide access to the native event object within the handler.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/event-handling.md#_snippet_9

```vue-html
<!-- using $event special variable -->
<button @click="warn('Form cannot be submitted yet.', $event)">
  Submit
</button>

<!-- using inline arrow function -->
<button @click="(event) => warn('Form cannot be submitted yet.', event)">
  Submit
</button>
```

---

## Vue.js Event Modifiers Example

This snippet illustrates how to use event modifiers in Vue.js templates. Modifiers like `.stop`, `.prevent`, `.self`, `.capture`, `.once`, and `.passive` are appended to the event name to modify event handling behavior. This allows for concise and declarative event handling logic within the template.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/event-handling.md#_snippet_12

```vue-html
<!-- the click event's propagation will be stopped -->
<a @click.stop="doThis"></a>

<!-- the submit event will no longer reload the page -->
<form @submit.prevent="onSubmit"></form>

<!-- modifiers can be chained -->
<a @click.stop.prevent="doThat"></a>

<!-- just the modifier -->
<form @submit.prevent></form>

<!-- only trigger handler if event.target is the element itself -->
<!-- i.e. not from a child element -->
<div @click.self="doThat">...</div>
```

```vue-html
<!-- use capture mode when adding the event listener     -->
<!-- i.e. an event targeting an inner element is handled -->
<!-- here before being handled by that element           -->
<div @click.capture="doThis">...</div>

<!-- the click event will be triggered at most once -->
<a @click.once="doThis"></a>

<!-- the scroll event's default behavior (scrolling) will happen -->
<!-- immediately, instead of waiting for `onScroll` to complete  -->
<!-- in case it contains `event.preventDefault()`                -->
<div @scroll.passive="onScroll">...</div>
```

---

## Reactive Count Initialization (Composition API)

Defines a reactive variable `count` using Vue's Composition API's `ref` function. This variable is initialized to 0 and can be used to track the number of times an event is triggered. This snippet is part of a larger example showcasing event handling with inline handlers.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/event-handling.md#_snippet_0

```javascript
const count = ref(0)
```

---

## Event Handler Definition (Composition API)

Defines a `warn` method that receives both a `message` string and an `event` object. The method prevents the default behavior of the event if an event object is provided, and then displays an alert with the provided message. It uses Vue's Composition API.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/event-handling.md#_snippet_10

```javascript
function warn(message, event) {
  // now we have access to the native event
  if (event) {
    event.preventDefault()
  }
  alert(message)
}
```

---

## Binding Click Event with Ctrl Modifier in Vue.js

This example illustrates binding the `onClick` method to a button's click event when the Ctrl key is pressed (and potentially other modifiers). It also demonstrates binding the `onCtrlClick` method to the click event, but only when the Ctrl key is pressed and no other modifier keys are active, using the `.exact` modifier.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/event-handling.md#_snippet_16

```vue-html
<!-- this will fire even if Alt or Shift is also pressed -->
<button @click.ctrl="onClick">A</button>

<!-- this will only fire when Ctrl and no other keys are pressed -->
<button @click.ctrl.exact="onCtrlClick">A</button>

<!-- this will only fire when no system modifiers are pressed -->
<button @click.exact="onClick">A</button>
```

---

## Increment Count with Inline Handler

This snippet demonstrates how to use an inline handler within a Vue template to increment the `count` variable.  The `@click` directive binds the click event of the button to the inline expression `count++`. The `{{ count }}` syntax displays the current value of the `count` variable.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/event-handling.md#_snippet_2

```vue-html
<button @click="count++">Add 1</button>
<p>Count is: {{ count }}</p>
```

