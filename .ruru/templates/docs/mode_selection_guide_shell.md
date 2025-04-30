+++
id = "STD-MODE-SELECTION-GUIDE-V1"
title = "Mode Selection & Discovery Guide"
context_type = "standard"
scope = "Provides guidance for selecting the appropriate mode for task delegation"
target_audience = ["roo-commander", "prime-coordinator", "lead-*", "manager-*", "all"] # Anyone delegating tasks
granularity = "detailed"
status = "active"
last_updated = "2025-04-25" # Use current date
tags = ["modes", "delegation", "selection", "discovery", "standard", "documentation", "hierarchy", "collaboration"]
related_context = [
    ".ruru/docs/standards/mode_naming_standard.md",
    ".ruru/modes/roo-commander/kb/available-modes-summary.md",
    ".roo/rules-roo-commander/03-delegation-simplified.md"
    ]
template_schema_doc = ".ruru/templates/toml-md/16_ai_rule.README.md"
relevance = "Critical: Essential for effective task delegation and coordination"
+++

# Mode Selection & Discovery Guide

## 1. Purpose

This guide provides structured information and principles to assist all modes (especially coordinators like `roo-commander`, Leads, and Managers) in selecting the most appropriate specialist mode for a given task. Effective delegation is key to efficient project execution.

## 2. General Selection Principles

1.  **Specificity First:** Always prefer a specialist mode whose core purpose directly matches the task over a generalist mode (e.g., use `framework-react` for React work over `util-senior-dev`).
2.  **Match Keywords & Tags:** Use the task description's keywords and the project's `stack_profile.json` to find modes with matching `tags` or capabilities.
3.  **Consider Hierarchy:** Understand the typical flow: Managers/Commander delegate to Leads or Agents; Leads delegate to Specialists or Agents within their domain. Use `core-architect` for high-level design, Leads for domain coordination, Specialists for implementation.
4.  **Consult Stack Profile:** Check `.ruru/context/stack_profile.json` for project-specific technology choices that might favour certain framework or data specialists.
5.  **Review Capabilities:** If unsure between similar modes, review their specific `Key Capabilities` listed below.
6.  **Use MDTM Appropriately:** Delegate complex, stateful, or high-risk tasks using the MDTM workflow (Rule `04-mdtm-workflow-initiation.md`). Use simple `new_task` for straightforward requests.
7.  **When in Doubt, Ask:** If unsure after consulting this guide, use `ask_followup_question` to confirm the best mode with the user or a higher-level coordinator.

## 3. Mode Details

*(Note: The detailed information below, especially under "Hierarchy & Collaboration", is intended to be automatically generated and maintained by a build script parsing individual `.mode.md` files. Manual updates should be avoided.)*

---

### `[mode-slug]` (`[Emoji] [Display Name]`)

*   **Core Purpose:** [Brief 1-sentence summary of the mode's main responsibility]
*   **Key Capabilities/Skills:**
    *   [Specific action or area of expertise 1]
    *   [Specific action or area of expertise 2]
    *   ...
*   **Common Task Types:**
    *   [Concrete example of a suitable task 1]
    *   [Concrete example of a suitable task 2]
    *   ...
*   **Tags/Keywords:** `[tag1]`, `[tag2]`, `[technology]`, ...
*   **Hierarchy & Collaboration:**
    *   **Typical Delegators:** `[mode-slug-A]`, `[mode-slug-B]`
        *   *Common Context Provided:* [e.g., MDTM ID, file paths, requirements doc path, design specs, API details]
    *   **Typical Reports To:** `[mode-slug-A]`
        *   *Common Information Reported:* [e.g., Completion status (`🟢 Done`/`⚪ Blocked`), modified file paths, blockers description, results/outputs path, test results]
    *   **Frequent Collaborators:** `[mode-slug-C]`, `[mode-slug-D]`
        *   *Typical Interaction:* [e.g., Requesting API details from `lead-backend`, clarifying UI behavior with `design-ui`, reviewing shared interfaces with `core-architect`]
*   **Selection Hints:**
    *   [Quick question or tip, e.g., "Is the primary goal UI implementation in React?"]
*   **When NOT to Use:**
    *   [Example of an unsuitable task, e.g., "Adding new features (use a dev specialist)", "High-level architecture (use `core-architect`)"]

---

*(Repeat the above template structure for each mode. The content within brackets `[]` serves as a placeholder for information to be populated by the build script.)*

---

## 4. Maintaining This Guide

The detailed mode information in Section 3 should be kept up-to-date automatically. A dedicated build script (e.g., `build_mode_selection_guide_data.js` - **Task TBD**) is responsible for parsing all `.mode.md` files and regenerating the content for Section 3. Manual edits to Section 3 are discouraged as they will be overwritten.