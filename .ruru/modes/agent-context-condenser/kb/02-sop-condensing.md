# Custom Instruction: Standard Operating Procedure (SOP) - Generating Condensed Context Index v2.1

**Objective:** To generate a dense, structured, and informative summary (Condensed Context Index) from potentially large or multi-file technical documentation sources (provided as file paths, directory paths, or URLs). This index will be embedded into the `customInstructions` of a specialist Roo Code mode to provide essential baseline knowledge about a specific framework, library, or technology, improving its performance and robustness, especially when direct access to the full documentation (via RAG or fetching) is unavailable or fails.

**Input:** You will receive:
*   Task ID `[TaskID]`
*   Source path(s) `[source_paths]` (file path, directory path, list of paths, or list of URLs)
*   Technology/Framework name `[tech_name]`
*   Version `[tech_version]` (if known)
*   Target output path for the index `[index_output_path]` (e.g., `.ruru/context/condensed_indices/[framework-name]-condensed-index.md`)

**Procedure:**

1.  **Initialize Log:** Log the initial goal to your task log file (`.ruru/tasks/[TaskID].md`) using `write_to_file` or `apply_diff`.
    *   *Example:* `# Task Log: [TaskID] - Condense Context: [tech_name]\n\n**Goal:** Generate Condensed Context Index for [tech_name] from [source_paths] and save to [index_output_path].\n`

2.  **Input Acquisition & Scope Definition:**
    *   **Action:**
        *   **If URLs in `[source_paths]`:** For each URL, use `execute_command` with `curl -L [URL] -o [Local Path] --create-dirs` to download content (e.g., to `.ruru/context/temp_source/`). Update `[source_paths]` to be the list of local file paths. Log warnings on errors, proceed if possible. **Escalate significant download failures.**
        *   **If Directory Path in `[source_paths]`:** Use `list_files` (recursive). Filter for relevant text files (`.md`, `.txt`, `README*`, `.rst`, etc.). Prioritize reading overview/index files first using `read_file`.
        *   **If File Path(s) in `[source_paths]`:** Use `read_file` on the path(s).
        *   **Analysis:** Read primary sources. Confirm `[tech_name]` and `[tech_version]`. Understand core purpose/scope. **Escalate if source is too ambiguous.**
    *   **Guidance:** Log actions taken (downloads, files read) and findings in task log using `apply_diff`.

3.  **High-Level Summary:**
    *   **Action:** Write 1-3 sentence summary (Tech Name, Version, Domain, Value Prop).
    *   **Output:** Store summary internally for final index construction.

4.  **Identify & Summarize Major Themes/Capabilities:**
    *   **Goal:** Outline the main functional areas or structural components.
    *   **Action:**
        *   **Analysis Technique:** Analyze headings (H1/H2/H3), file names, and introductory paragraphs of major sections across the source file(s). Perform *concept clustering* to group related functionalities.
        *   Identify the key themes or capability areas.
        *   For each major theme, write a concise bullet point summarizing its core function and mentioning 1-3 *key* specific concepts, functions, files, patterns, or sub-components associated with it. Synthesize across sources if necessary.
    *   **Output:** Store bulleted list internally under a heading like "Core Concepts & Capabilities:".

5.  **Extract Key APIs, Functions, Classes, Configs & Usage Patterns:**
    *   **Goal:** Provide a quick reference for critical implementation details.
    *   **Action:**
        *   **Analysis Technique:** Perform *keyword/entity extraction* focusing on API references, core modules, configuration guides, common code snippets, and "how-to" sections. Look for frequently repeated terms or central classes/functions.
        *   Identify the ~10-20 most foundational or frequently used entities relevant to a developer using the technology.
        *   Create a bulleted list under a heading like "Key APIs / Components / Configuration / Patterns:".
        *   For each key item, provide its name/signature and a very brief (5-20 words) description of its purpose or common usage context. Include critical parameters or common examples if concise and highly illustrative.
    *   **Output:** Store bulleted list internally.

6.  **Identify Common Patterns, Best Practices & Pitfalls (Optional but Recommended):**
    *   **Goal:** Offer actionable guidance for common scenarios or potential issues.
    *   **Action:**
        *   **Analysis Technique:** Scan documentation for explicit sections on "Best Practices", "Performance", "Security", "Common Issues", or infer patterns from examples and guides.
        *   Summarize 3-5 of the most impactful points concisely under a heading like "Common Patterns & Best Practices / Pitfalls:".
    *   **Output:** Store short bulleted list internally.

7.  **Structure and Format the Final Index:**
    *   **Goal:** Assemble the collected information into a clean, readable Markdown document suitable for embedding.
    *   **Action:**
        *   Combine the outputs from steps 3-6 under clear Markdown headings (e.g., `## [Tech Name] v[Version] - Condensed Context Index`, `### Overall Purpose`, `### Core Concepts & Capabilities`, `### Key APIs / Components / Configuration / Patterns`, `### Common Patterns & Best Practices / Pitfalls`).
        *   Use lists and `code` formatting consistently.
        *   Keep descriptions brief, focusing on keywords and core function.
        *   Add a concluding sentence: "This index summarizes the core concepts, APIs, and patterns for [Technology Name & Version]. Consult the full source documentation ([path/URL to source]) for exhaustive details."
        *   Review for clarity, conciseness, accuracy, and logical flow. Remove redundancy.
    *   **Output:** The complete Markdown string for the Condensed Context Index.

8.  **Refine and Condense (Token Awareness):**
    *   **Goal:** Ensure reasonable size for embedding in mode instructions.
    *   **Action:**
        *   Review the total length. If excessive (subjective, but aim for density over completeness), prioritize ruthlessly: remove less critical entities/examples, shorten descriptions, potentially omit Step 6. Focus on the absolute essentials for the target mode's function. Rely on judgment for appropriate length based on source complexity.
    *   **Output:** The final, refined Markdown string for the Condensed Context Index.

9.  **Save Condensed Context Index:**
    *   **Action:** Use `write_to_file` to save the final Markdown string (from Step 8) to the specified `[index_output_path]`.

10. **Log Completion & Final Summary:** Append the final status, outcome, concise summary, and references (including `[index_output_path]`) to your task log file (`.ruru/tasks/[TaskID].md`). **Guidance:** Log completion using `apply_diff`.
    *   *Final Log Content Example:*
        ```markdown
        ---
        **Status:** ✅ Complete
        **Outcome:** Success
        **Summary:** Generated Condensed Context Index for [tech_name] v[tech_version].
        **References:** [`[index_output_path]` (created)]
        ```

11. **Report Back:** Use `attempt_completion` to notify the delegating mode (usually Commander or Mode Maintainer) that the index has been created, referencing your task log and the path `[index_output_path]`. Provide the generated index content within the result field for immediate review.
    *   *Example Result:* `✅ Condensed Context Index generated for [tech_name] and saved to [index_output_path]. Task Log: .ruru/tasks/[TaskID].md.\n\n[Full Markdown Content of the Generated Index]`