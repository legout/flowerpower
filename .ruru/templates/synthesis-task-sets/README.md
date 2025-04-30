# Synthesis Task Set Templates (`.ruru/templates/synthesis-task-sets/`)

This directory contains TOML files that define sets of AI synthesis tasks tailored for specific types of software libraries or frameworks. The KB enrichment pipeline uses these definitions to guide the `agent-context-synthesizer` mode.

## File Naming Convention

*   Files should be named `[library_type]-tasks.toml` (e.g., `ui-library-tasks.toml`, `backend-framework-tasks.toml`).
*   Use lowercase, hyphenated library type names.
*   A `generic-tasks.toml` file **must** exist as a fallback for libraries whose type is not explicitly mapped or defined.

## TOML File Structure Standard

Each `.toml` file **must** adhere to the following structure:

```toml
# TOML definition for synthesis tasks for a specific library type.

# Required: Identifies the type this task set applies to. Matches the key used in library-types.json.
library_type = "example-type" # e.g., "ui-library", "backend-framework", "generic"

# Required: An array of task tables. Each table defines one synthesis task.
[[tasks]]
  # Required: Unique identifier for this task within the set. (e.g., "core_concepts", "component_props_summary")
  task_id = "task_identifier_1"

  # Required: Human-readable description of the task's goal.
  description = "Generate an overview of core concepts and principles."

  # Required: List of source KB category directory names to use as input for this task.
  # The synthesizer will read all .md files from these categories within the library's source KB.
  input_categories = ["guide", "concepts", "about"]

  # Required: The base filename for the synthesized output markdown file.
  # It will be saved in `.ruru/modes/{mode_slug}/kb/{library_name}/synthesized/`.
  output_filename = "core-concepts-summary.md"

  # Required: Specific instructions/prompt focus for the agent-context-synthesizer mode.
  # This tells the AI *what* to focus on when reading the input files for this specific task.
  prompt_focus = "Identify and explain the fundamental ideas, design philosophy, and main features based *only* on the provided input files. Aim for a conceptual overview."

[[tasks]]
  task_id = "setup_info"
  description = "Summarize installation and basic configuration."
  input_categories = ["guide", "config", "installation", "start"]
  output_filename = "setup-summary.md"
  prompt_focus = "Extract the essential steps for installation and initial setup, focusing on the most common path described in the input files."

# Add more [[tasks]] tables as needed for this library type.
```

**Fields Explained:**

*   **`library_type` (String, Required):** Must match a type defined in `.ruru/config/library-types.json`.
*   **`[[tasks]]` (Array of Tables, Required):** Defines one or more synthesis tasks.
    *   **`task_id` (String, Required):** A unique machine-readable ID for the task (e.g., `api_overview`).
    *   **`description` (String, Required):** A brief explanation of what this task aims to achieve.
    *   **`input_categories` (Array of Strings, Required):** List of category directory names (from the *initial* KB structure, e.g., `kb/[library_name]/[category]`) that should serve as source material for this synthesis task.
    *   **`output_filename` (String, Required):** The name of the markdown file the synthesizer should create in the target mode's `kb/[library_name]/synthesized/` directory.
    *   **`prompt_focus` (String, Required):** The core instruction given to the `agent-context-synthesizer` for this specific task, guiding its analysis and generation focus.

## Creating New Task Sets

1.  Identify a new library type (e.g., "database-orm").
2.  Create a new file named `[type]-tasks.toml` (e.g., `database-orm-tasks.toml`) in this directory.
3.  Define the `library_type` key at the top.
4.  Add one or more `[[tasks]]` tables, carefully defining the `task_id`, `description`, appropriate `input_categories`, a clear `output_filename`, and a specific `prompt_focus` for each task relevant to that library type.
5.  Ensure the new library type is added to the mapping in `.ruru/config/library-types.json`.