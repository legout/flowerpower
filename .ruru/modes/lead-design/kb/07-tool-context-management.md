# Tool Usage & Context Management

## Tool Proficiency

*   **Core Tools:** Proficiently use `new_task` for delegation, `read_file` for reviewing context/deliverables, `ask_followup_question` for clarification, and `attempt_completion` for reporting.
*   **Diligence:** Before invoking any tool, carefully review its description and parameters. Ensure all required parameters are included with valid values.
*   **Iterative Execution:** Use tools one step at a time. Wait for the result of each tool use before proceeding to the next step.

## Context Management

*   **Knowledge Base:** Maintain awareness of project design goals, target audience personas, and user journey maps.
*   **Key Documents:** Be familiar with the project's existing design system, component libraries, and style guides.
*   **Context Directory:** Utilize the mode's context directory (`v7.1/modes/lead/design/design-lead/context/`) for relevant documentation, including:
    *   Design system documentation (`design-system.md`)
    *   Style guides (`style-guide.md`)
    *   Project brand guidelines (`brand-guidelines.md`)
    *   Design workflow templates/checklists (`workflow-templates.md`)
    *   Common design patterns/best practices (`design-best-practices.md`)
    *   Design review criteria (`review-criteria.md`)
    *   Accessibility guidelines (`accessibility-guidelines.md`)
    *   User experience principles (`ux-principles.md`)
    *   Design tool documentation (`tooling.md`)
*   **Structural Context:** Refer to `.ruru/templates/mode_hierarchy.md` and `.ruru/templates/mode_folder_structure.md` for understanding the overall system structure.
*   **Worker Context:** Reference context files for `ui-designer` and `diagramer` when needed to understand their specific capabilities or provide them with relevant information.