# Process: Adaptive Failure Resolution (AFR) v1.0

**Date:** 2025-04-16
**Status:** Active
**Related Documents:** `.ruru/processes/acqa-process.md` (ACQA)

---

**1. Objective:**

To define a structured process for identifying, analyzing, and resolving **recurring failures or specification deviations** detected during the Quality Assurance (QA) phase of delegated tasks, particularly within the ACQA framework. This aims to move beyond repeatedly fixing symptoms and address potential root causes in agent capabilities, instructions, specifications, or SOPs.

**2. Trigger:**

This process is triggered by the **Coordinator** (e.g., Roo Commander) during the "Critically Analyze Feedback & Detect Patterns" step (ACQA Workflow Step 5.e) when:

*   The *same type* of error or deviation from specification is identified by QA agents across multiple, independent task executions (e.g., > 2-3 times recently).
*   Examples: Consistent failure to use correct TOML format, repeated misinterpretation of a specific schema field, incorrect path formatting, failure to handle a specific edge case mentioned in instructions.

**3. Process Steps:**

1.  **Identify & Log Pattern (Coordinator):**
    *   Recognize the recurring nature of a specific QA finding.
    *   Log the pattern, noting:
        *   The specific error/deviation type.
        *   The tasks/modes affected.
        *   The relevant specification(s) or SOP step(s) being violated.
        *   Frequency/context of recurrence.

2.  **Pause Symptom Fixes (Coordinator):**
    *   Temporarily halt initiating further revision tasks (`new_task` or Boomerang) aimed *solely* at fixing the specific recurring error in new instances. (Other unrelated fixes can proceed).

3.  **Hypothesize Root Cause(s) (Coordinator):**
    *   Analyze the pattern and context. Potential root causes include:
        *   **Agent Capability/Instructions:** The delegate agent (e.g., `mode-maintainer`) lacks the necessary knowledge or explicit instruction in its core definition or custom instructions.
        *   **Specification Clarity:** The relevant specification document (e.g., Mode Spec, TOML+MD Rule) is ambiguous, incomplete, or potentially incorrect.
        *   **SOP Flaw:** The SOP guiding the task execution or delegation is missing steps, providing insufficient context, or making incorrect assumptions.
        *   **Delegation Error:** The Coordinator's delegation message consistently lacks critical context or instruction, despite the SOP.
        *   **Tooling Issue:** (Less likely for format errors, but possible) A tool used in the process is introducing errors.

4.  **Initiate Meta-Review & Analysis (Coordinator):**
    *   **Action:** Escalate the identified pattern and hypothesized root cause(s) to the **User**.
    *   **Proposal:** Recommend a specific meta-review action based on the hypothesis:
        *   *If Agent Capability suspected:* Propose reviewing and enhancing the specific agent's definition/instructions.
        *   *If Spec Clarity suspected:* Propose reviewing the relevant specification document for ambiguity, potentially involving `technical-writer` or `second-opinion`.
        *   *If SOP Flaw suspected:* Propose applying the Process Assurance Lifecycle (PAL) simulation to the relevant SOP section.
        *   *If Delegation Error suspected:* Propose reviewing the Coordinator's own delegation logic/templates.
    *   **Tool:** Use `ask_followup_question` to present the findings and proposed meta-review action(s) to the user for guidance/approval.

5.  **Execute Meta-Review (Delegated or Coordinated):**
    *   Based on user direction, execute the chosen meta-review action (e.g., delegate spec review to `technical-writer`, enhance agent definition, simulate SOP).

6.  **Implement Process/Agent Improvement:**
    *   Based on the meta-review findings, implement the necessary changes:
        *   Update agent definitions/instructions.
        *   Update specifications or rules.
        *   Update SOPs.
        *   Refine Coordinator delegation templates/logic.

7.  **Validate Improvement (Optional but Recommended):**
    *   Re-run a relevant test case (e.g., re-migrate a problematic mode) using the updated process/agent to confirm the recurring error is resolved. Apply ACQA.

8.  **Resume Normal Operations:**
    *   Remove the pause on fixing the specific error type.
    *   Continue processing tasks using the improved process/agents/specs.

**4. Integration with ACQA:**

*   AFR is triggered within ACQA's Step 5.e (Analyze Feedback).
*   It acts as an escalation path when simple revision cycles (ACQA Step 5.f) are insufficient due to recurring systemic issues.

**5. Benefits:**

*   Prevents wasted effort fixing recurring symptoms.
*   Drives improvement of underlying processes, specifications, and agent capabilities.
*   Leverages pattern detection for systemic quality control.
*   Incorporates user guidance in addressing fundamental issues.