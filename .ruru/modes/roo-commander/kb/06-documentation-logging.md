# 06 - Documentation Management & Decision Records

This section outlines procedures for managing project documentation and creating Architecture Decision Records (ADRs). For detailed logging procedures, refer to `12-logging-procedures.md`.

**Formal Document Maintenance:**

*   **Responsibility:** Oversee high-level project documents. While Commander may directly edit files in `.ruru/planning/` due to their iterative nature, modifications to stable documents in `.ruru/docs/` typically require more rigor and should preferably be delegated to relevant specialists (e.g., `util-writer`, `core-architect`) to ensure stability and adherence to standards.
*   **Tool Guidance:**
    *   **Creating New Files:** Use `write_to_file` primarily for creating *new, relatively small* documents like initial planning drafts or ADRs based on templates (e.g., `.ruru/templates/toml-md/07_adr.md`).
    *   **Modifying Existing Files:** Strongly prefer `apply_diff` or `search_and_replace` for *modifying existing* documents, especially larger ones. This minimizes the risk of accidental data loss, improves efficiency, and provides clearer change tracking compared to overwriting the entire file with `write_to_file`.

**Decision Record Creation (ADRs):**

*   **Purpose:** Log all significant architectural, technological, or strategic decisions in `.ruru/decisions/` to maintain transparency and traceability.
*   **Guidance:** Create ADRs using `write_to_file`, targeting `.ruru/decisions/YYYYMMDD-brief-topic-summary.md`. Utilize the `07_adr.md` template from `.ruru/templates/toml-md/` or a similar structure.
*   **Example ADR Structure (Content remains illustrative):**
    ```markdown
    +++
    id = "YYYYMMDD-brief-topic-summary"
    title = "ADR: [Decision Title]"
    status = "Proposed | Accepted | Deprecated | Superseded" # Choose one
    date = "YYYY-MM-DD"
    # Optional: superseded_by = "YYYYMMDD-new-decision-id"
    # Optional: related_context = ["task-id", ".ruru/planning/doc.md"]
    tags = ["architecture", "backend", "database", ...]
    +++

    # ADR: [Decision Title]

    **Status:** [Status]
    **Date:** [Date]

    ## Context
    [Describe the issue, background, constraints, and forces driving the decision.]

    ## Decision
    [State the decision clearly and concisely.]

    ## Rationale
    [Explain the reasoning behind the decision. Justify why this option was chosen over alternatives.]

    ## Alternatives Considered
    [Briefly list other options evaluated and why they were not chosen.]

    ## Consequences
    [Outline the expected outcomes, impacts (positive and negative), and potential risks of this decision.]
    ```
*   **Logging:** Log the creation and context of the ADR according to the procedures in `12-logging-procedures.md`.