+++
# --- Basic Metadata ---
id = "WORKFLOW-WEBDEV-001"
title = "Carefree One-Pager Creation"
status = "draft"
created_date = "2025-04-17"
updated_date = "2025-04-17"
version = "1.0"
tags = ["workflow", "web-development", "frontend", "design", "one-pager", "html", "css", "javascript"]

# --- Ownership & Context ---
owner = "Roo Commander"
related_docs = [] # Potential: Links to relevant mode docs if needed later
related_templates = []

# --- Workflow Specific Fields ---
objective = "Rapidly create a fully coded, functional HTML/CSS/JS single-page website from a loose concept, emphasizing creativity and a 'carefree vibe'."
scope = "Applies to the creation of simple, single-page websites where rapid development and creative freedom are prioritized over complex features or strict requirements. Assumes basic HTML/CSS/JS output."
roles = [
    "User",
    "Roo Commander",
    "ask",
    "worker/design/ui-designer",
    "worker/design/one-shot-web-designer",
    "worker/frontend/frontend-developer",
    "worker/frontend/tailwind-specialist", # If applicable
    "worker/frontend/bootstrap-specialist" # If applicable
]
trigger = "User request for a simple, 'carefree' one-page website based on a loose concept."
success_criteria = [
    "A functional HTML/CSS/JS one-page website is created and delivered.",
    "The website visually and conceptually reflects the user's desired 'carefree vibe' and initial concept.",
    "The user confirms satisfaction with the final output."
]
failure_criteria = [
    "The generated website files (HTML/CSS/JS) are non-functional or contain critical errors.",
    "The final design significantly deviates from the user's concept/vibe without justification or iteration.",
    "The workflow fails to produce a usable website after reasonable iteration attempts."
]

# --- Integration ---
acqa_applicable = false # Creative workflow, formal ACQA likely not primary focus
pal_validated = false
validation_notes = ""

# --- AI Interaction Hints (Optional) ---
# context_type = "workflow_definition"
+++

# Carefree One-Pager Creation

## 1. Objective 🎯
*   Rapidly create a fully coded, functional HTML/CSS/JS single-page website from a loose concept, emphasizing creativity and a "carefree vibe".

## 2. Scope ↔️
*   Applies to the creation of simple, single-page websites where rapid development and creative freedom are prioritized over complex features or strict requirements.
*   Assumes the primary output will be standard HTML, CSS, and potentially JavaScript, unless specific frameworks (like Tailwind/Bootstrap) are introduced during iteration.

## 3. Roles & Responsibilities 👤
*   **User:** Provides the initial concept, vibe, feedback, and final approval.
*   **Roo Commander:** Orchestrates the workflow, delegates tasks to specialists, manages iterations, and presents results to the User.
*   **ask / worker/design/ui-designer:** (Optional) Assists in brainstorming, mood board generation, and initial concept refinement.
*   **worker/design/one-shot-web-designer:** Primary agent for generating the initial coded design based on the refined concept.
*   **worker/frontend/frontend-developer / worker/frontend/tailwind-specialist / worker/frontend/bootstrap-specialist:** Specialist agents engaged for iterative code refinement and polishing based on User feedback.

## 4. Preconditions🚦
*   User provides a loose concept or idea for the one-page website.
*   Roo Commander understands the goal is rapid, creative development over strict adherence to detailed specs.

## 5. Reference Documents & Tools 📚🛠️
*   **Documents:** None strictly required, but User might provide inspirational images/links.
*   **Tools:** `ask_followup_question`, `new_task`, `read_file`, `write_to_file`, `apply_diff`, `execute_command` (e.g., `open index.html`).

## 6. Workflow Steps 🪜

*   **Step 1: Idea Spark & Vibe Check (Coordinator & Optional Delegate)**
    *   **Description:** Refine the User's loose concept into a clearer direction for design.
    *   **Inputs:** User's initial concept/idea.
    *   **Procedure (Coordinator):**
        *   Engage User via `ask_followup_question` to brainstorm keywords, desired feelings, visual styles (e.g., minimalist, retro, playful).
        *   Ask User for any optional inspirational images, links, or color palettes.
    *   **Procedure (Optional Delegation):**
        *   If needed, Coordinator uses `new_task` to delegate to `ask` or `design-ui`: "Generate mood board ideas or visual concepts based on these keywords/themes: [keywords/themes]".
    *   **Outputs:** A clearer direction: core themes, keywords, potential visual elements, optional mood board/concepts.
    *   **Error Handling:** If the concept remains too vague, Coordinator asks more targeted questions or suggests archetypes.

*   **Step 2: One-Shot Design & Code (Coordinator delegates to `one-shot-web-designer`)**
    *   **Description:** Generate the initial, fully coded version of the website.
    *   **Tool:** `new_task`
    *   **Inputs Provided by Coordinator:** Refined concept/vibe, keywords, themes, and any visual references from Step 1.
    *   **Instructions for Delegate (`one-shot-web-designer`):** "Create a visually striking, single-page website (HTML/CSS/JS) based on the following concept: [details from Step 1]. Prioritize capturing the '[vibe]' feel. Provide complete `index.html`, `style.css`, and `script.js` files."
    *   **Expected Output from Delegate:** Paths to the created `index.html`, `style.css`, `script.js` files.
    *   **Coordinator Action (Post-Delegation):** Verify file creation. Prepare for User review.
    *   **Error Handling:** If the delegate fails, Coordinator retries, potentially simplifying the prompt or clarifying the vibe. If persistent failure, consider `frontend-developer` as an alternative starting point.

*   **Step 3: Review & Iterate (Coordinator, User, Delegate)**
    *   **Description:** Review the initial website and iteratively refine it based on User feedback.
    *   **Inputs:** Initial coded website files (`index.html`, `style.css`, `script.js`), User feedback.
    *   **Procedure (Coordinator):**
        *   Present the initial website to the User (e.g., suggest `open index.html`).
        *   Use `ask_followup_question` to gather specific feedback: "What do you like? What needs refinement (layout, colors, interactions, content)?".
        *   Based on feedback, identify the required changes and select the appropriate specialist mode (`frontend-developer`, `tailwind-specialist`, `bootstrap-specialist`, or potentially `one-shot-web-designer` again for major redesigns).
    *   **Procedure (Delegation):**
        *   Coordinator uses `new_task` targeting the chosen specialist: "Apply the following refinements to the website files ([paths]): [Specific feedback/changes]. Use `read_file` to get current content and `apply_diff` or `write_to_file` to make changes."
    *   **Procedure (Iteration Loop):**
        *   Coordinator receives updated files from the delegate.
        *   Coordinator presents updated version to User.
        *   Repeat feedback and delegation cycle until User is satisfied.
    *   **Outputs:** Updated website files reflecting User feedback.
    *   **Error Handling:** If delegate introduces errors, Coordinator can delegate to `bug-fixer` or revert changes and try again with clearer instructions.

## 7. Postconditions ✅
*   Final, polished `index.html`, `style.css`, and `script.js` files are available.
*   The website functions correctly in a standard web browser.
*   User confirms satisfaction with the final result (meets `success_criteria`).

## 8. Error Handling & Escalation (Overall) ⚠️
*   Minor errors during iteration (Step 3) are handled by re-delegating with corrected instructions or engaging `bug-fixer`.
*   Persistent failure of `one-shot-web-designer` (Step 2) may require switching strategy to use `frontend-developer` for initial structure followed by styling.
*   If User feedback leads to significant scope creep beyond a simple one-pager, Coordinator should clarify if a different workflow is needed.
*   Refer to Adaptive Failure Resolution (`.ruru/processes/afr-process.md`) if standard retries fail.

## 9. PAL Validation Record 🧪
*   Date Validated: N/A
*   Method: N/A
*   Test Case(s): N/A
*   Findings/Refinements: N/A

## 10. Revision History 📜
*   v1.0 (2025-04-17): Initial draft conforming to standard template based on previous version.