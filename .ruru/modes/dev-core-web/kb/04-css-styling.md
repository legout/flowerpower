+++
# --- Basic Metadata ---
id = "KB-COREWEB-CSS-V1"
title = "KB: Core Web Developer - Modern CSS Styling Practices"
context_type = "best_practices"
scope = "Guidelines for writing effective and maintainable CSS"
target_audience = ["dev-core-web"]
granularity = "guideline"
status = "active"
last_updated = "2025-04-22"
tags = ["kb", "css", "styling", "layout", "flexbox", "grid", "responsive", "variables", "best-practices", "dev-core-web"]
related_context = [
    ".ruru/modes/dev-core-web/kb/01-principles.md",
    ".ruru/modes/dev-core-web/kb/03-html-structure.md"
]
template_schema_doc = ".ruru/templates/toml-md/08_ai_context_source.README.md"
relevance = "High: Core skill for UI implementation"
+++

# KB: Modern CSS Styling Practices

Guidelines for writing effective, maintainable, and responsive CSS for core web development.

## 1. Layout: Flexbox & Grid

*   **Prefer Modern Layouts:** Use CSS Flexbox (`display: flex`) and CSS Grid (`display: grid`) as the primary methods for page and component layout. Avoid legacy techniques like floats or `<table>` for layout unless absolutely necessary for specific backward compatibility or email templates.
*   **Flexbox:** Ideal for one-dimensional layouts (rows or columns), distributing space, and aligning items. Key properties: `display: flex`, `flex-direction`, `justify-content`, `align-items`, `gap`, `flex-grow`, `flex-shrink`, `flex-basis`, `align-self`.
*   **Grid:** Ideal for two-dimensional layouts (rows and columns). Key properties: `display: grid`, `grid-template-columns`, `grid-template-rows`, `gap`, `grid-column`, `grid-row`, `grid-area`, `justify-items`, `align-items`.
*   **Combine Them:** Flexbox and Grid can be nested and used together effectively.

## 2. Responsive Design

*   **Mobile-First Approach (Recommended):** Design styles for mobile screens first, then use `min-width` media queries to add complexity or adjustments for larger screens.
    ```css
    /* Mobile styles first */
    .container { width: 95%; margin: 0 auto; }
    .sidebar { display: none; }

    /* Tablet and up */
    @media (min-width: 768px) {
      .container { width: 90%; }
      .sidebar { display: block; width: 200px; }
      .main-content { margin-left: 210px; }
    }

    /* Desktop and up */
    @media (min-width: 1024px) {
      .container { width: 80%; max-width: 1200px; }
    }
    ```
*   **Media Queries:** Use `@media` rules to apply styles based on viewport characteristics (width, height, orientation, resolution).
*   **Relative Units:** Prefer relative units like `em`, `rem`, `%`, `vw`, `vh` over absolute units (`px`) for properties like font sizes, padding, margins, and widths where scalability is desired. `rem` is often preferred for font-size consistency.
*   **Flexible Images/Media:** Use `max-width: 100%; height: auto;` for images and videos to prevent them from overflowing their containers.

## 3. CSS Variables (Custom Properties)

*   **Usage:** Define reusable values (colors, spacing, font sizes) at the root (`:root`) or component level. Improves maintainability and theming capabilities.
*   **Syntax:**
    *   Define: `--main-color: #333;`
    *   Use: `color: var(--main-color);`
    *   Provide fallbacks: `color: var(--main-color, black);`

```css
:root {
  --primary-color: #007bff;
  --secondary-color: #6c757d;
  --base-spacing: 8px;
  --font-family-sans: sans-serif;
}

body {
  font-family: var(--font-family-sans);
}

.button-primary {
  background-color: var(--primary-color);
  color: white;
  padding: var(--base-spacing) calc(var(--base-spacing) * 2);
}
```

## 4. Selectors & Specificity

*   **Prefer Classes:** Style primarily using classes (`.my-component`). Avoid relying heavily on tag selectors (`div`, `p`) or IDs (`#my-id`) for general styling, as they can be less reusable or overly specific. IDs should be reserved mainly for unique landmarks or JavaScript hooks.
*   **Keep Specificity Low:** Avoid overly complex selectors (`#main .nav > ul li a.active`) as they increase specificity, making overrides difficult and brittle. Aim for flatter structures.
*   **Methodologies (Optional):** Consider methodologies like BEM (Block, Element, Modifier - e.g., `.card__title--highlighted`) if the project requires a strict convention for naming and structure, especially in larger teams or projects without component frameworks.

## 5. Organization & Maintainability

*   **File Structure:** Organize CSS into logical files (e.g., `base.css`, `layout.css`, `components/button.css`, `utils.css`). Use `@import` (at the top of files) or a build tool to combine them.
*   **Comments:** Use comments (`/* ... */`) to explain complex selectors, non-obvious styles (like `z-index`), or section breaks.
*   **DRY (Don't Repeat Yourself):** Use CSS variables or utility classes (if applicable) to avoid repeating common style declarations.

## 6. Basic Transitions & Animations

*   **`transition` Property:** Use for simple property changes on hover/focus states. Specify the `property`, `duration`, `timing-function`, and `delay`.
*   **`@keyframes` & `animation` Property:** Use for more complex, multi-step animations.

```css
.button {
  transition: background-color 0.3s ease-out, transform 0.2s ease;
}

.button:hover {
  background-color: #555;
  transform: translateY(-2px);
}

@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.5; }
  100% { opacity: 1; }
}

.pulsing-element {
  animation: pulse 2s infinite ease-in-out;
}
```

Write clean, modern, responsive CSS using Flexbox/Grid, variables, and sensible selectors. Keep specificity manageable and organize files logically.