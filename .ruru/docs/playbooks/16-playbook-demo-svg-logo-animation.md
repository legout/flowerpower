+++
# --- Metadata ---
id = "PLAYBOOK-DEMO-SVG-ANIM-V1"
title = "Capability Playbook: Dynamic SVG Logo Animation"
status = "draft" # Start as draft until tested
created_date = "2025-04-24"
updated_date = "2025-04-24"
version = "1.0"
tags = ["playbook", "documentation", "capability-demo", "svg", "animation", "animejs", "frontend", "interactive", "logo", "epic", "feature", "task"]
related_docs = [
    ".ruru/docs/standards/project-management-strategy-v1.md",
    ".ruru/planning/project-structure/00-epic-feature-task-plan.md",
    ".ruru/modes/design-animejs/design-animejs.mode.md",
    ".ruru/modes/dev-general/dev-general.mode.md",
    ".ruru/modes/util-refactor/util-refactor.mode.md"
]
objective = "Guide the process of taking an existing SVG logo file and creating a complex, engaging animation for it (e.g., for loading states or user interaction) using `design-animejs`, showcasing fine-grained control over vector graphics."
scope = "Covers SVG preparation, animation concept definition, implementation with anime.js, triggering mechanisms, and refinement."
target_audience = ["Users", "Frontend Developers", "Designers", "AI Modes"]
# --- Document Specific Fields ---
example_project_type = "Website Element Enhancement / Brand Animation"
svg_file_placeholder = "[path/to/logo.svg]"
animation_type_placeholder = "[Loading|Hover|Scroll|Click]" # e.g., Loading, Hover, Scroll
animation_concept_placeholder = "[Detailed Animation Description]" # e.g., "Paths draw in sequentially, then the main icon pulses gently"
+++

# Capability Playbook: Dynamic SVG Logo Animation

This playbook demonstrates how Roo Commander can manage the creation of sophisticated animations for SVG logos, utilizing the `design-animejs` specialist.

**Scenario:** You have a static SVG logo file (`[svg_file_placeholder]`) and want to create a complex `[Animation Type]` animation for it, following a specific concept (`[Animation Concept Description]`).

## Phase 1: Preparation & Setup

1.  **Define the Animation Goal (Epic/Feature):**
    *   **Goal:** Clearly define the objective, the target SVG, the type of animation, and the desired visual effect.
    *   **Action:** Create an Epic or Feature (e.g., `.ruru/features/FEAT-180-animate-logo-svg.md`).
    *   **Content:** Set `objective` (e.g., "Create an engaging loading animation for the company logo SVG"). Include the `[svg_file_placeholder]`. Describe the high-level `[Animation Concept Description]`. Set `status` to "Planned".

2.  **SVG Analysis & Preparation (Feature):**
    *   **Goal:** Ensure the SVG is structured correctly for animation targeting (elements need IDs or specific classes).
    *   **Action:** Define as a Feature (`FEAT-181-prepare-logo-svg-for-animation.md`). Requires user input for the SVG path.
    *   **Tasks (Examples - Delegate to `dev-general`, possibly `design-diagramer` if it can parse/modify SVG structure):**
        *   "User provides path to the logo SVG: `[svg_file_placeholder]`." (Coordinator prompts user).
        *   "Read the content of `[svg_file_placeholder]`." (`read_file`).
        *   "Analyze SVG structure: Identify key elements (`<path>`, `<g>`, `<circle>`, etc.) that need independent animation." (Can be AI task or human review).
        *   **"CRITICAL:** Ensure target elements have unique IDs or appropriate classes. If not, use `<search_and_replace>` or delegate to `dev-general` to add them (e.g., `<path id='logo-path-1'>`, `<g class='logo-icon-group'>`). Update the SVG file." **(This step is essential for `anime.js` targeting)**.
        *   *(Optional)* "Optimize the SVG file (e.g., using SVGO tool via `execute_command` if available, or manually)."
    *   **Process:** Use MDTM workflow. Store the path to the *prepared* SVG. Mark Feature "Done".

3.  **Basic Web Page Setup (Feature):**
    *   **Goal:** Create a minimal HTML/CSS/JS environment to develop and view the animation.
    *   **Action:** Define as a Feature (`FEAT-182-svg-animation-dev-setup.md`). Delegate tasks to `dev-general`.
    *   **Tasks (Examples):**
        *   "Create `index.html`."
        *   "Embed the prepared SVG inline within the HTML body or load via JS." (Embedding inline is often easier for `anime.js` targeting).
        *   "Create basic `style.css` for layout/visibility."
        *   "Create `script.js` and link it."
        *   "Install `anime.js` dependency (`npm install animejs`) or add CDN link." (Coordinator via `execute_command`).

## Phase 2: Animation Implementation

1.  **Refine Animation Concept (Task within Epic/Feature):**
    *   **Goal:** Translate the high-level concept into a specific sequence/timeline.
    *   **Action:** Primarily **User-driven creative input**, potentially aided by suggestions from `design-animejs`.
    *   **Process:**
        *   Coordinator uses `ask_followup_question` with user: "Based on the concept '[Animation Concept Description]' and the SVG structure (elements: [list IDs/classes from prepared SVG]), can you describe the sequence? e.g., '1. Draw path-1 over 500ms. 2. Then fade in icon-group over 300ms. 3. Then pulse icon-group scale slightly...'".
        *   *(Optional)* Delegate to `design-animejs`: "Suggest an `anime.js` timeline structure for animating elements [IDs/classes] in SVG `[svg_file_placeholder]` based on the concept '[Animation Concept Description]'."
        *   Document the finalized sequence/timeline details in the main Feature (`FEAT-180`). Update status to "Ready for Dev".

2.  **Implement Core Animation (Feature/Tasks):**
    *   **Goal:** Write the `anime.js` code to execute the defined animation sequence.
    *   **Action:** Define as a Feature (`FEAT-183-implement-logo-animation-sequence.md`) or break into tasks under FEAT-180. Delegate heavily to `design-animejs`.
    *   **Tasks (Examples):**
        *   "In `script.js`, use `anime.timeline({...})` to orchestrate the sequence."
        *   "Add animation step for element `#logo-path-1` using `strokeDashoffset` for drawing effect." (Pass target, properties, duration, easing from concept).
        *   "Add animation step for element `.logo-icon-group` using `opacity` and `scale`." (Pass details).
        *   "Configure overall timeline properties (looping, direction, etc.)."
    *   **Process:** Use MDTM workflow. Provide the *prepared* SVG structure/content and the finalized animation sequence from Step 1 as context. `design-animejs` writes JavaScript code using `anime.js` API.

3.  **Implement Animation Trigger (Feature/Tasks - If not simple loading):**
    *   **Goal:** Add logic to start the animation based on the desired `[Animation Type]` (Hover, Scroll, Click).
    *   **Action:** Define as a Feature (`FEAT-184-implement-logo-animation-trigger.md`). Delegate to `design-animejs` or `dev-general`.
    *   **Tasks (Examples):**
        *   *(Hover)* "Add `mouseenter`/`mouseleave` event listeners to the SVG container to play/reverse the animation timeline."
        *   *(Click)* "Add `click` event listener to play the animation."
        *   *(Scroll)* "Use `IntersectionObserver` to detect when the logo enters the viewport and trigger the animation."
    *   **Process:** Use MDTM workflow. Modify `script.js`.

## Phase 3: Refinement & Testing

1.  **Tuning & Polishing (Tasks):**
    *   **Goal:** Adjust timing, easing, delays, and visual details for optimal effect.
    *   **Action:** Iterative process involving User feedback and delegation back to `design-animejs`.
    *   **Process:** User reviews the animation in `index.html`. Provides feedback like "Make the first part faster", "Use an 'easeOutExpo' easing". Coordinator creates tasks for `design-animejs` to adjust parameters in `script.js`.

2.  **Cross-Browser Testing (Tasks):**
    *   **Goal:** Ensure consistent animation behavior across target browsers.
    *   **Action:** Mostly manual testing by User. Define tasks if specific browser issues are found.
    *   **Process:** Test in Chrome, Firefox, Safari, Edge. Note any jerky movements, rendering glitches, or timing issues. Create bug-fix tasks (`dev-fixer` or `design-animejs`).

## Phase 4: Documentation & Integration Prep

1.  **Refactor for Reusability (Optional Task):**
    *   **Goal:** Package the animation logic into a clean function or component.
    *   **Action:** Delegate to `util-refactor` or `design-animejs`.
    *   **Process:** Encapsulate the `anime.js` code and potentially the SVG embedding into a reusable JavaScript function or framework component.

2.  **Documentation (README/Usage Guide):**
    *   **Goal:** Explain how to use the animated logo.
    *   **Action:** Define Task. Delegate to `util-writer`.
    *   **Content:** Create/update `README.md` for the animation component/project. Explain how to include it, trigger it (if interactive), and any configuration options.

3.  **Final Review & Completion:**
    *   **Action:** Review the final animation and documentation. Mark Features and the parent Epic as "Done".

## Key Considerations for SVG Animation:

*   **SVG Structure:** The *most critical* prerequisite. SVGs from design tools often lack the necessary IDs or logical grouping (`<g>`) for easy animation targeting. Preparation (Phase 1, Step 2) is essential.
*   **Performance:** Complex SVGs with many elements or intricate path animations can impact performance. Optimize the SVG itself and keep `anime.js` targets specific. Use browser performance profiling tools if needed.
*   **Targeting Methods:** `anime.js` can target elements using CSS selectors (IDs, classes), direct DOM element references, or NodeLists. Inline SVGs usually make targeting easier.
*   **Animation Libraries:** While `anime.js` is specified, other libraries like GSAP exist. The core principles remain similar.
*   **Creative Iteration:** Animation is often subjective. Expect iterative refinement based on visual feedback.

This playbook provides a structured path for creating dynamic SVG animations, highlighting the necessary preparation, the role of the `design-animejs` specialist, and the iterative nature of creative development.