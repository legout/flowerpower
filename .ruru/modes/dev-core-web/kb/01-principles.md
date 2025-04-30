+++
# --- Basic Metadata ---
id = "KB-COREWEB-PRINCIPLES-V1"
title = "KB: Core Web Developer - Core Principles"
context_type = "best_practices"
scope = "Guiding principles for Core Web Developer mode"
target_audience = ["dev-core-web"]
granularity = "principles"
status = "active"
last_updated = "2025-04-22"
tags = ["kb", "principles", "best-practices", "html", "css", "javascript", "a11y", "responsive", "vanilla-js", "dev-core-web"]
related_context = [
    ".ruru/modes/dev-core-web/kb/03-html-structure.md",
    ".ruru/modes/dev-core-web/kb/04-css-styling.md",
    ".ruru/modes/dev-core-web/kb/05-vanilla-js.md",
    ".ruru/modes/dev-core-web/kb/06-accessibility-basics.md"
]
template_schema_doc = ".ruru/templates/toml-md/08_ai_context_source.README.md"
relevance = "High: Defines the fundamental approach to development"
+++

# KB: Core Web Developer - Core Principles

These principles guide your work as the Core Web Developer.

1.  **Semantic HTML:** Prioritize using HTML elements according to their semantic meaning (e.g., `<nav>`, `<article>`, `<button>`, `<label>`). This improves accessibility and SEO. (See KB `03-html-structure.md`).
2.  **Modern CSS:** Utilize modern CSS features like Flexbox and Grid for layout. Employ CSS Custom Properties (variables) for maintainable styling. Write clean, organized, and understandable CSS. (See KB `04-css-styling.md`).
3.  **Responsive Design:** Ensure layouts and components adapt appropriately to different screen sizes and devices. Use relative units (em, rem, %), media queries, and flexible layout techniques.
4.  **Vanilla JavaScript (ES6+):** Implement client-side interactivity using standard, modern JavaScript features (`let`/`const`, arrow functions, Promises, `async`/`await`, template literals, modules). Avoid unnecessary libraries for basic tasks. Write efficient and readable JS. (See KB `05-vanilla-js.md`).
5.  **Accessibility (Basics):** Incorporate fundamental accessibility practices: use semantic HTML, provide text alternatives for images (`alt` text), ensure keyboard navigability for interactive elements, use appropriate ARIA roles/attributes where necessary, and consider color contrast. Escalate complex accessibility requirements. (See KB `06-accessibility-basics.md`).
6.  **Performance Awareness:** Write reasonably efficient code. Be mindful of large image sizes, minimize direct DOM manipulation within loops, and consider basic loading strategies. Escalate significant performance optimization needs.
7.  **Maintainability:** Write code that is easy to read, understand, and modify. Use clear naming conventions and add comments for complex or non-obvious logic.
8.  **Cross-Browser Considerations:** Aim for compatibility with modern evergreen browsers (latest Chrome, Firefox, Safari, Edge) unless otherwise specified.
9.  **Progressive Enhancement:** Where appropriate, ensure core functionality works without JavaScript enabled, enhancing the experience when JS is available.
10. **Simplicity:** Prefer simple, straightforward solutions using core web technologies over complex abstractions unless complexity is warranted and approved.