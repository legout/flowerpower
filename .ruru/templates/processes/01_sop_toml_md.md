+++
# --- Basic Metadata ---
title = "SOP: [Process Title]"
status = "Draft" # Draft | Active | Deprecated
version = "0.1"
created_date = "[YYYY-MM-DD]" # Optional: Add current date if needed
updated_date = "[YYYY-MM-DD]" # Optional: Add current date if needed
authors = ["[Author Name(s)]"]

# --- Document Type Specific Fields (Process/SOP) ---
objective = "Clearly state the primary goal of this SOP. What specific task or activity does it govern? What is the intended outcome?"
scope = "Define the boundaries of this process. When does it apply? What situations are explicitly *out* of scope?"
applicability = ["[Role Name 1]", "[Role Name 2]"] # Roles expected to follow this procedure

# --- Inputs & Outputs ---
prerequisites = [
    "List any necessary conditions, tools, permissions, or information required *before* starting this process.",
    "Example: Node.js installed",
    "Example: Access to `v7.1/modes/` directory",
]
inputs = [
    "List the specific data, files, or parameters needed to execute the process.",
    "Example: Path to source mode file",
    "Example: Target directory path",
]
outputs = [
    "List the specific files, data, or state changes produced by successfully completing this process.",
    "Example: Updated `.mode.md` file",
    "Example: Confirmation message to user",
]

# --- Context & Relationships ---
related_documents = [
    "[Link to relevant spec, rule, or other process]",
    ".ruru/processes/pal-process.md", # Process Assurance Lifecycle
]
# script_path = ".path/to/relevant/script.sh" # Optional: If the SOP primarily documents a script
tags = ["sop", "[domain]", "[task-type]"] # Add relevant tags for categorization

+++

# SOP: [Process Title]

## 1. Objective 🎯

*   [Copy/Elaborate on `objective` from TOML]

## 2. Scope & Applicability 🌐

*   [Copy/Elaborate on `scope` from TOML]
*   **Applicable Roles:** [Copy/Elaborate on `applicability` from TOML]

## 3. Prerequisites ✅

*   [Copy/Elaborate on `prerequisites` from TOML]

## 4. Inputs 📥

*   [Copy/Elaborate on `inputs` from TOML]

## 5. Roles & Responsibilities 👥

*   **[Role Name 1]**: Responsibilities...
*   **[Role Name 2]**: Responsibilities...
*   *(Clearly define who performs which steps)*

## 6. Process Steps 🚀

1.  **Step 1: [Action Description]**
    *   **Actor:** [Role Name]
    *   **Details:** Provide specific instructions. Mention tools (`read_file`, `execute_command`, `new_task`, etc.) and specific commands/parameters if applicable. Reference `script_path` from TOML if relevant.
    *   **Context (If Delegating):** Specify exactly what information/paths must be passed.
    *   **Output/Confirmation:** What is the expected result of this step?
2.  **Step 2: [Action Description]**
    *   **Actor:** [Role Name]
    *   **Details:** ...
    *   **Context (If Delegating):** ...
    *   **Output/Confirmation:** ...
3.  **Step 3: [Decision Point - Example]**
    *   **Actor:** [Role Name]
    *   **Condition:** If [Condition X] is true...
    *   **Action:** Proceed to Step 4.
    *   **Condition:** Else...
    *   **Action:** Proceed to Step 5.
4.  **Step 4: ...**
    *   ...

*(Continue numbering steps sequentially)*

## 7. Outputs / Artifacts 📦

*   [Copy/Elaborate on `outputs` from TOML]

## 8. Error Handling & Escalation ⚠️

*   Describe how to handle common errors or failure points within the process.
*   Specify escalation paths (e.g., "Report error to Coordinator", "Trigger AFR process if pattern detected", "Ask user for clarification via `ask_followup_question`").

## 9. Important Notes / Considerations 🤔

*   Include any additional context, warnings, or best practices relevant to this process.
*   Reference `related_documents` from TOML where appropriate.