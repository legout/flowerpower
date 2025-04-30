+++
# --- Metadata ---
id = "PLAYBOOK-DEMO-DATAVIZ-V1"
title = "Capability Playbook: Interactive Data Visualization"
status = "draft"
created_date = "2025-04-24"
updated_date = "2025-04-24"
version = "1.0"
tags = ["playbook", "documentation", "capability-demo", "data-visualization", "d3js", "threejs", "frontend", "interactive", "epic", "feature", "task"]
related_docs = [
    ".ruru/docs/standards/project-management-strategy-v1.md",
    ".ruru/planning/project-structure/00-epic-feature-task-plan.md",
    ".ruru/modes/design-d3/design-d3.mode.md",
    ".ruru/modes/design-threejs/design-threejs.mode.md", # If 3D
    ".ruru/modes/agent-research/agent-research.mode.md" # For finding data/examples
]
objective = "Guide the creation of a compelling, interactive data visualization using relevant specialist modes like `design-d3`, showcasing Roo Commander's ability to handle complex frontend and data-driven tasks."
scope = "Covers finding inspiration/data, designing the visualization structure, implementing using a chosen library (e.g., D3.js), adding interactivity, and basic deployment."
target_audience = ["Users", "Developers", "Designers", "AI Modes"]
# --- Document Specific Fields ---
example_project_type = "Standalone Web Visualization or Embedded Chart"
viz_library_placeholder = "[VizLibrary]" # e.g., "D3.js", "Three.js", "Chart.js"
data_source_placeholder = "[DataSource]" # e.g., "Provided CSV", "Public API", "Generated Sample Data"
interaction_placeholder = "[InteractionType]" # e.g., "Tooltips on Hover", "Zoom and Pan", "Data Filtering Controls"
+++

# Capability Playbook: Interactive Data Visualization

This playbook demonstrates how Roo Commander can orchestrate the creation of sophisticated, interactive data visualizations, leveraging specialist AI modes.

**Scenario:** You want to build a specific data visualization (e.g., an animated force-directed graph, a choropleth map with hover effects, a 3D scatter plot) based on an idea, an existing example image/URL, or a dataset.

## Phase 1: Inspiration, Data & Setup

1.  **Define the Visualization Goal (Epic/Feature):**
    *   **Goal:** Clearly describe the desired visualization, its purpose, and the data it should represent.
    *   **Action:** Create an Epic or Feature (e.g., `.ruru/features/FEAT-150-interactive-world-map-viz.md`).
    *   **Content:** Provide a detailed `description` (e.g., "Create an interactive world map using D3.js showing population density. Countries should highlight on hover, displaying the country name and density value."), link to inspiration images/URLs, specify desired `[InteractionType]`. Set `status` to "Planned".

2.  **Acquire & Prepare Data (Feature/Tasks):**
    *   **Goal:** Obtain and format the data needed for the visualization.
    *   **Action:** Define as a Feature (`FEAT-151-prepare-visualization-data.md`). Delegate tasks based on data source.
    *   **Tasks (Examples):**
        *   "Find public dataset for [Data Needed, e.g., world population density by country] in CSV or JSON format." (Delegate to `agent-research`)
        *   "If data from API `[URL]` -> Implement script/function to fetch and format data as JSON." (Delegate to `util-senior-dev` or Backend specialist)
        *   "If using sample data -> Define JSON structure and generate realistic sample data for 20 countries." (Delegate to `util-senior-dev`)
        *   "Clean and format the final data into a suitable JSON structure (e.g., GeoJSON for maps, array of objects for charts) saved to `src/data/viz-data.json`." (Delegate to `data-specialist` or `util-senior-dev`)
    *   **Process:** Use MDTM workflow. Store final data within the project.

3.  **Project & Tooling Setup (Feature/Tasks):**
    *   **Goal:** Set up a basic frontend project environment to host the visualization.
    *   **Action:** Define as a Feature (`FEAT-152-visualization-project-setup.md`).
    *   **Tasks (Examples - Delegate to `lead-frontend`, `util-vite`):**
        *   "Initialize basic frontend project (e.g., using Vite with Vanilla JS/TS or a framework)."
        *   "Install `[VizLibrary]` dependency (e.g., `d3`, `three`, `chart.js`)."
        *   "Set up basic HTML (`index.html`) with a container element for the visualization."
        *   "Create main JavaScript/TypeScript file (`main.js`/`ts`) to load data and initialize the visualization."

## Phase 2: Implementation & Interactivity

1.  **Implement Core Visualization Structure (Feature/Tasks):**
    *   **Goal:** Render the basic static visualization using the prepared data.
    *   **Action:** Define as a Feature (`FEAT-153-implement-base-[VizLibrary]-structure.md`). Delegate heavily to the relevant specialist (`design-d3`, `design-threejs`).
    *   **Tasks (Examples - D3.js Map):**
        *   "Load GeoJSON world map data and `viz-data.json`."
        *   "Set up SVG canvas and projection."
        *   "Draw map paths (countries) using GeoJSON data."
        *   "Implement color scale based on population density data."
        *   "Apply color scale fill to country paths."
        *   "Add a basic legend for the color scale."
    *   **Process:** Use MDTM workflow. Provide the Data Feature (`FEAT-151`) and Design Feature (`FEAT-150`) as context. The specialist mode will write the core visualization code.

2.  **Implement Interactivity (Feature/Tasks):**
    *   **Goal:** Add the specified interactive elements (`[InteractionType]`).
    *   **Action:** Define as a Feature (`FEAT-154-add-[InteractionType]-to-viz.md`). Delegate to the visualization specialist (`design-d3`, `design-threejs`).
    *   **Tasks (Examples - D3.js Tooltips):**
        *   "Add mouseover event listeners to country paths."
        *   "On mouseover, display a tooltip (create tooltip div if needed) showing country name and density value."
        *   "Implement logic to position the tooltip near the cursor."
        *   "Add mouseout event listener to hide the tooltip."
        *   "Apply visual highlighting (e.g., change stroke color/width) to the hovered country path."
        *   "Remove highlight on mouseout."
    *   **Process:** Use MDTM workflow. Build upon the code from the previous feature.

3.  **Styling & Refinement (Feature/Tasks):**
    *   **Goal:** Improve the visual appearance and polish the interactions.
    *   **Action:** Define as a Feature (`FEAT-155-visualization-styling-polish.md`). Delegate to `design-d3`/`design-threejs` or `design-tailwind`/`design-ui`.
    *   **Tasks (Examples):**
        *   "Refine color scheme and legend appearance."
        *   "Add smooth transitions for hover effects."
        *   "Style tooltips."
        *   "Ensure visualization is responsive (if required)."

## Phase 3: Testing & Documentation

1.  **Cross-Browser/Device Testing (Manual or Automated):**
    *   **Goal:** Ensure the visualization renders and functions correctly in target environments.
    *   **Action:** Define testing tasks. Manual testing is common for complex viz. E2E tests (`test-e2e` with visual regression) are possible but complex to set up.

2.  **Documentation (README):**
    *   **Goal:** Explain the visualization, data source, and how to run it.
    *   **Action:** Define Task. Delegate to `util-writer`.
    *   **Process:** Create/update `README.md` explaining the demo, data source, setup, and how to view it. Include a screenshot or GIF if possible.

3.  **Final Review & Epic/Feature Completion:**
    *   **Action:** Review the final visualization. Mark Features and the parent Epic as "Done".

## Key Considerations for Visualization Demos:

*   **Data:** The quality and format of the input data are critical. Phase 1, Step 2 is often the most challenging.
*   **Library Choice:** Select the right library (`[VizLibrary]`) for the job (D3 for complex custom SVG/Canvas, Chart.js for standard charts, Three.js for 3D, etc.).
*   **Performance:** Complex visualizations with large datasets can be demanding. Consider optimization techniques (data aggregation, efficient rendering, debouncing events) if performance is an issue (`util-performance`).
*   **Iteration:** Visualization development is often highly iterative. Expect back-and-forth between implementation, styling, and interaction refinement. Use Storybook if building reusable viz components.
*   **Clarity:** The primary goal is often to communicate data effectively. Ensure labels, tooltips, legends, and interactions aid understanding.

This playbook provides a roadmap for leveraging Roo Commander and its specialist modes to create impressive interactive data visualizations.