+++
# --- Basic Metadata ---
id = "KB-COREWEB-A11Y-BASICS-V1"
title = "KB: Core Web Developer - Accessibility (a11y) Basics"
context_type = "best_practices"
scope = "Fundamental accessibility checks and implementation guidelines"
target_audience = ["dev-core-web"]
granularity = "guideline"
status = "active"
last_updated = "2025-04-22"
tags = ["kb", "accessibility", "a11y", "wcag", "html", "semantic-html", "aria", "dev-core-web"]
related_context = [".ruru/modes/dev-core-web/kb/01-principles.md", ".ruru/modes/dev-core-web/kb/03-html-structure.md"]
template_schema_doc = ".ruru/templates/toml-md/08_ai_context_source.README.md"
relevance = "High: Essential for creating inclusive UIs"
+++

# KB: Accessibility (a11y) Basics

Ensure your implementations are usable by everyone, including those using assistive technologies. Focus on these fundamentals. Escalate complex a11y issues to the `frontend-lead` (suggesting `util-accessibility`).

## 1. Semantic HTML

*   **Foundation:** Using the correct HTML element for its purpose (KB `03`) provides a strong accessibility foundation. Screen readers and browsers understand the meaning of semantic elements.
*   **Examples:** Use `<button>` for clickable actions, `<nav>` for navigation, `<main>` for primary content, proper heading levels (`<h1>`-`<h6>`), lists (`<ul>`, `<ol>`) for list content, etc.
*   **Avoid:** Don't use `<div>` or `<span>` with click handlers when a `<button>` is appropriate. Don't use bold tags (`<b>`) for headings.

## 2. Images & Alternatives (`alt` Text)

*   **Requirement:** All `<img>` elements **must** have an `alt` attribute.
*   **Meaningful `alt`:** Describe the *content and function* of the image concisely. If the image conveys information, the `alt` text should convey the same information.
    ```html
    <img src="logo.png" alt="Roo Code Company Logo">
    <img src="chart.png" alt="Bar chart showing increasing sales over Q1.">
    ```
*   **Decorative Images:** If an image is purely decorative and provides no information, use an empty `alt` attribute (`alt=""`). This tells screen readers to ignore it.
    ```html
    <img src="background-pattern.svg" alt="">
    ```
*   **Complex Images:** For charts or diagrams, provide a longer description nearby or link to one. The `alt` text can be brief, indicating what the image is (e.g., `alt="Sales chart - See description below."`).

## 3. Form Labels & Instructions

*   **Explicit Labels:** Every form control (`<input>`, `<textarea>`, `<select>`) **must** have an associated `<label>`. Use the `for` attribute on the `<label>` matching the `id` of the control.
    ```html
    <label for="user-email">Email Address:</label>
    <input type="email" id="user-email" name="email">
    ```
*   **Grouping Controls:** Use `<fieldset>` and `<legend>` to group related controls (like radio buttons or checkboxes) and provide a group label.
*   **Instructions & Errors:** Provide clear instructions and error messages. Associate errors with specific fields using `aria-describedby` if necessary (consult lead/specialist for complex cases).

## 4. Keyboard Navigation & Focus

*   **Focus Order:** Ensure users can navigate through all interactive elements (links, buttons, form fields) using the `Tab` key in a logical order (usually matching the visual order). Avoid manipulating `tabindex` unless absolutely necessary and well understood.
*   **Focus Visibility:** Ensure the element that currently has keyboard focus has a clear visual indicator (the default browser outline is often sufficient, but don't disable it with `outline: none;` without providing an alternative).
*   **Interactive Elements:** Use naturally focusable elements like `<a>`, `<button>`, `<input>`, `<select>`, `<textarea>`. If using non-focusable elements like `<div>` for interaction (generally discouraged), add `tabindex="0"` to make them focusable and ensure appropriate keyboard event listeners (Enter/Space for activation) are added.

## 5. Basic ARIA Roles (Use Sparingly)

*   **ARIA (Accessible Rich Internet Applications):** Provides additional attributes to enhance semantics when native HTML isn't sufficient (e.g., for complex custom widgets).
*   **Principle:** Prefer using native semantic HTML elements first. Use ARIA only when necessary to bridge gaps.
*   **Common Roles:** You might occasionally need simple roles like `role="button"` (if using a `<div>` as a button, *not recommended*), `role="alert"` (for dynamic error messages), or `role="dialog"` (for modals, though ensure focus management).
*   **Common Properties:** `aria-label="Accessible Name"` (provides label when none visible), `aria-labelledby="idOfLabelElement"`, `aria-describedby="idOfDescriptionElement"`.
*   **Consult:** For complex widgets or advanced ARIA usage, consult the `frontend-lead` or `util-accessibility`.

## 6. Color Contrast

*   Ensure sufficient contrast between text and background colors to meet WCAG AA guidelines (4.5:1 for normal text, 3:1 for large text/UI components). Use online contrast checkers or browser developer tools if unsure, especially if using custom color schemes.

Focusing on these basics significantly improves the accessibility of the interfaces you build.