# Vue Rendering Mechanism Documentation

## Template with v-if Directive - HTML

This HTML snippet demonstrates how the `v-if` directive creates a new block node. The outer `div` is the root block, and the `div` with the `v-if` directive creates a child block. This nested structure allows Vue to efficiently update the DOM when the condition of the `v-if` directive changes.

Source: https://github.com/vuejs/docs/blob/main/src/guide/extras/rendering-mechanism.md#_snippet_7

```HTML
<div> <!-- root block -->
  <div>
    <div v-if> <!-- if block -->
      ...
    </div>
  </div>
</div>
```

---

## Vue HTML Template Example with Static Caching

This Vue HTML template demonstrates static caching. The `foo` and `bar` divs are static content which are cached by the compiler and reused in subsequent re-renders. The dynamic content is bound to the `dynamic` property.

Source: https://github.com/vuejs/docs/blob/main/src/guide/extras/rendering-mechanism.md#_snippet_3

```HTML
<div>
  <div>foo</div> <!-- cached -->
  <div>bar</div> <!-- cached -->
  <div>{{ dynamic }}</div>
</div>
```

---

## Render Function with createElementBlock - JavaScript

This JavaScript snippet shows a render function that returns a virtual DOM tree. It uses `_openBlock()` and `_createElementBlock()` to create a fragment. The `_createElementBlock` function takes a `_Fragment` (which is likely a reference to Vue's Fragment component), null attributes, an array of children (empty in this case), and a flag `64 /* STABLE_FRAGMENT */` indicating that the fragment's children are stable.

Source: https://github.com/vuejs/docs/blob/main/src/guide/extras/rendering-mechanism.md#_snippet_5

```JavaScript
export function render() {
  return (_openBlock(), _createElementBlock(_Fragment, null, [
    /* children */
  ], 64 /* STABLE_FRAGMENT */))
}
```

---

## Template with Tracked and Untracked Elements - HTML

This HTML snippet illustrates which elements within a Vue template are tracked for dynamic updates based on their attributes and content. Elements with dynamic bindings (like `:id` and `{{ bar }}`) are tracked, while static elements are not. The outermost `div` represents the root block.

Source: https://github.com/vuejs/docs/blob/main/src/guide/extras/rendering-mechanism.md#_snippet_6

```HTML
<div> <!-- root block -->
  <div>...</div>         <!-- not tracked -->
  <div :id="id"></div>   <!-- tracked -->
  <div>                  <!-- not tracked -->
    <div>{{ bar }}</div> <!-- tracked -->
  </div>
</div>
```

---

## createElementVNode Usage in JavaScript

This JavaScript code snippet showcases how `createElementVNode` is used with patch flags to optimize DOM updates. The third argument, `2`, is the CLASS patch flag which tells the runtime renderer only the class needs to be updated during patching. The code assumes the existence of `_normalizeClass` and `_ctx.active` for generating the class value.

Source: https://github.com/vuejs/docs/blob/main/src/guide/extras/rendering-mechanism.md#_snippet_1

```JavaScript
createElementVNode("div", {
  class: _normalizeClass({ active: _ctx.active })
}, null, 2 /* CLASS */)
```

