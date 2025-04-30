# Vue.js Form Input Bindings

## Select Multiple Values with v-model in Vue

This snippet shows how to create a multiple select dropdown, allowing the user to select multiple options. The selected values are bound to an array using `v-model`.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/forms.md#_snippet_12

```vue-html
<div>Selected: {{ selected }}</div>

<select v-model="selected" multiple>
  <option>A</option>
  <option>B</option>
  <option>C</option>
</select>
```

---

## Checkbox Value Bindings in Vue

This snippet demonstrates how to bind the `true` and `false` values of a checkbox to specific strings using `true-value` and `false-value`. This allows you to control the value of the bound variable based on the checkbox's state.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/forms.md#_snippet_16

```vue-html
<input
  type="checkbox"
  v-model="toggle"
  true-value="yes"
  false-value="no" />
```

---

## Text Input Binding with v-model (Vue HTML)

Demonstrates basic text input binding using v-model. The input's value is bound to the 'text' variable. When the input value changes, the 'text' variable is updated automatically.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/forms.md#_snippet_0

```vue-html
<input
  :value="text"
  @input="event => text = event.target.value">

```

---

## Multiple Checkboxes with v-model (Vue HTML)

Demonstrates binding multiple checkboxes to the same 'checkedNames' array. When a checkbox is checked or unchecked, its value is added to or removed from the 'checkedNames' array.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/forms.md#_snippet_9

```vue-html
<div>Checked names: {{ checkedNames }}</div>

<input type="checkbox" id="jack" value="Jack" v-model="checkedNames" />
<label for="jack">Jack</label>

<input type="checkbox" id="john" value="John" v-model="checkedNames" />
<label for="john">John</label>

<input type="checkbox" id="mike" value="Mike" v-model="checkedNames" />
<label for="mike">Mike</label>

```

---

## Dynamically Render Select Options in Vue

This snippet shows how to dynamically render select options using `v-for`.  The options are created from an array of objects, where each object has a `text` and `value` property. The selected value is bound to a data property with `v-model`.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/forms.md#_snippet_13

```vue-html
<select v-model="selected">
  <option v-for="option in options" :value="option.value">
    {{ option.text }}
  </option>
</select>

<div>Selected: {{ selected }}</div>
```

---

## Multiline Text Input - Correct v-model Binding (Vue HTML)

Shows the correct way to bind a textarea to a reactive variable 'text' using v-model for proper two-way data binding.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/forms.md#_snippet_5

```vue-html
<!-- good -->
<textarea v-model="text"></textarea>

```

---

## Radio Buttons with v-model (Vue HTML)

Example of binding radio buttons to a 'picked' ref. When a radio button is selected, its value is assigned to the 'picked' ref.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/forms.md#_snippet_10

```vue-html
<div>Picked: {{ picked }}</div>

<input type="radio" id="one" value="One" v-model="picked" />
<label for="one">One</label>

<input type="radio" id="two" value="Two" v-model="picked" />
<label for="two">Two</label>

```

---

## Text Input Binding with v-model (Simplified) (Vue HTML)

A simplified version of the text input binding using v-model. This directive handles both the value binding and the input event listener, reducing boilerplate code.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/forms.md#_snippet_1

```vue-html
<input v-model="text">

```

---

## Text Input with v-model (Vue HTML)

Example of binding a text input to a 'message' ref using v-model. Any changes to the input field will automatically update the value of the 'message' ref, and vice versa.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/forms.md#_snippet_2

```vue-html
<p>Message is: {{ message }}</p>
<input v-model="message" placeholder="edit me" />

```

---

## Multiline Text Input with v-model (Vue HTML)

Illustrates binding a textarea element to a 'message' ref using v-model. This allows for capturing multiline text input and synchronizing it with the reactive variable.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/forms.md#_snippet_3

```vue-html
<span>Multiline message is:</span>
<p style="white-space: pre-line;">{{ message }}</p>
<textarea v-model="message" placeholder="add multiple lines"></textarea>

```

---

## Single Checkbox with v-model (Vue HTML)

Example of binding a single checkbox to a boolean 'checked' ref. The checkbox's checked state will update the 'checked' ref, and vice versa.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/forms.md#_snippet_6

```vue-html
<input type="checkbox" id="checkbox" v-model="checked" />
<label for="checkbox">{{ checked }}</label>

```

---

## Checkbox Dynamic Value Bindings in Vue

This snippet demonstrates how to dynamically bind the `true` and `false` values of a checkbox to data properties using `:true-value` and `:false-value`. This allows for more flexible control over the values associated with the checkbox state.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/forms.md#_snippet_17

```vue-html
<input
  type="checkbox"
  v-model="toggle"
  :true-value="dynamicTrueValue"
  :false-value="dynamicFalseValue" />
```

---

## Number Modifier for v-model in Vue

This snippet demonstrates the use of the `.number` modifier with `v-model`. This modifier automatically attempts to typecast the user input as a number. If parsing fails, the original string value is used.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/forms.md#_snippet_21

```vue-html
<input v-model.number="age" />
```

---

## Lazy Modifier for v-model in Vue

This snippet demonstrates the use of the `.lazy` modifier with `v-model`. This modifier syncs the input with the data only after a `change` event, instead of the default `input` event.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/forms.md#_snippet_20

```vue-html
<!-- synced after "change" instead of "input" -->
<input v-model.lazy="msg" />
```

---

## Trim Modifier for v-model in Vue

This snippet demonstrates the use of the `.trim` modifier with `v-model`. This modifier automatically trims whitespace from the user input.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/forms.md#_snippet_22

```vue-html
<input v-model.trim="msg" />
```

---

## Select Single Value with v-model in Vue

This snippet demonstrates how to create a single select dropdown using the `<select>` element and bind its selected value to a data property using `v-model`. It includes a disabled option as a best practice for iOS.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/forms.md#_snippet_11

```vue-html
<div>Selected: {{ selected }}</div>

<select v-model="selected">
  <option disabled value="">Please select one</option>
  <option>A</option>
  <option>B</option>
  <option>C</option>
</select>
```

---

## Radio Value Bindings in Vue

This snippet demonstrates how to bind the values of radio buttons to data properties using `:value`. When a radio button is selected, the value of the corresponding data property is assigned to the `v-model` bound variable.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/forms.md#_snippet_18

```vue-html
<input type="radio" v-model="pick" :value="first" />
<input type="radio" v-model="pick" :value="second" />
```

---

## Checkbox Value Assignment

Illustrates assigning string values of 'a' to the `picked` property when a radio button is checked and boolean values of true or false to the `toggle` property when a checkbox is checked. Also demonstrates assigning string values to a `selected` property when selecting the first option in a select element.

Source: https://github.com/vuejs/docs/blob/main/src/guide/essentials/forms.md#_snippet_23

```vue-html
<!-- `picked` is a string "a" when checked -->
<input type="radio" v-model="picked" value="a" />

<!-- `toggle` is either true or false -->
<input type="checkbox" v-model="toggle" />

<!-- `selected` is a string "abc" when the first option is selected -->
<select v-model="selected">
  <option value="abc">ABC</option>
</select>
```

