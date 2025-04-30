+++
# --- Basic Metadata ---
id = "KB-COREWEB-HTML-V1"
title = "KB: Core Web Developer - Semantic HTML Structure"
context_type = "best_practices"
scope = "Guidelines for writing semantic and accessible HTML5"
target_audience = ["dev-core-web"]
granularity = "guideline"
status = "active"
last_updated = "2025-04-22"
tags = ["kb", "html", "semantic-html", "accessibility", "structure", "dev-core-web"]
related_context = [".ruru/modes/dev-core-web/kb/01-principles.md", ".ruru/modes/dev-core-web/kb/06-accessibility-basics.md"]
template_schema_doc = ".ruru/templates/toml-md/08_ai_context_source.README.md"
relevance = "High: Foundational for accessible and maintainable UIs"
+++

# KB: Semantic HTML Structure Guidelines

Use HTML elements according to their semantic meaning to improve accessibility, SEO, and code clarity.

## 1. Document Structure

*   **`<!DOCTYPE html>`:** Always start with the HTML5 doctype.
*   **`<html>`:** Root element, include `lang` attribute (e.g., `<html lang="en">`).
*   **`<head>`:** Contains meta-information.
    *   **`<meta charset="UTF-8">`:** Essential for character encoding.
    *   **`<meta name="viewport" content="width=device-width, initial-scale=1.0">`:** Crucial for responsive design.
    *   **`<title>`:** Required, descriptive page title.
    *   Link CSS (`<link rel="stylesheet" href="...">`).
    *   Include critical scripts or deferred/async scripts.
*   **`<body>`:** Contains the visible page content.

## 2. Page Sectioning & Landmarks

Use appropriate elements to define page structure and navigation landmarks:

*   **`<header>`:** Introductory content or navigational links for the page or a section. Often contains headings (`<h1>`-`<h6>`), logo, search form.
*   **`<nav>`:** Represents a section with major navigation links (main site navigation, table of contents, etc.).
*   **`<main>`:** **Enclose the dominant content** of the `<body>`. There should typically be **only one** `<main>` element per page, not nested inside `<article>`, `<aside>`, `<header>`, `<nav>`, or `<footer>`.
*   **`<article>`:** Self-contained composition intended for independent distribution or reuse (e.g., blog post, forum entry, news article).
*   **`<section>`:** Represents a thematic grouping of content, typically with a heading. Use when there isn't a more specific semantic element. Don't use it as a generic container; use `<div>` for that.
*   **`<aside>`:** Represents content tangentially related to the main content (e.g., sidebar, call-out box, related links).
*   **`<footer>`:** Footer for the nearest sectioning content or root (`<body>`). Often contains copyright, author info, related links.
*   **`<h1>` - `<h6>`:** Define heading hierarchy. Use `<h1>` for the main page title (usually only one). Structure sub-sections logically with `<h2>`, `<h3>`, etc. Do not skip levels (e.g., don't jump from `<h2>` to `<h4>`).

## 3. Content Elements

*   **`<p>`:** Paragraphs of text.
*   **`<ul>`, `<ol>`, `<li>`:** Unordered and ordered lists for list items.
*   **`<dl>`, `<dt>`, `<dd>`:** Description lists (term/definition pairs).
*   **`<blockquote>`, `<q>`:** Block and inline quotations. Use `cite` attribute for source URL.
*   **`<code>`, `<pre>`:** Inline code snippets and preformatted blocks of code.
*   **`<em>`, `<strong>`:** Emphasis and strong importance (affect semantics). Use `<i>` or `<b>` only for stylistic offsets without changing meaning (less common).
*   **`<a>`:** Hyperlinks. Must have `href`. Ensure link text is descriptive.
*   **`<img>`:** Images. **Crucially, always provide meaningful `alt` text** describing the image content, unless the image is purely decorative (`alt=""`).
*   **`<figure>`, `<figcaption>`:** Group images/diagrams with their captions.

## 4. Interactive Elements & Forms

*   **`<button>`:** Use for actions triggered by a click. Provide clear text content. Do *not* use `<div>` or `<a>` styled as buttons unless absolutely necessary (and add `role="button"` and keyboard handling if you do).
*   **`<form>`:** Container for form controls. Specify `method` (`GET` or `POST`) and `action` (URL to submit to).
*   **`<label>`:** **Associate labels explicitly with form controls** using the `for` attribute matching the control's `id`. This is critical for accessibility.
    ```html
    <label for="username">Username:</label>
    <input type="text" id="username" name="username">
    ```
*   **`<input>`:** Use appropriate `type` attributes (`text`, `email`, `password`, `number`, `date`, `checkbox`, `radio`, `submit`, `button`, `hidden`, etc.).
*   **`<select>`, `<option>`, `<optgroup>`:** Dropdown lists.
*   **`<textarea>`:** Multiline text input.
*   **`<fieldset>`, `<legend>`:** Group related form controls, providing a caption with `<legend>`.

## 5. Generic Containers

*   **`<div>`:** Generic block-level container with no semantic meaning. Use for styling or grouping when no other semantic element applies.
*   **`<span>`:** Generic inline container with no semantic meaning. Use for styling parts of text or grouping inline elements.

**Key Takeaway:** Choose HTML elements based on their *meaning* and *purpose*, not just their default appearance. This creates more accessible, maintainable, and SEO-friendly structures. Avoid using `<div>` and `<span>` excessively when a more specific semantic element exists.