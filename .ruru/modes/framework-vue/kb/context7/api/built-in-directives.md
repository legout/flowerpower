# Vue.js Built-in Directives

## v-slot Usage Examples in Vue.js

Illustrates the use of v-slot for defining named slots and scoped slots in Vue.js components.  Examples show how to pass data to slots using props and destructuring. v-slot facilitates flexible content distribution and customization within components.

Source: https://github.com/vuejs/docs/blob/main/src/api/built-in-directives.md#_snippet_7

```vue-html
<!-- Named slots -->
<BaseLayout>
  <template v-slot:header>
    Header content
  </template>

  <template v-slot:default>
    Default slot content
  </template>

  <template v-slot:footer>
    Footer content
  </template>
</BaseLayout>

<!-- Named slot that receives props -->
<InfiniteScroll>
  <template v-slot:item="slotProps">
    <div class="item">
      {{ slotProps.item.text }}
    </div>
  </template>
</InfiniteScroll>

<!-- Default slot that receive props, with destructuring -->
<Mouse v-slot="{ x, y }">
  Mouse position: {{ x }}, {{ y }}
</Mouse>
```

---

## Using v-on Directive for Event Handling in Vue.js

These snippets illustrate various ways to use the `v-on` directive (shorthand `@`) in Vue.js for event handling. It can attach listeners to native DOM events or custom events emitted by child components. The directive supports modifiers for event propagation, default prevention, key filtering, and more. It can also accept an object of event/listener pairs.

Source: https://github.com/vuejs/docs/blob/main/src/api/built-in-directives.md#_snippet_5

```vue-html
<!-- method handler -->
<button v-on:click="doThis"></button>

<!-- dynamic event -->
<button v-on:[event]="doThis"></button>

<!-- inline statement -->
<button v-on:click="doThat('hello', $event)"></button>

<!-- shorthand -->
<button @click="doThis"></button>

<!-- shorthand dynamic event -->
<button @[event]="doThis"></button>

<!-- stop propagation -->
<button @click.stop="doThis"></button>

<!-- prevent default -->
<button @click.prevent="doThis"></button>

<!-- prevent default without expression -->
<form @submit.prevent></form>

<!-- chain modifiers -->
<button @click.stop.prevent="doThis"></button>

<!-- key modifier using keyAlias -->
<input @keyup.enter="onEnter" />

<!-- the click event will be triggered at most once -->
<button v-on:click.once="doThis"></button>

<!-- object syntax -->
<button v-on="{ mousedown: doThis, mouseup: doThat }"></button>
```

```vue-html
<MyComponent @my-event="handleThis" />

<!-- inline statement -->
<MyComponent @my-event="handleThis(123, $event)" />
```

---

## v-bind Attribute Binding in Vue.js

Demonstrates how to use v-bind to dynamically bind HTML attributes to Vue.js expressions. This includes shorthand notations, dynamic attribute names, class and style bindings, and prop binding for components. v-bind allows flexible and reactive attribute manipulation based on component data.

Source: https://github.com/vuejs/docs/blob/main/src/api/built-in-directives.md#_snippet_6

```vue-html
<!-- bind an attribute -->
<img v-bind:src="imageSrc" />

<!-- dynamic attribute name -->
<button v-bind:[key]="value"></button>

<!-- shorthand -->
<img :src="imageSrc" />

<!-- same-name shorthand (3.4+), expands to :src="src" -->
<img :src />

<!-- shorthand dynamic attribute name -->
<button :[key]="value"></button>

<!-- with inline string concatenation -->
<img :src="'/path/to/images/' + fileName" />

<!-- class binding -->
<div :class="{ red: isRed }"></div>
<div :class="[classA, classB]"></div>
<div :class="[classA, { classB: isB, classC: isC }]"></div>

<!-- style binding -->
<div :style="{ fontSize: size + 'px' }"></div>
<div :style="[styleObjectA, styleObjectB]"></div>

<!-- binding an object of attributes -->
<div v-bind="{ id: someProp, 'other-attr': otherProp }"></div>

<!-- prop binding. "prop" must be declared in the child component. -->
<MyComponent :prop="someThing" />

<!-- pass down parent props in common with a child component -->
<MyComponent v-bind="$props" />

<!-- XLink -->
<svg><a :xlink:special="foo"></a></svg>
```

```vue-html
<div :someProperty.prop="someObject"></div>

<!-- equivalent to -->
<div .someProperty="someObject"></div>
```

```vue-html
<svg :view-box.camel="viewBox"></svg>
```

---

## v-cloak Directive Usage in Vue.js

Shows how to use v-cloak to hide un-compiled templates until Vue.js is ready, preventing a flash of unstyled content.  This directive is particularly useful in no-build-step setups. Requires corresponding CSS to initially hide the element.

Source: https://github.com/vuejs/docs/blob/main/src/api/built-in-directives.md#_snippet_11

```css
[v-cloak] {
  display: none;
}
```

```vue-html
<div v-cloak>
  {{ message }}
</div>
```

---

## Using v-else-if Directive with v-if in Vue.js

This snippet shows the usage of the `v-else-if` directive in Vue.js to create conditional chains. The `v-else-if` block is rendered if its condition is truthy and the preceding `v-if` and `v-else-if` conditions are falsy. The previous sibling element must have a `v-if` or `v-else-if` directive.

Source: https://github.com/vuejs/docs/blob/main/src/api/built-in-directives.md#_snippet_3

```vue-html
<div v-if="type === 'A'">
  A
</div>
<div v-else-if="type === 'B'">
  B
</div>
<div v-else-if="type === 'C'">
  C
</div>
<div v-else>
  Not A/B/C
</div>
```

---

## Using v-for Directive for List Rendering in Vue.js

These snippets demonstrate different ways to use the `v-for` directive in Vue.js to render a list of items.  It supports iterating over arrays, objects, numbers, strings and iterables.  You can access the index (or key for objects) in addition to the item itself. The `key` attribute is recommended for efficient updates.

Source: https://github.com/vuejs/docs/blob/main/src/api/built-in-directives.md#_snippet_4

```vue-html
<div v-for="item in items">
  {{ item.text }}
</div>
```

```vue-html
<div v-for="(item, index) in items"></div>
```

```vue-html
<div v-for="(value, key) in object"></div>
```

```vue-html
<div v-for="(value, name, index) in object"></div>
```

```vue-html
<div v-for="item in items" :key="item.id">
  {{ item.text }}
</div>
```

---

## v-once Directive in Vue.js

Demonstrates how v-once renders an element or component only once, skipping future updates. This improves performance by treating the element as static content.  Applies to single elements, elements with children, and components.

Source: https://github.com/vuejs/docs/blob/main/src/api/built-in-directives.md#_snippet_9

```vue-html
<!-- single element -->
<span v-once>This will never change: {{msg}}</span>
<!-- the element have children -->
<div v-once>
  <h1>Comment</h1>
  <p>{{msg}}</p>
</div>
<!-- component -->
<MyComponent v-once :comment="msg"></MyComponent>
<!-- `v-for` directive -->
<ul>
  <li v-for="i in list" v-once>{{i}}</li>
</ul>
```

---

## v-memo Directive in Vue.js

Explains how v-memo memoizes a sub-tree of the template based on a dependency array.  If the values in the array haven't changed since the last render, updates to the sub-tree are skipped, improving performance, especially in large v-for lists.  Correct dependency specification is critical.

Source: https://github.com/vuejs/docs/blob/main/src/api/built-in-directives.md#_snippet_10

```vue-html
<div v-memo="[valueA, valueB]">
  ...
</div>
```

```vue-html
<div v-for="item in list" :key="item.id" v-memo="[item.id === selected]">
  <p>ID: {{ item.id }} - selected: {{ item.id === selected }}</p>
  <p>...more child nodes</p>
</div>
```

---

## Using v-text Directive in Vue.js

This snippet demonstrates the usage of the `v-text` directive in Vue.js to update the text content of an element. It sets the `textContent` property of the element, overwriting any existing content. It's equivalent to using mustache interpolation.

Source: https://github.com/vuejs/docs/blob/main/src/api/built-in-directives.md#_snippet_0

```vue-html
<span v-text="msg"></span>
<!-- same as -->
<span>{{msg}}</span>
```

---

## Using v-else Directive with v-if in Vue.js

This snippet illustrates the usage of the `v-else` directive in conjunction with `v-if` in Vue.js for conditional rendering.  The `v-else` block is rendered if the `v-if` condition is falsy. The previous sibling element must have a `v-if` or `v-else-if` directive.

Source: https://github.com/vuejs/docs/blob/main/src/api/built-in-directives.md#_snippet_2

```vue-html
<div v-if="Math.random() > 0.5">
  Now you see me
</div>
<div v-else>
  Now you don't
</div>
```

---

## v-pre Directive in Vue.js

Explains how v-pre prevents Vue.js from compiling an element and its children, preserving the raw template syntax. This is useful for displaying code examples or preventing Vue from interpreting specific sections of the template.

Source: https://github.com/vuejs/docs/blob/main/src/api/built-in-directives.md#_snippet_8

```vue-html
<span v-pre>{{ this will not be compiled }}</span>
```

