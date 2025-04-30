+++
# --- Basic Metadata ---
id = "WF-MODE-KB-ENRICHMENT-002"
title = "Workflow: Enhanced Mode Knowledge Base Enrichment (v2.4)" # Updated Title
status = "draft"
created_date = "2025-04-26"
updated_date = "2025-04-27"
version = "2.4" # Updated Version
tags = [
    "workflow", "kb-enrichment", "ai-synthesis", "modes", "pipeline", "documentation",
    "sop", "context-handling", "json-context", "mcp-preference", "synthesis-templates",
    "ai-assessment", "kb-granularity", "subfolders", "existing-mode", "context-source",
    "workspace", "url", "vertex-ai", "web-crawl" # Removed tags
]

# --- Ownership & Context ---
owner = "Roo Commander"
related_docs = [
    ".ruru/workflows/WF-MODE-KB-ENRICHMENT-001.md", # Previous version
    ".ruru/workflows/WF-NEW-MODE-CREATION-004.md", # Reference for improvements
    ".ruru/planning/mode-kb-enrichment-strategy/00-strategy-overview.md",
    ".ruru/config/library-types.json",
    ".ruru/templates/synthesis-task-sets/README.md",
    ".roo/rules/01-standard-toml-md-format.md",
    ".roo/rules/04-mdtm-workflow-initiation.md",
    ".roo/rules/08-logging-procedure-simplified.md",
    ".roo/rules/10-vertex-mcp-usage-guideline.md",
    ".ruru/processes/acqa-process.md",
    ".ruru/processes/afr-process.md",
    ".ruru/processes/pal-process.md"
]
related_templates = [
    ".ruru/templates/synthesis-task-sets/" # Directory containing task set definitions
]

# --- Workflow Specific Fields ---
objective = "Define the enhanced step-by-step procedure for enriching an *existing* specialist mode's knowledge base (KB) with AI-synthesized context derived from various sources (workspace files/folders, URLs, MCPs). Incorporates AI assessment, structured synthesis via templates, JSON context handling, user options for KB structure, and MCP tool preference." # Updated Objective (Removed Context7)
scope = "Covers the end-to-end process for enriching an *existing* mode's KB. Allows user to select context source type (Workspace Folder/File, Vertex AI MCP, Web Crawl URL, Manual). Handles source acquisition based on type. Includes optional context gathering, optional AI assessment, structured synthesis using templates, saving context to JSON, user prompts for KB structure, populating synthesized files (potentially in subfolders), updating KB indexes and README, ensuring KB usage strategy exists, updating mode definition context, QA, user review, and cleanup. Prefers MCP tools with fallbacks." # Updated Scope (Removed Context7)
roles = [
    "User", "Coordinator (Roo Commander)", "Context Gatherer (e.g., agent-research)",
    "Context Synthesizer (e.g., agent-context-condenser)",
    "Mode Structure Agent (e.g., mode-maintainer, technical-writer, toml-specialist)",
    "QA Agent (e.g., code-reviewer)",
    "Web Crawler Agent (e.g., spec-firecrawl, spec-crawl4ai)"
]
trigger = "Manual initiation by Roo Commander or User for a specific library and target *existing* mode."
success_criteria = [
    "Target mode's KB contains synthesized documents for the specified library in the `kb/[library_name]/synthesized/` subdirectory (potentially within further subfolders).",
    "Target mode's KB includes an updated library-specific `kb/[library_name]/index.toml`.", # Updated criteria (Removed Context7)
    "Target mode's master `kb/index.toml` is updated with the library entry.",
    "Target mode's KB README (`kb/README.md`) is updated with the new synthesized files.",
    "Target mode has an internal KB usage strategy document (`kb/00-kb-usage-strategy.md`).",
    "Target mode's configuration (`.mode.md`) references the library KB index (`kb/[library_name]/index.toml`) in `related_context`.", # Updated criteria (Removed Context7)
    "The temporary context file (`.ruru/temp/kb-enrichment-context-[mode_slug]-[library_name].json`) is deleted.",
    "Any temporary downloaded/crawled source files are deleted.",
    "The enriched structure passes Quality Assurance (QA) review.",
    "User confirms the enrichment meets initial requirements."
]
failure_criteria = [
    "Failure to acquire or verify source data based on selected type.", # Updated criteria (Removed Context7)
    "Failure during optional context gathering or AI assessment.",
    "Failure to load synthesis task set.",
    "Critical failure during AI synthesis task execution.",
    "Failure saving/reading/parsing temporary JSON context file (if used).",
    "Failure during KB population (creating files/subdirs).", # Updated criteria (Removed Context7 script)
    "Failure to generate valid or complete index files or KB README.",
    "Failure to update mode configuration or ensure usage strategy document exists.",
    "Synthesized content fails validation/QA checks.",
    "User rejects the final enrichment."
]

# --- Integration ---
acqa_applicable = true # Requires ACQA review
pal_validated = false # Needs validation for v2.3
validation_notes = ""

# --- AI Interaction Hints (Optional) ---
context_type = "workflow_definition"
+++

# Workflow: Enhanced Mode Knowledge Base Enrichment (v2.4)

## 1. Objective 🎯

To define the enhanced step-by-step procedure for enriching an **existing** specialist mode's knowledge base (KB) with AI-synthesized context derived from various sources (workspace files/folders, URLs, MCPs). This workflow incorporates:
*   User selection of the primary context source.
*   User preferences for additional context gathering and AI assessment.
*   Structured synthesis using predefined task templates.
*   Intermediate context storage using a temporary JSON file.
*   User options for KB structure (single folder vs. subfolders) based on assessment.
*   Preference for MCP tools with robust fallbacks.
*   QA and user review steps.

## 2. Scope ↔️

This workflow covers the end-to-end process for enriching an **existing** mode's KB. It allows the user to select the primary context source type:
*   **Workspace Folder:** Reads all `.md` files within a specified workspace folder.
*   **Workspace File:** Reads a single specified workspace file.
*   **Vertex AI MCP:** Leverages Vertex AI tools (e.g., `save_topic_explanation`) for context generation.
*   **Web Crawl URL:** Uses a crawling agent (e.g., Firecrawl) to extract content from a general URL.
*   **Specify Manually / Other:** Allows for custom handling or clarification.

It handles source acquisition based on the selected type. It includes optional context gathering, optional AI assessment, structured synthesis using templates, saving context to JSON, user prompts for KB structure, populating synthesized files (potentially in subfolders), updating KB indexes and README, ensuring KB usage strategy exists, updating mode definition context, QA, user review, and cleanup. Prefers MCP tools with fallbacks.

## 3. Roles & Responsibilities 👤

*   **User:** Initiates or confirms the request, provides target mode slug and library name, selects context source type and details, selects context/assessment preferences, reviews KB structure options, and confirms final enrichment.
*   **Coordinator (Roo Commander):** Orchestrates the workflow, interacts with the User, delegates tasks, performs QA, manages temporary context file, and manages finalization steps.
*   **Context Gatherer:** (Worker Agent, e.g., `agent-research`) Optionally gathers additional context based on user preferences.
*   **Context Synthesizer:** (Worker Agent, e.g., `agent-context-condenser`) Condenses source data (from file, folder, URL, MCP, crawl) and optional gathered context into a structured JSON format based on synthesis task templates.
*   **Mode Structure Agent:** (Worker Agent, e.g., `mode-maintainer`, `technical-writer`, `toml-specialist`) Creates directories, reads/parses context from temporary JSON file, populates KB files, updates indexes, README, usage strategy, and mode definition file, preferring MCP tools.
*   **QA Agent:** (Worker Agent, potentially Coordinator) Reviews generated artifacts against standards and requirements (part of ACQA process).
*   **Web Crawler Agent:** (Worker Agent, e.g., `spec-firecrawl`, `spec-crawl4ai`) Extracts content from a specified URL.

## 4. Preconditions🚦

*   The target specialist mode (`[mode_slug]`) exists.
*   The user can provide valid input for the chosen context source type (path, URL, etc.).
*   Network access is available if URL/MCP/Crawl sources are chosen.
*   Relevant crawling agents/MCPs are available if Web Crawl source is chosen.
*   The Library Type Mapping file (`.ruru/config/library-types.json`) exists.
*   Synthesis Task Set templates exist in `.ruru/templates/synthesis-task-sets/`.
*   Required agents (`agent-research`, `agent-context-condenser`, `mode-maintainer`, etc.) are operational.
*   Relevant MCP servers (e.g., `vertex-ai-mcp-server`) are connected (preferred).
*   The User is available for interaction.
*   The `.ruru/temp/` directory exists and is writable.

## 5. Reference Documents & Tools 📚🛠️

*   Previous Workflow: `.ruru/workflows/WF-MODE-KB-ENRICHMENT-001.md`
*   Mode Creation Workflow: `.ruru/workflows/WF-NEW-MODE-CREATION-004.md`
*   Library Type Mapping: `.ruru/config/library-types.json`
*   Synthesis Task Templates: `.ruru/templates/synthesis-task-sets/` (see `README.md`)
*   Relevant Rules: `.roo/rules/` (TOML format, Logging, MCP Usage, etc.)
*   Relevant Processes: ACQA, AFR, PAL
*   **MCP Tools (Preferred):** `read_file_content`, `read_multiple_files_content`, `write_file_content`, `create_directory`, `list_directory_contents`, `answer_query_direct` (for assessment), `save_topic_explanation` (Vertex AI source), `use_mcp_tool` (for crawling)
*   **Fallback Tools:** `read_file`, `write_to_file`, `execute_command` (for `mkdir`, `rm`), `list_files`, `apply_diff`, `insert_content`, `search_files` (for workspace folder)

## 6. Workflow Steps 🪜

*(Coordinator: `roo-commander` unless otherwise specified)*

*   **Step 1: Initiation & Requirements Gathering (Coordinator, User)**
    *   **1.1:** Coordinator asks User for an approximate name or part of the slug for the target mode. Store as `[approx_mode_name]`.
    *   **1.2:** Coordinator uses `list_files` on `.ruru/modes/` (non-recursive) to get a list of all mode slugs (directory names).
    *   **1.3:** Coordinator filters the list of slugs based on `[approx_mode_name]`.
    *   **1.4:** If exactly one match is found, propose it to the user for confirmation. If multiple matches, present them using `ask_followup_question`. If no matches, inform the user and ask for a different name. Store the confirmed, exact slug as `[mode_slug]`. Handle errors/user cancellation.
    *   **1.5: Select Context Source Type (Coordinator, User)**
        *   Use `<ask_followup_question>`: "Please select the type of primary context source for the library documentation:"
            *   `<suggest>Workspace Folder (Provide path)</suggest>`
            *   `<suggest>Workspace File (Provide path)</suggest>`
            *   `<suggest>Vertex AI MCP (Use AI to generate context)</suggest>`
            *   `<suggest>Web Crawl URL (Provide URL for AI crawling)</suggest>`
            *   `<suggest>Specify Manually / Other</suggest>`
        *   Store the user's choice as `[context_source_type]`.
    *   **1.5.1: Handle Workspace Folder/File (Coordinator, User)**
        *   If `[context_source_type]` is "Workspace Folder" or "Workspace File":
            *   Ask User for the relative path (e.g., `src/docs/library`, `docs/main_spec.md`). Store as `[context_source_value]`.
            *   Validate path existence (using `list_files` or MCP `get_filesystem_info`). Handle errors.
    *   **1.5.2: Handle Vertex AI MCP (Coordinator, User)**
        *   If `[context_source_type]` is "Vertex AI MCP":
            *   Ask User for the specific topic/library name to use for generation (e.g., "React Router v6"). Store as `[vertex_topic]`.
            *   Ask User for the specific query or aspect to focus on (e.g., "Explain core concepts and provide usage examples"). Store as `[vertex_query]`.
            *   Store `{ topic: [vertex_topic], query: [vertex_query] }` as `[context_source_value]`.
            *   *(Note: Subsequent steps will use `save_topic_explanation` or similar)*.
    *   **1.5.3: Handle Web Crawl URL (Coordinator, User)**
        *   If `[context_source_type]` is "Web Crawl URL":
            *   Ask User for the general website URL to crawl. Store as `[context_source_value]`. Validate basic URL format.
            *   *(Placeholder Comment: Check for available crawling MCPs like `spec-firecrawl`, `spec-crawl4ai`. If none, inform user and potentially stop or offer alternatives.)*
    *   **1.5.4: Handle Manual/Other (Coordinator, User)**
        *   If `[context_source_type]` is "Specify Manually / Other":
            *   Ask User for details on how to obtain the context source. Store description/instructions as `[context_source_value]`.
            *   *(Note: This may require manual intervention or custom steps not fully automated by this workflow).*
    *   **1.6:** Coordinator asks User for context preferences (similar to WF-NEW-MODE-CREATION Step 1.5): "How should I approach gathering any *additional* context beyond the primary source (`[context_source_type]`) for the library?" (Suggest: 1. Use Primary Source Only, 2. Standard Research, 3. Deep Dive Research, 4. Let me specify...). Note preference `[context_preference]`. Handle specific details if needed.
    *   **1.7:** Coordinator asks User: "Should I perform an AI assessment of the potential KB depth before generating files?" (Suggest: Yes, No). Note preference `[perform_assessment]`.
    *   **1.8:** Coordinator attempts to derive a short, filesystem-safe `[library_name]` based on `[context_source_type]` and `[context_source_value]` (e.g., from filename, folder name, URL segment, Vertex topic).
    *   **1.8b:** Coordinator asks User to confirm the derived `[library_name]` or provide a preferred one. Store the confirmed name. Handle potential errors in derivation/confirmation.
    *   **1.9:** Coordinator summarizes confirmed `[mode_slug]`, confirmed `[library_name]`, `[context_source_type]`, `[context_source_value]` (or relevant parts), `[context_preference]`, `[perform_assessment]`. Ask User for confirmation.

*   **Step 2: Acquire Source Content (Coordinator)**
    *   **2.1:** Define base temporary path: `[temp_source_base_path] = .ruru/temp/doc-source-[library_name]`.
    *   **2.2:** Based on `[context_source_type]`:
        *   **Workspace File:**
            *   Set `[source_content_location] = [context_source_value]` (from 1.5.1). Verify existence again. Handle errors -> **Stop**.
        *   **Workspace Folder:**
            *   Set `[source_content_location] = [context_source_value]` (from 1.5.1). Verify existence again. Handle errors -> **Stop**. *(Note: Step 6 needs to handle reading multiple files from this folder).*
        *   **Vertex AI MCP:**
            *   Set `[temp_source_path] = [temp_source_base_path] + .md`.
            *   Use `use_mcp_tool` with `vertex-ai-mcp-server` and `save_topic_explanation`.
                *   `arguments`: `{ "topic": "[vertex_topic]", "query": "[vertex_query]", "output_path": "[temp_source_path]" }` (using values from 1.5.2).
            *   Check result. Verify file `[temp_source_path]` created. Store `[temp_source_path]` as `[source_content_location]`. Handle errors -> **Stop**.
        *   **Web Crawl URL:**
            *   Set `[temp_source_path] = [temp_source_base_path] + .md`.
            *   *(Placeholder Comment: Delegate to available crawler agent (e.g., `spec-firecrawl`) using `use_mcp_tool` or `new_task`. Instruct it to save crawled content to `[temp_source_path]`.)*
            *   *(Placeholder Comment: Check result. Verify file `[temp_source_path]` created.)* Store `[temp_source_path]` as `[source_content_location]`. Handle errors -> **Stop**.
        *   **Manual/Other:**
            *   Log instructions from `[context_source_value]`. May require manual step outside workflow. Assume content is manually placed at a location `[manual_source_path]`. Set `[source_content_location] = [manual_source_path]`. Verify existence. Handle errors -> **Stop**.
    *   **2.3:** Log the determined `[source_content_location]` and method used.

*   **Step 3: Context Gathering (Optional) (Coordinator delegates to Context Gatherer)**
    *   **3.1:** If `[context_preference]` requires additional research:
            *   Delegate to `agent-research` to gather context based on the confirmed `[library_name]` and `[context_preference]`.
            *   Instruct agent to prefer MCP tools (`explain_topic_with_docs`, `answer_query_websearch`) with fallbacks.
            *   Store gathered context (e.g., text content) as `[additional_context]`.
    *   **3.2:** If `[context_preference]` is "Use Primary Source Only", set `[additional_context]` to empty/null.

*   **Step 4: AI Assessment (Optional) (Coordinator, potentially delegates)**
    *   **4.1:** If `[perform_assessment]` is "Yes":
        *   Prepare input: Reference the primary source at `[source_content_location]` (Step 2). If it's a folder, specify the folder path. Include summary/reference to `[additional_context]` if gathered.
        *   Formulate query (adapting based on whether source is file or folder) for LLM (Prefer MCP `answer_query_direct`).
        *   Execute query and store result `[ai_assessment_result]` (rating and topics). Log result.
        *   Handle assessment errors (default to 'Standard' rating, log error).
    *   **4.2:** If `[perform_assessment]` is "No", set `[ai_assessment_result]` to null.

*   **Step 5: Determine Library Type & Load Synthesis Task Set (Coordinator)**
    *   *(No changes needed here, uses confirmed `[library_name]`)*
    *   **5.1:** Read `.ruru/config/library-types.json` (Prefer MCP `read_file_content`, fallback `read_file`). Parse JSON.
    *   **5.2:** Determine `[library_type]` for the confirmed `[library_name]` (fallback to "generic").
    *   **5.3:** Construct path to `[library_type]-tasks.toml` in `.ruru/templates/synthesis-task-sets/`. Check existence (Prefer MCP `get_filesystem_info`, fallback `list_files`). Use fallback `generic-tasks.toml` if specific not found. Log warning if fallback used. **Stop** if fallback also missing.
    *   **5.4:** Read the selected task set file (Prefer MCP `read_file_content`, fallback `read_file`). Parse TOML into `[synthesis_tasks_list]`. Handle errors (Log, **Stop**).

*   **Step 6: Context Synthesis (Coordinator delegates to Context Synthesizer)**
    *   **6.1:** Delegate to `agent-context-synthesizer`.
    *   **6.2:** Instruct agent to:
        *   Access the primary source content based on `[source_content_location]` (Step 2).
            *   If it's a file path: Read the file (Prefer MCP `read_file_content`, fallback `read_file`).
            *   If it's a folder path: Read all relevant files (e.g., `.md`) within the folder (Prefer MCP `read_multiple_files_content` or fallback `search_files` + iterative `read_file`).
        *   Incorporate `[additional_context]` (Step 3) if available.
        *   Execute synthesis tasks defined in `[synthesis_tasks_list]` iteratively, adapting logic for single file vs. multiple files/folder input.
        *   Output results as a **JSON structure** (array of objects: `{ "filename": "[relative_path_for_synthesized_file.md]", "content": "[synthesized_markdown_content]" }`). Ensure `filename` reflects potential subfolder structure if chosen later.
        *   **Crucially, ensure synthesized `content` includes appropriate TOML frontmatter (`title`, `summary`, `tags`).**
    *   **6.3:** Receive JSON output `[synthesized_json_context]`. Handle delegate failure (Log, **Stop**).

*   **Step 7: Save Synthesized Context (Coordinator)**
    *   *(No changes needed here, uses confirmed `[mode_slug]` and `[library_name]`)*
    *   **7.1:** Define `[temp_json_path] = .ruru/temp/kb-enrichment-context-[mode_slug]-[library_name].json`.
    *   **7.2:** Use file writing tool (Prefer MCP `write_file_content`, fallback `write_to_file`) to save `[synthesized_json_context]` to `[temp_json_path]`. Handle errors (Log, **Stop**).

*   **Step 8: KB Population Prompt (Coordinator, User)**
    *   *(No changes needed here)*
    *   **8.1:** Read `[temp_json_path]` (Prefer MCP `read_file_content`, fallback `read_file`).
    *   **8.2:** Formulate question for User, including `[ai_assessment_result]` if available (Step 4).
    *   **8.3:** Use `ask_followup_question` (similar to WF-NEW-MODE-CREATION Step 6) offering KB structure options:
        *   1. Standard KB (Single Folder)
        *   2. Comprehensive KB (Subfolders) (Offer if assessment suggests Comprehensive/Advanced)
        *   3. Basic KB Structure (Placeholders) (Offer if assessment suggests Basic)
        *   4. Skip KB Population
    *   **8.4:** Store User's decision `[kb_structure_choice]`.

*   **Step 9: Prepare Target Directory (Coordinator delegates to Mode Structure Agent)**
    *   *(No changes needed here, uses confirmed `[mode_slug]` and `[library_name]`)*
    *   **9.1:** Define `[synthesized_kb_dir] = .ruru/modes/[mode_slug]/kb/[library_name]/synthesized/`.
    *   **9.2:** Instruct Mode Structure Agent to ensure `[synthesized_kb_dir]` exists. (Prefer MCP `create_directory`, fallback `execute_command mkdir -p ...`). Handle errors.

*   **Step 10: Delegate KB Population (Coordinator delegates to Mode Structure Agent)**
    *   *(No changes needed here, uses confirmed `[mode_slug]` and `[library_name]`)*
    *   **10.1:** If `[kb_structure_choice]` is "Skip KB", proceed to Step 11.
    *   **10.2:** Instruct Mode Structure Agent to:
        *   Read and parse `[temp_json_path]` (Prefer MCP `read_file_content`, fallback `read_file`).
        *   If `[kb_structure_choice]` is "Comprehensive KB (Subfolders)": Create necessary subdirectories within `[synthesized_kb_dir]` based on `filename` paths in the JSON. (Prefer MCP `create_directory`, fallback `execute_command mkdir -p ...`).
        *   If `[kb_structure_choice]` involves population: Iterate through JSON array, creating/populating each KB file at `.ruru/modes/[mode_slug]/kb/[library_name]/[filename]` (respecting subfolders in `filename`) using the `content`. (Prefer MCP `write_file_content`, fallback `write_to_file` iteratively).
        *   If `[kb_structure_choice]` is "Basic KB Structure": Create placeholder files as appropriate.
    *   **10.3:** Handle errors during file/directory creation (Log, potentially **Stop** if critical).

*   **Step 11: Build Library Index (Coordinator delegates to Mode Structure Agent)**
    *   **Condition:** Only run this step if KB population was NOT skipped in Step 8.
    *   *(No changes needed here, uses confirmed `[mode_slug]` and `[library_name]`)*
    *   **11.1:** Instruct Mode Structure Agent to:
        *   Scan for `.md` files within `[synthesized_kb_dir]` (created in Step 9). (Prefer MCP `list_directory_contents` recursively, fallback `list_files`). Store paths `[synthesized_files]`.
        *   If `[synthesized_files]` is empty (or population skipped), log warning and skip to Step 12.
        *   Initialize `library_index_entries = []`.
        *   For each `file_path` in `[synthesized_files]`:
            *   Read file (Prefer MCP `read_file_content`, fallback `read_file`). Handle errors (Log, skip).
            *   Extract TOML frontmatter (`title`, `summary`, `tags`). Handle errors (Log, skip).
            *   Create entry object: `{ title, summary, tags, file = "synthesized/[relative_path_from_synthesized_dir]" }`. Append to `library_index_entries`.
        *   Sort entries by `title`.
        *   Format as TOML string `[Generated TOML String]` using `[[documents]]`.
        *   Define `[library_index_path] = .ruru/modes/[mode_slug]/kb/[library_name]/index.toml`.
        *   Write `[Generated TOML String]` to `[library_index_path]`. (Prefer MCP `write_file_content`, fallback `write_to_file`). Handle errors (Log, **Stop**).
    *   **11.2:** Handle delegate errors.

*   **Step 12: Update Mode Master Index (Coordinator delegates to Mode Structure Agent)**
    *   **Condition:** Only run this step if KB population was NOT skipped in Step 8.
    *   *(Original Step 13a content goes here, renumbered)*
    *   **12.1:** Instruct Mode Structure Agent to:
        *   Define `[master_index_path] = .ruru/modes/[mode_slug]/kb/index.toml`.
        *   Read `[master_index_path]` (Prefer MCP `read_file_content`, fallback `read_file`). Handle not found (init empty index), handle read/parse errors (Log, ask user before overwrite, **Stop** if critical).
        *   Parse TOML into `master_index_data`.
        *   Find/update or append library entry: `{ name = "[library_name]", description = "Synthesized KB for [library_name] from [context_source_type]", index_file = "[library_name]/index.toml", last_updated = "[current_date]" }`. # Updated description
        *   Sort `master_index_data.libraries` by `name`.
        *   Format back to TOML string `[Master TOML String]`.
        *   Write `[Master TOML String]` to `[master_index_path]`. (Prefer MCP `write_file_content`, fallback `write_to_file`). Handle errors (Log, **Stop**).
    *   **12.2:** Handle delegate errors.

*   **Step 13: Update/Create KB Usage Strategy (Coordinator delegates to Mode Structure Agent)**
    *   *(No changes needed here, uses confirmed `[mode_slug]`)*
    *   **13.1:** Instruct Mode Structure Agent to:
        *   Define `[usage_strategy_path] = .ruru/modes/[mode_slug]/kb/00-kb-usage-strategy.md`.
        *   Check if `[usage_strategy_path]` exists (Prefer MCP `get_filesystem_info`, fallback `list_files`).
        *   If it does NOT exist: Create it using standard content (defined in planning docs or a template). (Prefer MCP `write_file_content`, fallback `write_to_file`). Handle errors (Log).
        *   If it exists: Log that it already exists, no action needed for creation.
    *   **13.2:** Handle delegate errors.

*   **Step 14: Update Mode Definition Context (Coordinator delegates to Mode Structure Agent)**
    *   **Condition:** Only run this step if KB population was NOT skipped in Step 8.
    *   *(No changes needed here, uses confirmed `[mode_slug]` and `[library_name]`)*
    *   **14.1:** Instruct Mode Structure Agent to:
        *   Define `[mode_file_path] = .ruru/modes/[mode_slug]/[mode_slug].mode.md`.
        *   Define `[index_context_path] = kb/[library_name]/index.toml`.
        *   Read `[mode_file_path]` (Prefer MCP `read_file_content`, fallback `read_file`). Handle errors (Log, **Stop**).
        *   Parse TOML frontmatter.
        *   Check if `[index_context_path]` is already in the `related_context` array.
        *   If NOT present: Add it to the `related_context` array. Re-serialize TOML. Use `apply_diff` (or MCP `edit_file_content`) to update the TOML block in `[mode_file_path]`. Handle errors (Log, **Stop**).
        *   If present: Log that context already exists, no update needed.
    *   **14.2:** Handle delegate errors.

*   **Step 15: Generate/Update KB README (Coordinator delegates to Mode Structure Agent)**
    *   **Condition:** Only run this step if KB population was NOT skipped in Step 8.
    *   **15.1:** Instruct Mode Structure Agent to create/update `.ruru/modes/[mode_slug]/kb/README.md`.
    *   **15.2:** README should include:
        *   Overview of the KB.
        *   List of library KBs indexed in `kb/index.toml`.
        *   Add/update a section for the confirmed `[library_name]`, listing synthesized files created (from Step 10, potentially using `list_files` or reading `kb/[library_name]/index.toml`), including summaries/line counts or status (Basic/Skipped). Mention the source type used (`[context_source_type]`) and potentially the specific source (`[context_source_value]`).
    *   **15.3:** Use file writing tools (Prefer MCP `write_file_content`, fallback `write_to_file`). Handle errors (Log).

*   **Step 16: Quality Assurance (Coordinator applies ACQA)**
    *   *(No changes needed here, uses confirmed `[library_name]`)*
    *   **16.1:** Coordinator initiates ACQA process (`.ruru/processes/acqa-process.md`).
    *   **16.2:** Checks (potentially delegated to `QA Agent`):
        *   Correctness of synthesized files (spot check).
        *   Validity and consistency of `kb/[library_name]/index.toml` and `kb/index.toml`.
        *   Update status of `kb/README.md`.
        *   Presence of `kb/00-kb-usage-strategy.md`.
        *   Correct update of `related_context` in `.mode.md`.
    *   **16.3:** Handle issues via corrections (looping back) or AFR process.

*   **Step 17: User Review (Coordinator, User)**
    *   *(No changes needed here, uses confirmed `[library_name]` and `[mode_slug]`)*
    *   **17.1:** Coordinator presents summary of changes (new files in `synthesized/`, updated indexes/README) to User.
    *   **17.2:** Ask User for feedback: "Does this KB enrichment for `[library_name]` in mode `[mode_slug]` meet your expectations?"
    *   **17.3:** Handle refinements by looping back to relevant steps if necessary, followed by QA.

*   **Step 18: Identify & Suggest Placeholder KB Removal (Coordinator, User)**
    *   **18.1:** Coordinator lists all `.md` files within the target mode's main KB directory: `.ruru/modes/[mode_slug]/kb/` (excluding subdirectories like `/[library_name]/`). (Use `list_files` or MCP `list_directory_contents`).
    *   **18.2:** For each file found:
        *   Read the first ~10 lines (Use `read_file` with `end_line=10` or MCP `read_file_content` and truncate).
        *   Check if the content suggests it's a placeholder (e.g., contains "[Add content here]", "# Placeholder", "## Overview\n\nTODO", or is very short/empty).
    *   **18.3:** If potential placeholder files are identified:
        *   Present the list of identified file paths to the User.
        *   Use `<ask_followup_question>`: "I found the following files in `.ruru/modes/[mode_slug]/kb/` that might be placeholders. Do you want to delete them?"
            *   `<suggest>Yes, delete the listed files.</suggest>`
            *   `<suggest>No, keep the files.</suggest>`
            *   `<suggest>Let me review them manually first.</suggest>`
    *   **18.4:** If User confirms deletion:
        *   Instruct the appropriate agent (or Coordinator performs directly) to delete the confirmed files. (Use `execute_command rm [path1] [path2]...` or MCP `delete_file` iteratively). Log the action.
    *   **18.5:** If User chooses manual review or declines deletion, log the decision and proceed.

*   **Step 19: Delete Temporary Files (Coordinator)**
    *   *(Renumbered from 18)*
    *   **19.1:** Once QA and User Review pass (and optional placeholder cleanup is addressed):
        *   Use file operation tool to delete the temporary JSON context file `[temp_json_path]` (Step 7.1). (Prefer MCP `delete_file`, fallback `execute_command rm ...`). Handle errors (Log).
        *   If `[source_content_location]` (from Step 2) points to a file within `.ruru/temp/` (i.e., if it was downloaded/generated by Vertex/Crawled, *not* if it was a workspace path): Delete it. (Prefer MCP `delete_file`, fallback `execute_command rm ...`). Handle errors (Log).

*   **Step 20: Finalization (Coordinator)**
    *   *(Renumbered from 19)*
    *   **20.1:** Log successful completion of enrichment for confirmed `[library_name]` in `[mode_slug]` using source type `[context_source_type]`. # Updated log message
    *   **20.2:** Report success to the User/initiating process.

## 7. Postconditions ✅

*   Synthesized documents exist in `.ruru/modes/[mode_slug]/kb/[library_name]/synthesized/` (potentially with subfolders).
*   Valid `index.toml` exists at `.ruru/modes/[mode_slug]/kb/[library_name]/index.toml`.
*   The mode's master index `.ruru/modes/[mode_slug]/kb/index.toml` includes/updates the entry for the confirmed `[library_name]`.
*   The mode's KB README `.ruru/modes/[mode_slug]/kb/README.md` is updated.
*   The mode's usage strategy exists at `.ruru/modes/[mode_slug]/kb/00-kb-usage-strategy.md`.
*   The mode's definition file `.ruru/modes/[mode_slug]/[mode_slug].mode.md` has `kb/[library_name]/index.toml` in `related_context`.
*   The temporary JSON context file and any temporary source files are deleted. # Updated postcondition

## 8. Error Handling & Escalation (Overall) ⚠️

*   Log errors at each step. Use AFR process for persistent issues.
*   Failure to acquire or verify source data (Step 2) is critical -> **Stop**.
*   Failure in synthesis (Step 6) or context saving/reading (Step 7, 8, 10) is critical -> **Stop**.
*   Failure in KB population (Step 10) or indexing (Step 11, 12) may require manual intervention or **Stop**.
*   Failure to update mode definition (Step 14) or README (Step 15) should be logged; mode might function but lack full context integration.
*   QA failures (Step 16) trigger correction loops or AFR.
*   User rejection (Step 17) triggers refinement loops or documented closure.
*   Failure to delete temp files (Step 18) is logged but non-critical.

## 9. PAL Validation Record 🧪

*   Date Validated: TBD
*   Method: TBD (Test Case Execution)
*   Test Case(s): Enrich mode 'A' with library 'B' using 'Workspace Folder'. Test 'Vertex AI MCP' source. Test 'Web Crawl URL' source (with mock crawler). Test 'Skip KB' option. Test MCP fallbacks.
*   Findings/Refinements: TBD

## 10. Revision History 📜

*   v2.0 (2025-04-26): Initial draft based on WF-MODE-KB-ENRICHMENT-001 and incorporating improvements from WF-NEW-MODE-CREATION-004 (AI assessment, JSON context, KB structure options, MCP preference, QA, User Review, Cleanup). Focused on enriching *existing* modes. Used a generic base URL + suffix for source fetching.
*   v2.1 (2025-04-27): Replaced simple URL prompt (Step 1.5) with multi-choice selection for context source type (Workspace Folder/File, Context7 URL, Vertex AI MCP, Web Crawl URL, Manual). Added sub-steps (1.5.1-1.5.5) to handle input for each type. Adjusted subsequent steps (2, 4, 6, 12, 15, 18, 19) to accommodate different source types. Updated metadata, scope, roles, preconditions, postconditions. Added placeholder comments for crawler integration.
*   v2.2 (2025-04-27): Integrated `process_llms_json.js` script for 'Context7 Library URL' source type. Removed `curl` download for Context7. Added new Step 9 to execute the script. Removed original Steps 9-11 (Prepare Dir, Populate KB, Build Index for non-Context7). Renumbered subsequent steps. Added conditional logic to skip synthesis/population/indexing steps (6, 7, 8, 10, 11, 12) for Context7. Added Step 13b to update master index specifically for Context7 output. Modified Steps 15 (Mode Def), 16 (README), 19 (Cleanup) to handle Context7 paths (`kb/context7/_index.json`). Updated metadata and revision history.
*   v2.3 (2025-04-27): Removed 'Context7 Library URL' source type and associated `process_llms_json.js` script integration. Deleted Step 1.5.2, Step 9, and Step 13b. Renumbered subsequent steps. Removed conditional logic related to Context7 in Steps 6, 7, 8, 10, 11, 12, 14, 15, 18. Simplified Step 18 (Cleanup). Updated metadata (version, tags, objective, scope, success/failure criteria, postconditions) and revision history.