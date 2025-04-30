# Material UI: Accessibility (a11y)

Ensuring MUI components are implemented accessibly.

## Core Concept

MUI components are designed with accessibility in mind, aiming to follow WAI-ARIA standards and best practices. However, correct implementation and usage are crucial to maintain accessibility.

**Key Principles:**

*   **Semantic HTML:** While MUI components render underlying HTML, ensure you use them semantically where possible (e.g., using `<Button component="a" href="...">` for links styled as buttons).
*   **Keyboard Navigation:** Most interactive MUI components are designed to be keyboard navigable (using Tab, Shift+Tab, Arrow keys, Enter, Space). Verify this during testing.
*   **Focus Management:** Components like `Modal`, `Drawer`, and `Menu` manage focus trapping automatically. Ensure custom implementations also handle focus correctly.
*   **Labels & Descriptions:** Provide clear, associated labels for form controls (`TextField`, `Checkbox`, `Radio`, `Select`, `Slider`). Use `aria-label`, `aria-labelledby`, or `<label>` appropriately. Use helper text or `aria-describedby` for additional instructions or error messages.
*   **Color Contrast:** While the default theme aims for good contrast, custom theme palettes or `sx` prop overrides must be checked for sufficient contrast (WCAG AA: 4.5:1 for normal text, 3:1 for large text/UI components).
*   **ARIA Attributes:** MUI components often render necessary ARIA attributes automatically (e.g., `role`, `aria-haspopup`, `aria-expanded`). Avoid overriding these unless you fully understand the implications. Add supplementary ARIA attributes if needed for custom structures or behaviors.

## Common Component Considerations

*   **`<Button>`:** Ensure button text clearly describes the action. If using an `<IconButton>`, provide an accessible name via `aria-label`.
    ```jsx
    import IconButton from '@mui/material/IconButton';
    import DeleteIcon from '@mui/icons-material/Delete';

    <IconButton aria-label="delete item" color="error">
      <DeleteIcon />
    </IconButton>
    ```
*   **`<TextField>`:** Always provide a visible `<label>` or an `aria-label` if a visible label is not feasible. Use `helperText` and the `error` prop for validation feedback.
*   **`<Checkbox>`, `<Radio>`, `<Switch>`:** Use `<FormControlLabel>` to associate the control with a visible label. If no visible label exists, use `aria-label` on the input component itself. Group radio buttons within `<RadioGroup>` which should have an accessible name (via `<FormLabel>` or `aria-label`).
*   **`<Select>`:** Use `<InputLabel>` with an `id` and reference it using `labelId` on the `<Select>` component. Ensure the `<Select>` also has a `label` prop matching the `InputLabel` text.
*   **`<Modal>` / `<Dialog>`:** Ensure they have descriptive titles using `<DialogTitle>` referenced by `aria-labelledby` on the `<Dialog>`. Content should be described by `aria-describedby` referencing `<DialogContentText>` if applicable. Focus is managed automatically.
*   **`<Link>`:** Ensure link text is descriptive. If using with a routing library, pass the router's Link component via the `component` prop.
*   **`<Table>`:** Use `<th>` elements with `scope="col"` or `scope="row"` for table headers. Provide a `<caption>` or use `aria-label`/`aria-labelledby` on the `<Table>` element.
*   **`<Tabs>`:** Ensure each `<Tab>` has `id` and `aria-controls` linking to the corresponding tab panel's `id` and `aria-labelledby`. (MUI handles this if using standard structure).
*   **`<Autocomplete>`:** The `renderInput` prop requires rendering a `<TextField>` which needs an accessible label.

## Testing

*   **Keyboard Navigation:** Navigate through all interactive elements using only the Tab, Shift+Tab, Arrow keys, Enter, and Space keys. Ensure focus is always visible and moves logically. Check for keyboard traps.
*   **Screen Reader:** Use a screen reader (NVDA, JAWS, VoiceOver) to navigate the UI and verify that component roles, states, names, and values are announced correctly.
*   **Contrast Checkers:** Use browser extensions or online tools to check text and UI element contrast ratios against WCAG standards, especially after theme customization.

While MUI provides a strong accessible foundation, developers must use components correctly, provide necessary labels, and test interactions to ensure an accessible experience for all users. Consult the `accessibility-specialist` via your lead for complex scenarios or audits.

*(Refer to the official MUI documentation section on Accessibility.)*