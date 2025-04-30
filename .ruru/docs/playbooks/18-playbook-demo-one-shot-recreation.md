+++
# --- Metadata ---
id = "PLAYBOOK-DEMO-ONESHOT-V1"
title = "Capability Playbook: 'One-Shot' Website Recreation"
status = "draft" # Start as draft until tested
created_date = "2025-04-24"
updated_date = "2025-04-24"
version = "1.0"
tags = ["playbook", "documentation", "capability-demo", "design", "ui", "html", "css", "one-shot", "website-recreation", "visual-design", "epic", "feature", "task"]
related_docs = [
    ".ruru/docs/standards/project-management-strategy-v1.md",
    ".ruru/planning/project-structure/00-epic-feature-task-plan.md",
    ".ruru/modes/design-one-shot/design-one-shot.mode.md",
    ".ruru/modes/dev-general/dev-general.mode.md",
    ".ruru/modes/util-writer/util-writer.mode.md"
]
objective = "Guide the process of attempting to recreate the visual structure and styling of a given static website URL or image using the specialized `design-one-shot` mode, showcasing rapid visual prototyping capabilities."
scope = "Covers providing the target, setting up a basic page, delegating the core recreation task to `design-one-shot`, saving the output, and performing a brief review (with minimal refinement)."
target_audience = ["Users", "Designers", "Frontend Developers", "AI Modes"]
# --- Document Specific Fields ---
example_project_type = "Rapid Visual Prototyping / AI Design Capability Demo"
target_url_or_description_placeholder = "[Target Website URL or Detailed Visual Description]"
output_directory_placeholder = "[output_directory]" # e.g., "output/one-shot-demo"
+++

# Capability Playbook: "One-Shot" Website Recreation

This playbook demonstrates how Roo Commander can use the specialized `design-one-shot` mode to rapidly generate HTML and CSS attempting to visually replicate a given static website or design concept. The emphasis is on speed and visual fidelity in a single pass, not pixel-perfect replication or complex functionality.

**Scenario:** You want to quickly generate the HTML/CSS for a website based on its URL (`[Target Website URL]`) or a detailed description/image (`[Detailed Visual Description]`).

## Phase 1: Target Definition & Setup

1.  **Define the Recreation Goal (Epic/Feature):**
    *   **Goal:** Specify the target website/design to recreate and the objective of the demonstration.
    *   **Action:** Create a Feature (e.g., `.ruru/features/FEAT-210-oneshot-recreate-[target-name].md`).
    *   **Content:** Define `objective` (e.g., "Attempt a one-shot recreation of the visual layout and style of `[Target Website URL]` using `design-one-shot`."), include the `[Target Website URL or Detailed Visual Description]`. Set `status` to "Planned".

2.  **Gather Target Input (Coordinator Task):**
    *   **Goal:** Get the specific URL or visual description from the user.
    *   **Inputs:** User selected this playbook's related initial action.
    *   **Tool:** `ask_followup_question`
    *   **Procedure:**
        1.  Present prompt:
            ```xml
            <ask_followup_question>
             <question>Okay, let's try the 'One-Shot' recreation! Please provide EITHER:
             1. The **URL** of the static website you want to visually replicate.
             OR
             2. A **detailed description** of the visual design (layout, colors, fonts, key elements - if working from an image).
             Also, specify an output directory name (e.g., 'my-site-recreation').
             </question>
             <follow_up>
               <suggest>URL: [Enter Target URL], Output Dir: [Enter Dir Name]</suggest>
               <suggest>Description: [Describe Design], Output Dir: [Enter Dir Name]</suggest>
               <suggest>Cancel Recreation Demo</suggest>
             </follow_up>
            </ask_followup_question>
            ```
        2.  Await user response. Store as `[Target Input]` and `[Output Directory Name]`. Validate directory name is safe.
    *   **Outputs:** `[Target Input]` (URL or Description), `[Output Directory Name]`.
    *   **Error Handling:** Handle cancellation. Prompt again if input is unclear.

3.  **Basic Project Setup (Feature/Tasks):**
    *   **Goal:** Create the output directory and minimal placeholder files.
    *   **Action:** Define as a Feature (`FEAT-211-oneshot-setup.md`). Delegate tasks to `dev-general`.
    *   **Tasks (Examples):**
        *   "Create directory `[Output Directory Name]`." (`execute_command mkdir`)
        *   "Create empty file `[Output Directory Name]/index.html`." (`execute_command touch` or `New-Item` via Rule 05)
        *   "Create empty file `[Output Directory Name]/style.css`."
        *   *(Optional)* "Create directory `[Output Directory Name]/assets/images` if images are expected."
    *   **Process:** Use MDTM workflow. Mark Feature "Done". Set `[output_directory_placeholder]` path variable.

## Phase 2: One-Shot Generation

1.  **Delegate to `design-one-shot` (Coordinator Task - Core Step):**
    *   **Goal:** Task the specialist mode to perform the visual recreation.
    *   **Inputs:** `[Target Input]`.
    *   **Tool:** `new_task`
    *   **Procedure:**
        1.  Generate Task ID (`TASK-ONESHOT-...`). Log delegation.
        2.  Formulate message:
            ```xml
            <new_task>
              <mode>design-one-shot</mode>
              <message>
              🎨 One-Shot Recreation Task:
              Target: `[Target Input]` <!-- Either the URL or the detailed description -->
              Goal: Analyze the visual structure, layout, color palette, typography, spacing, and key elements of the target. Generate corresponding HTML (for structure) and CSS (for styling) to recreate the visual appearance of the target as closely as possible in a single attempt. Focus on static visual fidelity. Provide the generated HTML and CSS content separately in your result.
              Your Task ID: [Generated TASK-ONESHOT-... ID].
              Coordinator Task ID: [Coordinator's Task ID].
              </message>
            </new_task>
            ```
        3.  Await `attempt_completion`.
    *   **Outputs:** Result from `design-one-shot` containing generated HTML and CSS content.
    *   **Error Handling:** If `new_task` fails or `design-one-shot` reports failure (e.g., cannot access URL, description too vague), log error and report to user. **Stop.**

2.  **Write Output Files (Coordinator Task):**
    *   **Goal:** Save the generated HTML and CSS.
    *   **Inputs:** HTML and CSS content from `design-one-shot` result. `[output_directory_placeholder]`.
    *   **Tool:** `write_to_file` (x2)
    *   **Procedure:**
        1.  Execute: `<write_to_file><path>[output_directory_placeholder]/index.html</path><content>[HTML Content]</content></write_to_file>`
        2.  Await confirmation. Handle errors.
        3.  Execute: `<write_to_file><path>[output_directory_placeholder]/style.css</path><content>[CSS Content]</content></write_to_file>`
        4.  Await confirmation. Handle errors.
    *   **Outputs:** `index.html` and `style.css` populated with AI-generated content.

## Phase 3: Review & Optional Minimal Refinement

1.  **Manual Review (User Task):**
    *   **Goal:** Visually compare the generated page to the original target.
    *   **Action:** Instruct user: "I've saved the generated HTML and CSS to the `[Output Directory Name]` directory. Please open `[output_directory_placeholder]/index.html` in your web browser and compare it to the original `[Target Input]`. Remember, this is a 'one-shot' attempt focused on rapid visual prototyping."

2.  **Gather Feedback & Optional Refinement (Coordinator Task):**
    *   **Goal:** Allow for *one* specific, major correction if desired, maintaining the spirit of rapid generation.
    *   **Inputs:** User observation.
    *   **Tool:** `ask_followup_question`
    *   **Procedure:**
        1.  Ask:
            ```xml
            <ask_followup_question>
             <question>How does the 'one-shot' recreation look? Is it a useful starting point? Is there any single, major visual correction you'd like to attempt (understanding it might deviate from the 'one-shot' goal)?</question>
             <follow_up>
               <suggest>It's good enough for a demo!</suggest>
               <suggest>Request one specific adjustment...</suggest>
               <suggest>No adjustments needed.</suggest>
             </follow_up>
            </ask_followup_question>
            ```
        2.  **If** "Request adjustment": Prompt user for the *specific* change needed (e.g., "What specific CSS rule or HTML change is required?"). Delegate this *small, targeted* fix to `dev-general` or `design-tailwind` using `apply_diff` or `search_and_replace`.
        3.  **Else:** Proceed to Documentation.
    *   **Outputs:** Potentially slightly refined HTML/CSS.

## Phase 4: Documentation

1.  **Write README (Task):**
    *   **Goal:** Document the demo process and results.
    *   **Action:** Define Task. Delegate to `util-writer`.
    *   **Process:** Create `[output_directory_placeholder]/README.md`. Explain the goal (one-shot recreation), the `[Target Input]`, the modes used (`design-one-shot`), and include observations about the fidelity or limitations of the result. Suggest adding screenshots manually.

2.  **Final Completion:**
    *   **Action:** Mark the Feature/Epic as "Done". Inform the user the demo is complete.

## Key Considerations for "One-Shot" Recreation:

*   **Expectation Management:** This mode prioritizes speed and overall visual structure over pixel-perfect accuracy or complex interactivity. Manage user expectations accordingly.
*   **Static Focus:** The generated output will be primarily static HTML and CSS. JavaScript for interactivity is usually out of scope for `design-one-shot`.
*   **Image/Asset Handling:** The AI will likely *not* recreate complex images or download assets. It will focus on layout, color, and typography. Placeholder images might be used.
*   **Input Quality:** A clear, accessible URL or a very detailed visual description yields better results. Complex dynamic sites are poor targets.
*   **Refinement:** Keep refinement minimal to stay true to the "one-shot" concept. It's a starting point generator, not a full development process.

This playbook leverages the unique `design-one-shot` mode for rapid visual prototyping based on existing examples.