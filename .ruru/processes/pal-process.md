# Process: Process Assurance Lifecycle (PAL) v1.0

**Date:** 2025-04-16

**Authors:** Roo Commander, User (Jeremy)

**Status:** Active

---

**1. Goal & Scope**

*   **Goal:** To establish a standard, iterative process for creating, validating, and maintaining clear, correct, robust, and effective Standard Operating Procedures (SOPs) or Workflow documents governing multi-agent activities within the Roo Code system.
*   **Scope:** This lifecycle applies to the creation of new SOPs/Workflows and significant revisions of existing ones, particularly those involving delegation, context management, and quality assurance steps like ACQA.

**2. Core Principles**

*   **Iteration:** SOPs/Workflows are developed through cycles of drafting, review, simulation, and refinement.
*   **Simulation:** Virtual test runs are used to proactively identify flaws before real-world execution.
*   **Clarity:** Documents must use unambiguous language and clearly define steps, roles, inputs, and outputs.
*   **Fault Tolerance:** Documents should anticipate potential failure points and include error handling or escalation paths.
*   **Context Awareness:** Documents must ensure necessary context (specifications, data, user intent) is available or explicitly passed at each relevant step, especially during delegation.

**3. Agent Roles (within PAL)**

*   **Author/Owner:** The agent primarily responsible for drafting and maintaining the SOP/Workflow (often Roo Commander or a lead specialist).
*   **Conceptual Reviewer:** An agent tasked with reviewing the draft for clarity, logic, and completeness (e.g., `technical-writer`, `second-opinion`).
*   **Simulator:** The agent performing the virtual test run (usually the Author/Owner).
*   **User:** Provides final approval and guidance on requirements.

**4. The PAL Workflow**

*   **Phase 1: Drafting**
    1.  **Define Objective & Scope:** Clearly state what process the SOP/Workflow covers and its intended outcome.
    2.  **Identify Actors & Roles:** List the primary agents involved and their responsibilities.
    3.  **Select Template:** Choose the appropriate template (`.ruru/templates/toml-md/15_sop.md` for simple processes, `.ruru/templates/workflows/00_workflow_boilerplate.md` for complex workflows).
    4.  **Outline Steps:** Draft the initial sequence of actions using the chosen template, including inputs, tools, decision points, outputs, and basic error handling.
    5.  **Store Draft:** Save the initial version in `.ruru/planning/` (e.g., `draft-my-process.md`).

*   **Phase 2: Conceptual Review**
    1.  **Delegate Review:** Author delegates a review task (`new_task`) to a Conceptual Reviewer. Provide the draft path and objectives.
    2.  **Perform Review:** Reviewer analyzes the draft for clarity, logic, completeness, consistency, and potential contradictions.
    3.  **Provide Feedback:** Reviewer provides structured feedback.
    4.  **Incorporate Feedback:** Author updates the draft SOP/Workflow based on the review.

*   **Phase 3: Simulated Execution (Virtual Test Run)**
    1.  **Select Test Case:** Simulator chooses a realistic scenario the SOP/Workflow should handle.
    2.  **Walk Through:** Simulator follows the steps sequentially for the test case.
    3.  **Simulate Actions:**
        *   Assume plausible results for info gathering steps.
        *   Follow logic for decision points based on simulated conditions.
        *   For delegation steps (`new_task`): Formulate the message, critically assess if it includes *all necessary context*, and anticipate potential delegate failures/questions. Check if the SOP/Workflow handles these.
    4.  **Identify Gaps:** Document findings: ambiguities, missing steps, unhandled errors, insufficient context, incorrect assumptions, logical flaws.

*   **Phase 4: Refinement**
    1.  **Update Draft:** Author revises the draft based on simulation findings.
    2.  **Iterate:** Repeat Phase 2 (Review) and/or Phase 3 (Simulation) if refinements are significant, until confident.

*   **Phase 5: Integration Checks**
    1.  **Cross-Reference:** Ensure alignment with related processes (e.g., ACQA) and specifications.
    2.  **Verify Paths:** Double-check all document paths referenced are correct.

*   **Phase 6: Finalization & Deployment**
    1.  **User Approval:** Present the refined SOP/Workflow to the user for final review and approval via `ask_followup_question`.
    2.  **Determine Final Location:** Based on the document type (SOP vs. Workflow) and content, confirm the correct final directory (e.g., `.ruru/processes/`, `.ruru/workflows/`, `.ruru/docs/standards/`).
    3.  **Store Official Version:**
        *   Use `read_file` on the final draft in `.ruru/planning/`.
        *   Use `write_to_file` to save the content to the determined official path (e.g., `.ruru/processes/pal-process.md`). Ensure correct `line_count`.
    4.  **Cleanup Draft:** Use `execute_command rm` to delete the draft version from `.ruru/planning/`.
    5.  **Update Related Docs:** Ensure any documents referencing the SOP/Workflow are updated with the new path if necessary.
    6.  **Internal Knowledge:** (Future) Update internal knowledge base for relevant agents about the new/updated SOP/Workflow.

**5. Benefits**

*   Reduces errors caused by flawed or ambiguous SOPs/Workflows.
*   Improves reliability by ensuring context is considered during delegation.
*   Builds more robust and fault-tolerant multi-agent workflows.
*   Provides a structured way to iteratively improve operational procedures.

**6. Next Steps**

*   Adopt PAL as the standard method for developing/refining SOPs/Workflows.
*   Apply PAL retrospectively to the Mode Creation SOP v2 draft.
*   Utilize PAL for developing future SOPs/Workflows.