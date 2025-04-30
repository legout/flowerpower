# Process Templates (`.ruru/templates/processes/`)

This directory contains standard templates for creating new process documents, such as Standard Operating Procedures (SOPs) or more complex Workflows/Lifecycles.

## Purpose

Using these templates ensures consistency, clarity, and includes essential sections for defining robust and understandable processes within the Roo Code system. They incorporate best practices observed in existing processes located in `.ruru/processes/`.

## Available Templates:

*   **`00_sop_basic.md`**: A basic SOP template using standard Markdown. Suitable for simpler, descriptive processes where extensive machine-readable metadata isn't critical.
*   **`01_sop_toml_md.md`**: An enhanced SOP template using **TOML+Markdown**. This is the **preferred format for most new SOPs**, especially those tied to specific scripts, tools, or artifacts, as it provides structured metadata.
*   **`02_workflow_lifecycle.md`**: A template for more complex, multi-phase processes, workflows, or lifecycles, using standard Markdown. Suitable for describing coordination patterns, iterative cycles, or processes involving multiple roles and decision points (similar to PAL or ACQA).

## Usage Guidelines:

1.  **Choose the Right Template:** Select the template that best fits the complexity and nature of the process you are defining. Prefer `01_sop_toml_md.md` for standard procedures.
2.  **Copy, Don't Modify:** Copy the chosen template to your working location (e.g., `.ruru/planning/` during drafting) before modifying it. Do not edit the templates directly in this directory.
3.  **Fill Sections:** Complete all relevant sections of the template. Pay close attention to:
    *   **Objective:** Clearly state the goal.
    *   **Metadata (TOML or Markdown):** Update version, status, date, inputs, outputs, tags, etc.
    *   **Steps:** Provide clear, sequential instructions. Specify tools and context for delegation.
    *   **Error Handling:** Consider potential failure points.
4.  **Validate:** Use the Process Assurance Lifecycle (PAL) defined in `.ruru/processes/pal-process.md` (involving review and simulation) to validate the draft process before finalizing.
5.  **Finalize:** Once validated and approved, move the completed process document to the appropriate final location (usually `.ruru/processes/` or `.ruru/workflows/`).