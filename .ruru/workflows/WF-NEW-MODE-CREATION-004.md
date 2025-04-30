+++
# --- Basic Metadata ---
id = "WF-NEW-MODE-CREATION-004" # Updated ID
title = "Interactive New Mode Creation Workflow (.ruru/modes/ Structure)"
status = "draft" # Remains draft until fully tested/validated
created_date = "2025-04-16"
updated_date = "2025-04-26" # Date updated reflecting these revisions
version = "4.0" # Incremented version for AI Assessment & KB Granularity
tags = [
    "workflow", "mode-creation", "interactive", "modes-structure", "naming-convention",
    "kb-population", "readme-enhancement", "kb-generation", "template-enforcement",
    "mode-registry", "context-handling", "user-input", "scalability", "json-context", "mcp-preference",
    "synthesis-templates", "core-knowledge", "vertex-ai", "ux-improvement",
    "ai-assessment", "kb-granularity", "subfolders" # Added new tags for v4.0
]

# --- Ownership & Context ---
owner = "Roo Commander"
related_docs = [
    "`.ruru/modes/roo-commander/kb/available-modes-summary.md`",
    "`.ruru/rules/00-standard-toml-md-format.md`",
    "`.ruru/processes/acqa-process.md`",
    "`.ruru/processes/afr-process.md`",
    "`.ruru/processes/pal-process.md`",
    "`.ruru/templates/synthesis-task-sets/README.md`"
]
related_templates = [
    "`.ruru/templates/modes/00_standard_mode.md`", # Standard Mode Template (v1.1)
    "`.ruru/templates/toml-md/16_ai_rule.md`", # For KB lookup rule
    "`.ruru/templates/synthesis-task-sets/*.toml`" # Synthesis task templates
]

# --- Workflow Specific Fields ---
objective = "To guide the creation of a new Roo Commander mode from scratch, incorporating refined user requirements gathering (with improved UX for context preferences), using the `.ruru/modes/` structure, applying predefined naming conventions, generating a detailed 'Core Knowledge & Capabilities' section (with enhanced detail request), separating knowledge base (KB) content (with option to generate basic KB if missing), creating mode-specific rules, generating an enhanced KB README, running `build_roomodes.js` to update the mode registry, enforcing the standard mode template structure, maximizing delegation, managing context via a temporary JSON file, utilizing synthesis task templates, and preferring MCP tools where available." # Updated objective
scope = "Applies when creating a *new* Roo Commander mode. Requires user interaction. Gathers detailed user input upfront (using simplified options for context preferences). Includes AI assessment of research depth. Creates structure in `.ruru/modes/` and `.roo/rules-<slug>/`. Uses naming conventions. Generates 'Core Knowledge' using Vertex AI MCP (if available) or fallback methods. Optionally populates KB files (potentially in subfolders) based on synthesized context (from JSON), applying requested detail level and AI assessment. Populates the standard mode template (from JSON). Generates KB README and KB lookup rule. Triggers mode registry update (`build_roomodes.js`). Cleans up temporary JSON context file. Prefers MCP tools." # Updated scope for v4.0
roles = ["User", "Coordinator (Roo Commander)", "Context Gatherer (e.g., agent-research)", "Context Synthesizer (e.g., agent-context-condenser)", "Mode Structure Agent (e.g., mode-maintainer, technical-writer, toml-specialist)", "QA Agent (e.g., code-reviewer)"]
trigger = "User request to create a new mode, specifying its purpose and basic identification."
success_criteria = [
    "Mode definition file exists in `.ruru/modes/<new-slug>/<new-slug>.mode.md`, adhering to the standard template structure (`.ruru/templates/modes/00_standard_mode.md`), containing gathered/generated data (including Core Knowledge and AI assessment results if applicable) with the correct `id`.", # Updated for v4.0
    "KB directory exists at `.ruru/modes/<new-slug>/kb/`.",
    "KB directory contains either generated content from provided sources (parsed from JSON context) or generated basic KB content (unless explicitly skipped).",
    "KB README (`.ruru/modes/<new-slug>/kb/README.md`) exists and contains an overview, file list with summaries and line counts (or indicates pending/skipped population).",
    "Mode-specific rule directory exists at `.roo/rules-<slug>/`.",
    "KB lookup rule file exists at `.roo/rules-<slug>/01-kb-lookup-rule.md` using the standard rule template (`.ruru/templates/toml-md/16_ai_rule.md`) with enhanced instructions.",
    "The mode registry is successfully updated after running `build_roomodes.js`.",
    "The temporary context file (`.ruru/temp/mode-creation-context-<new-slug>.json`) is deleted.",
    "The created structure passes Quality Assurance (QA) review against specifications (including template structure).",
    "User confirms the generated mode meets initial requirements and is accessible after window reload."
]
failure_criteria = [
    "Unable to determine a valid `prefix-topic` slug with user.",
    "Unable to gather sufficient context (including from user-provided files or based on selected preference).",
    "Failure during AI assessment of context depth/breadth (Step 3).", # Added for v4.0
    "Failure during context synthesis using task templates.",
    "Failure during context saving to temporary JSON file.",
    "Failure during Core Knowledge generation (MCP or fallback methods).",
    "Failure during optional KB population/generation sub-process (including parsing JSON context).",
    "Worker Agent fails to correctly populate the standard mode template (potentially due to failure reading/parsing temp JSON context file).",
    "Worker Agent fails critical file/directory operations (potentially due to MCP tool failure without fallback success).",
    "Worker Agent fails to generate enhanced KB README.",
    "Failure during execution of `build_roomodes.js`.",
    "Failure to delete the temporary context JSON file.",
    "Generated structure repeatedly fails QA.",
    "User rejects the final mode structure or cannot access it after reload."
]

# --- Integration ---
acqa_applicable = true # Requires ACQA review
pal_validated = false # Needs re-validation for v4.0
validation_notes = ""

# --- AI Interaction Hints (Optional) ---
# context_type = "workflow_definition"
+++

# Interactive New Mode Creation Workflow

## 1. Objective 🎯
To guide the creation of a new Roo Commander mode from scratch. This involves:
*   Gathering refined requirements and context preferences from the user upfront **using simplified options**.
*   Using the `.ruru/modes/` directory structure.
*   Applying predefined naming conventions (see `.ruru/modes/roo-commander/kb/available-modes-summary.md`).
*   Generating a detailed "Core Knowledge & Capabilities" section within the mode definition file, preferring Vertex AI MCP tools.
*   Separating knowledge base (KB) content into the `kb/` subdirectory, with an interactive option to generate basic KB if source material is missing or insufficient, **applying the requested level of detail and potentially using subfolders**.
*   Creating mode-specific rules in the corresponding `.roo/rules-<slug>/` directory, **deferring standard rules**.
*   Generating an enhanced KB `README.md` file summarizing the KB contents.
*   Running the `build_roomodes.js` script to update the application's mode registry.
*   Enforcing the use and structure of the standard mode template (`.ruru/templates/modes/00_standard_mode.md`).
*   Maximizing delegation of tasks to specialized agents where appropriate.
*   Using a temporary JSON file (`.ruru/temp/mode-creation-context-<new-slug>.json`) to pass synthesized context between steps.
*   Utilizing synthesis task templates from `.ruru/templates/synthesis-task-sets/` for structured context generation.
*   Preferring MCP tools (e.g., for file operations, research) with fallbacks to standard tools (`execute_command`, `write_to_file`, etc.).

## 2. Scope ↔️
This workflow applies when creating a *new* Roo Commander mode. Requires user interaction. Gathers detailed user input upfront (using simplified options for context preferences). Includes AI assessment of research depth. Creates structure in `.ruru/modes/` and `.roo/rules-<slug>/`. Uses naming conventions. Generates 'Core Knowledge' using Vertex AI MCP (if available) or fallback methods. Optionally populates KB files (potentially in subfolders) based on synthesized context (from JSON), applying requested detail level and AI assessment. Populates the standard mode template (from JSON). Generates KB README and KB lookup rule. Triggers mode registry update (`build_roomodes.js`). Cleans up temporary JSON context file. Prefers MCP tools.

## 3. Roles & Responsibilities 👤
*   **User:** Initiates the request, provides purpose/context, selects context preference option (or provides details), approves slug/classification/emoji, reviews KB options, potentially provides source files for Core Knowledge, and confirms final mode usability. # Updated
*   **Coordinator (Roo Commander):** Orchestrates the workflow, interacts with the User, delegates tasks to Worker Agents, performs QA, manages temporary context file, and manages finalization steps.
*   **Context Gatherer:** (Worker Agent, e.g., `agent-research`) Gathers relevant information based on the mode's purpose, scope, and user preferences from Step 1.5, **applying the selected detail level**. # Updated
*   **Context Synthesizer:** (Worker Agent, e.g., `agent-context-condenser`) Condenses gathered information into a structured JSON format based on synthesis task templates, suitable for mode definition and KB.
*   **Mode Structure Agent:** (Worker Agent, e.g., `mode-maintainer`, `technical-writer`, `toml-specialist`) Creates directories, reads/parses context from temporary JSON file, populates template files (mode definition, KB files, KB README, rules) based on context and templates, preferring MCP tools.
*   **QA Agent:** (Worker Agent, potentially Coordinator) Reviews generated artifacts against standards and requirements (part of ACQA process).

## 4. Preconditions🚦
*   The Roo Commander system and its delegated agents are operational.
*   Relevant MCP servers (e.g., `vertex-ai-mcp-server`) are connected and operational (preferred, but workflow includes fallbacks).
*   The User is available for interaction and providing necessary input/confirmations.
*   Required templates (`.ruru/templates/modes/00_standard_mode.md`, `.ruru/templates/toml-md/16_ai_rule.md`, `.ruru/templates/synthesis-task-sets/*.toml`) exist and are accessible.
*   Reference documents (naming convention, available modes summary, synthesis template README) are accessible.
*   The `build_roomodes.js` script exists and is executable by the Coordinator.
*   The `.ruru/temp/` directory exists and is writable by the Coordinator.

## 5. Reference Documents & Tools 📚🛠️
*   Naming Convention: `.ruru/modes/roo-commander/kb/available-modes-summary.md`
*   Existing Mode Examples: `.ruru/modes/roo-commander/kb/available-modes-summary.md`
*   Standard Mode Template: `.ruru/templates/modes/00_standard_mode.md`
*   Standard Rule Template: `.ruru/templates/toml-md/16_ai_rule.md`
*   Synthesis Task Templates: `.ruru/templates/synthesis-task-sets/` (see `README.md` there)
*   TOML+MD Format Rule: `.ruru/rules/00-standard-toml-md-format.md`
*   QA Process: `.ruru/processes/acqa-process.md`
*   Failure Resolution Process: `.ruru/processes/afr-process.md`
*   Process Validation Lifecycle: `.ruru/processes/pal-process.md`
*   Mode Registry Build Script: `build_roomodes.js` (Assumed location accessible to Coordinator)
*   Temporary JSON Context File Structure: (See `.ruru/templates/synthesis-task-sets/README.md` for expected output structure based on synthesis templates)
*   **MCP Tools (Preferred):**
    *   `vertex-ai-mcp-server`: `read_file_content`, `read_multiple_files_content`, `write_file_content`, `create_directory`, `move_file_or_directory`, `explain_topic_with_docs`, `get_doc_snippets`, `answer_query_websearch`, `answer_query_direct`
*   **Fallback Tools:** `read_file`, `write_to_file`, `execute_command` (for `mkdir`, `rm`), `apply_diff`, `insert_content`

## 6. Workflow Steps 🪜

*   **Step 1: Initiation & Refined Requirements Gathering (Coordinator, User)**
    *   **1.1: Ask for Initial Description:** Coordinator asks the User for a general description of the desired mode's purpose and function.
    *   **1.2: Analyze & Read Summary:** Coordinator analyzes the description and reads the mode summary file (`.ruru/modes/roo-commander/kb/available-modes-summary.md`).
    *   **1.3: Check for Similarity:** Coordinator checks if any existing modes are significantly similar to the User's description.
    *   **1.4: Prompt Enhancement vs. Creation:** If a similar mode is found, Coordinator asks the User: "A similar mode '[Existing Mode Name]' already exists. Would you prefer to enhance that mode instead?" (Provide "Yes" / "No" suggestions). If "Yes", note to abort this workflow and start an enhancement task. If "No", proceed.
    *   **1.5: Ask User for Context Preferences:** Coordinator uses `ask_followup_question` to ask the User: "How should I approach gathering context and building the Knowledge Base (KB) for this mode? Please select an option:"
        *   *(Coordinator generates suggestions similar to the following)*
        *   `<suggest>1. Standard KB: Focus on common usage, prioritize official docs.</suggest>`
        *   `<suggest>2. Deep Dive KB: Use local docs (if specified), focus on advanced topics, deep research.</suggest>`
        *   `<suggest>3. Quick Overview KB: Broad focus, mixed sources, quick scan.</suggest>`
        *   `<suggest>4. Let me specify the details...</suggest>`
    *   **1.5.1 (Conditional): Handle Specific Details:** If the User selects "Let me specify the details...", the Coordinator follows up with specific questions:
        *   "Are there specific local files or directories you want me to use as primary context?" (Prompt for paths if yes).
        *   "Are there specific topics or areas the Knowledge Base (KB) should focus on?" (Optional input).
        *   "Should research prioritize official documentation (if applicable) over general web search?" (Yes/No/Default).
        *   "What level of research effort is desired?" (Offer dynamic options like: Quick Scan, Standard Research, Deep Dive).
    *   *(Coordinator notes the user's selection or detailed preferences for use in Step 2)*
    *   **1.6: Propose Slug & Classification:** Based on the description and naming conventions, Coordinator proposes a `prefix-topic` slug and `classification`. Ask the User for confirmation. Iterate if necessary.
    *   **1.7: Propose & Select Emoji:** Coordinator proposes 3-5 relevant emojis, potentially explaining the relevance briefly. Present these emojis *inline* within the confirmation suggestions (alongside slug/classification) for the User to select one.
    *   **1.8: Confirm Final Details:** Coordinator summarizes the refined purpose, use cases, target audience, slug, classification, emoji, and context preferences (selected option or specific details). Ask the User for final confirmation using `ask_followup_question`. The suggestions should be ordered: 1. Confirm all, 2. Change slug, 3. Change classification, 4. Change emoji, 5. Change context preferences. *(Note: If the user chooses to change the emoji here, the next prompt should offer 4-10 relevant emoji options, potentially looping back to refine Step 1.7's selection)*. Proceed to Step 2 upon confirmation.

*   **Step 2: Context Gathering (Coordinator delegates to Context Gatherer)**
    *   Coordinator instructs the Context Gatherer agent (e.g., `agent-research`) to find and retrieve relevant information based on the agreed purpose, scope, and user preferences from Step 1.5/1.5.1.
    *   **Instructions MUST include:**
        *   Processing any user-provided local files/directories (from Step 1.5.1) **iteratively** if large. (Prefer MCP `read_multiple_files_content` or `read_file_content`, fallback `read_file`).
        *   Applying user preferences for KB focus areas, documentation priority (prefer MCP `explain_topic_with_docs`/`get_doc_snippets` if official docs preferred, fallback to `answer_query_websearch`), and research effort level (e.g., **ensure the selected effort level, such as 'Deep Dive', is applied, aiming for comprehensive coverage appropriate to that level**). # Enhanced instruction
        *   Emphasize iterative processing for large inputs or deep research levels.
        *   *(Note: Instructions should specify preference for MCP tools and requirement to handle fallbacks.)*

*   **Step 3: AI Assessment of Context Depth/Breadth (Coordinator, potentially delegates)**
    *   **3.1: Prepare Input:** Coordinator extracts the list of filenames/sources used or generated during Step 2.
    *   **3.2: Formulate Query:** Coordinator formulates a query for an LLM (e.g., via `vertex-ai-mcp-server`'s `answer_query_direct` or internal capability) like: "Based on these source filenames related to [Mode Purpose/Topic]: [List of filenames]. Assess the likely depth and breadth of the knowledge base that could be generated. Provide a rating (e.g., Basic, Standard, Comprehensive, Advanced) and list the key topics likely covered."
    *   **3.3: Execute Query & Store Result:** Coordinator (or delegated agent) executes the query and stores the resulting rating and topic list. This result will be used in Step 6.
    *   *(Error Handling: If assessment fails, default to a 'Standard' rating and proceed, logging the error.)*

*   **Step 4: Context Synthesis (Coordinator delegates to Context Synthesizer)**
    *   Coordinator instructs the Context Synthesizer agent (e.g., `agent-context-condenser`) to process the gathered information (output from Step 2).
    *   **Instructions MUST include:**
        *   Identifying and using the appropriate `[type]-tasks.toml` template from `.ruru/templates/synthesis-task-sets/` based on the mode's purpose/classification (fallback to `generic-tasks.toml`).
        *   Executing the synthesis tasks defined in the TOML template **iteratively**.
        *   Outputting the results as a **JSON structure** (e.g., an array of objects, where each object contains `filename` and `content` keys corresponding to the `output_filename` and synthesized content for each task in the TOML template). **If the user later selects the 'Comprehensive KB (Subfolders)' option (Step 6), ensure the `filename` keys in the JSON include the intended subfolder path (e.g., `kb/setup/installation.md`).**
        *   *(Note: Instructions should specify preference for MCP tools and requirement to handle fallbacks.)*

*   **Step 5: Save Synthesized Context (Coordinator)**
    *   Coordinator takes the **JSON output** from Step 4.
    *   Coordinator uses a file writing tool (Prefer MCP `write_file_content`, fallback `write_to_file`) to save this **JSON** context to a temporary file: `.ruru/temp/mode-creation-context-<new-slug>.json`.
    *   Handle potential file writing errors (see Section 8). Note if fallback was used.

*   **Step 6: Optional KB Population Prompt (Coordinator, User)**
    *   Coordinator reviews the synthesized context (by reading the temp file `.ruru/temp/mode-creation-context-<new-slug>.json` - Prefer MCP `read_file_content`, fallback `read_file`) **and the AI assessment result from Step 3**.
    *   Coordinator uses `ask_followup_question` to present the assessment and KB options:
        *   **Question:** "The AI assessment suggests the gathered context is rated '[AI Rating from Step 3]' covering topics like '[Key Topics from Step 3]'. Based on this, how should we structure the Knowledge Base (KB)?"
        *   **Suggestions (Tailored based on AI Rating):**
            *   `<suggest>1. Standard KB (Single Folder): Populate KB files directly in 'kb/'.</suggest>`
            *   `<suggest>2. Comprehensive KB (Subfolders): Organize KB files into subfolders within 'kb/' based on topics.</suggest>` (Offer this prominently if rating is Comprehensive/Advanced)
            *   `<suggest>3. Basic KB Structure: Create placeholder files only.</suggest>` (Offer if rating is Basic or context seems limited)
            *   `<suggest>4. Skip KB Population: Do not create KB files now.</suggest>`
    *   Store the User's decision regarding KB population and structure (Single Folder vs. Subfolders).

*   **Step 7: Delegate Directory Creation (Coordinator delegates to Mode Structure Agent)**
    *   Coordinator instructs the Mode Structure Agent to create the necessary directory structure:
        *   Mode directory: `.ruru/modes/<new-slug>/`
        *   KB subdirectory: `.ruru/modes/<new-slug>/kb/`
        *   Rules directory: `.roo/rules-<slug>/` (using the same `<new-slug>`)
    *   *(Note: Instructions should specify preference for MCP `create_directory` and requirement to handle fallback to `execute_command mkdir -p ...`)*

*   **Step 8: Delegate Initial Mode File Creation using Template (Coordinator delegates to Mode Structure Agent)**
    *   Coordinator instructs the Mode Structure Agent to:
        *   **Read and parse the JSON context** from the temporary file: `.ruru/temp/mode-creation-context-<new-slug>.json`. (Prefer MCP `read_file_content`, fallback `read_file`).
        *   Copy the standard mode template (`.ruru/templates/modes/00_standard_mode.md`) to `.ruru/modes/<new-slug>/<new-slug>.mode.md`.
        *   Populate the TOML frontmatter and relevant sections of this new `.mode.md` file using the **parsed JSON context** (specifically the part relevant to the main mode definition, perhaps identified by a specific task_id/filename in the JSON or inferred), agreed slug, classification, and a generated `id` (e.g., `MODE-<SLUG>`). Ensure adherence to the template's structure. **Leave the `## Core Knowledge & Capabilities` section with a placeholder like `<!-- Core Knowledge to be generated -->`**.
    *   *(Note: Instructions should specify preference for MCP tools (`read_file_content`, `write_file_content`) and requirement to handle fallbacks (`read_file`, `write_to_file`).)*

*   **Step 9: Generate Core Knowledge & Capabilities (Coordinator, delegates as needed)**
    *   **9.1: Check MCP Availability:** Coordinator checks if `vertex-ai-mcp-server` is connected.
    *   **9.2: Generate Knowledge (Branching Logic):**
        *   **If Vertex AI MCP is Available:**
            *   **9.2.A.1:** Coordinator instructs an agent (e.g., `agent-research` or `mode-maintainer`) to use `vertex-ai-mcp-server`'s `explain_topic_with_docs` tool.
            *   **Query:** Formulate a query based on the mode's `slug` and `purpose` (parsed from `.ruru/temp/mode-creation-context-<new-slug>.json`). E.g., "Explain core concepts, principles, best practices, and key functionalities for a [Mode Purpose/Topic] specialist, suitable for an AI assistant's internal knowledge base."
            *   **9.2.A.2:** Agent receives the Markdown output.
            *   **9.2.A.3:** Coordinator instructs `mode-maintainer` to insert this Markdown content into the `## Core Knowledge & Capabilities` section of `.ruru/modes/<new-slug>/<new-slug>.mode.md` (using `apply_diff` or `insert_content`, replacing any placeholder).
        *   **If Vertex AI MCP is NOT Available:**
            *   **9.2.B.1:** Coordinator uses `ask_followup_question` to ask the User: "Vertex AI tools are unavailable for advanced knowledge generation. Can you provide paths to relevant source files (code, docs) to help generate the Core Knowledge section?" (Suggest: "Yes, provide paths", "No, generate from base knowledge").
            *   **9.2.B.2 (If User provides paths):**
                *   Coordinator delegates to `agent-research` to read files (iteratively, prefer MCP `read_multiple_files_content`, fallback `read_file`).
                *   Coordinator delegates to `agent-context-condenser` (or uses base LLM directly) to synthesize knowledge from file content into Markdown suitable for the `## Core Knowledge & Capabilities` section.
            *   **9.2.B.3 (If User says No):**
                *   Coordinator delegates to `agent-context-condenser` (or uses base LLM directly) to generate knowledge based *only* on the mode's purpose/slug using internal knowledge, formatted as Markdown for the `## Core Knowledge & Capabilities` section.
            *   **9.2.B.4 (Optional Review):** Coordinator delegates the generated Markdown (from B.2 or B.3) to `util-second-opinion` for review. Agent receives feedback. Coordinator decides whether to incorporate feedback (potentially another delegation to `mode-maintainer` or `technical-writer`).
            *   **9.2.B.5:** Coordinator instructs `mode-maintainer` to insert the final generated/reviewed Markdown content into the `## Core Knowledge & Capabilities` section of `.ruru/modes/<new-slug>/<new-slug>.mode.md` (using `apply_diff` or `insert_content`, replacing any placeholder).
    *   *(Note: Ensure the agent performing the insertion (9.2.A.3 or 9.2.B.5) uses appropriate tools like `apply_diff` or `insert_content` and handles potential errors. Prefer MCP tools if available for file reading/writing in sub-steps.)*

*   **Step 10: Delegate KB Content / Instruction File Creation (Coordinator delegates to Mode Structure Agent)**
    *   Based on the User's decision in Step 6:
        *   If **Standard KB (Single Folder)** or **Comprehensive KB (Subfolders)**:
            *   Instruct the Agent to **read and parse the JSON context** from `.ruru/temp/mode-creation-context-<new-slug>.json` (Prefer MCP `read_file_content`, fallback `read_file`).
            *   **If Comprehensive KB (Subfolders) was chosen:** Instruct the Agent to **first create any necessary subdirectories** within `.ruru/modes/<new-slug>/kb/` based on the paths specified in the JSON `filename` keys (e.g., `kb/setup/`, `kb/usage/`). (Prefer MCP `create_directory`, fallback `execute_command mkdir -p ...`).
            *   Then, **iterate through the JSON array**, creating/populating each KB file specified by `filename` within `.ruru/modes/<new-slug>/kb/` (including subfolders if applicable) using the corresponding `content`. Process iteratively for many files.
        *   If **Basic KB Structure**: Instruct the Agent to create placeholder files or a single file in `.ruru/modes/<new-slug>/kb/` indicating basic structure and need for population. (JSON context reading might not be strictly needed here but can be passed for consistency).
        *   If **Skip KB**: No KB files are created at this stage, but the KB directory exists.
    *   *(Note: Instructions should specify preference for MCP tools (`read_file_content`, `write_file_content`, `create_directory`) and requirement to handle fallbacks (`read_file`, `write_to_file`, `execute_command`). Handle potential errors per file/directory.)*

*   **Step 11: Delegate Enhanced KB README Update (Coordinator delegates to Mode Structure Agent)**
    *   Coordinator instructs the Mode Structure Agent to create/update the KB README file at `.ruru/modes/<new-slug>/kb/README.md`.
    *   This README should include:
        *   An overview of the KB's purpose (derived from mode purpose, potentially using context parsed from the temp file `.ruru/temp/mode-creation-context-<new-slug>.json` if needed - Prefer MCP `read_file_content`, fallback `read_file`).
        *   A list of files within the `kb/` directory (including subfolders if applicable, potentially using a tree structure if complex) created in Step 10.
        *   Brief summaries and line counts for each KB file (or indicate "Basic structure generated" or "KB population skipped").
    *   *(Note: Instructions should specify preference for MCP tools (`read_file_content`, `write_file_content`) and requirement to handle fallbacks (`read_file`, `write_to_file`).)*

*   **Step 12: Delegate KB Rule Creation (Coordinator delegates to Mode Structure Agent)**
    *   Coordinator instructs the Mode Structure Agent to:
        *   Copy the standard AI rule template (`.ruru/templates/toml-md/16_ai_rule.md`) to `.roo/rules-<slug>/01-kb-lookup-rule.md`.
        *   Populate the template, ensuring the rule correctly targets the KB directory (`.ruru/modes/<new-slug>/kb/`) and includes enhanced instructions for the AI on how to utilize the KB content effectively for this specific mode (potentially using context parsed from the temp file `.ruru/temp/mode-creation-context-<new-slug>.json` if needed - Prefer MCP `read_file_content`, fallback `read_file`).
    *   *(Note: Instructions should specify preference for MCP tools (`read_file_content`, `write_file_content`) and requirement to handle fallbacks (`read_file`, `write_to_file`).)*

*   **Step 13: Quality Assurance (Coordinator applies ACQA)**
    *   Coordinator receives the generated artifacts and the *confidence score* from the Mode Structure Agent.
    *   Coordinator initiates the Adaptive Confidence-based Quality Assurance (ACQA) process (defined in `.ruru/processes/acqa-process.md`), using the received confidence score and the User Caution Level.
    *   This involves checks (potentially delegated to a QA Agent) for:
        *   Correct directory structure and naming.
        *   Presence and basic validity of all required files (`.mode.md`, `kb/README.md`, `01-kb-lookup-rule.md`, KB files if applicable).
        *   Adherence of the `.mode.md` file to the standard template structure **and presence of Core Knowledge content**.
        *   Consistency between the mode definition, KB README, and KB lookup rule.
        *   Correct population of metadata (ID, slug, classification).
        *   Validity of JSON parsing and file creation steps (check logs/agent reports).
    *   If issues are found, initiate corrections (potentially looping back to relevant creation steps like Step 8, 9, 10, 11, 12) and re-run QA. Persistent failures may trigger the Adaptive Failure Resolution (AFR) process (see Section 8).

*   **Step 14: User Review & Refinement (Coordinator, User)**
    *   Coordinator presents the generated mode structure (key files like `.mode.md`, `kb/README.md`) to the User for review.
    *   Coordinator asks for feedback: "Does this initial structure, including the generated Core Knowledge, align with your requirements for the new mode?"
    *   If the User requests refinements, the Coordinator gathers the feedback, determines necessary changes, and potentially loops back to earlier steps (e.g., Step 4 for context synthesis, Step 8/9/10/11/12 for file content) to implement them, followed by re-running QA (Step 13).

*   **Step 15: Build Mode Registry (Coordinator)**
    *   Once the structure passes QA and User review, the Coordinator executes the command to update the mode registry.
    *   Coordinator uses `execute_command` (or equivalent mechanism) to run: `node build_roomodes.js`.
    *   *(Note: While MCP might offer command execution, standard `execute_command` is likely sufficient here unless specific MCP features are needed.)*
    *   Coordinator verifies the command executed successfully (e.g., checks for exit code 0 and absence of critical errors in output). Handle script execution errors as per Section 8.

*   **Step 16: Delete Temporary Context File (Coordinator)**
    *   After successful registry build (Step 15), Coordinator uses a file operation tool to delete the temporary context file.
    *   Target file: `.ruru/temp/mode-creation-context-<new-slug>.json`
    *   *(Note: Instructions should specify preference for MCP tools (`move_file_or_directory`, `delete_file`) and requirement to handle fallback to `execute_command rm ...`)*
    *   Handle potential command execution errors (see Section 8). Note if fallback was used.

*   **Step 17: Reload Window (User Action - IMPORTANT)**
    *   Coordinator informs the user: "The mode structure is complete, the registry has been rebuilt, and temporary files cleaned up. **Please reload the VS Code window now** for the changes to take effect. You can do this via the Command Palette (`Ctrl+Shift+P` or `Cmd+Shift+P`) and searching for 'Developer: Reload Window'."
    *   Coordinator waits for user confirmation that the window has been reloaded before proceeding.

*   **Step 18: Finalization (Coordinator)**
    *   Coordinator confirms with the user that the new mode is now available in the application's mode list and functions as expected at a basic level (e.g., user can switch to it).
    *   Coordinator marks the workflow task as complete.

## 7. Postconditions ✅
*   The new mode's directory structure exists under `.ruru/modes/`.
*   The mode definition file (`<new-slug>.mode.md`) exists, conforms to the standard template, and contains initial content derived from JSON context **including a populated Core Knowledge section**.
*   The KB directory (`kb/`) exists, containing either populated content (from JSON context, potentially in subfolders), basic generated content, or is empty (as per user choice), along with an updated `README.md`.
*   The mode-specific rules directory exists under `.roo/rules-<slug>/`.
*   The KB lookup rule (`01-kb-lookup-rule.md`) exists and is configured.
*   The mode registry has been updated via `build_roomodes.js`.
*   The temporary context file (`.ruru/temp/mode-creation-context-<new-slug>.json`) has been deleted.
*   The User has confirmed the mode is accessible and meets initial requirements after reloading the window.

## 8. Error Handling & Escalation (Overall) ⚠️
*   **Invalid Slug/Classification:** If agreement cannot be reached in Step 1, escalate to the User/owner for clarification or abandon the workflow.
*   **Context Gathering Failure (Step 2):** If agents fail (including reading user files or applying preference), retry. Check MCP tool status. If persistent, notify the User and potentially proceed with minimal context or abandon. # Updated
*   **AI Assessment Failure (Step 3):** If assessment fails, log the error, default rating to 'Standard', notify User, and proceed.
*   **Context Synthesis Failure (Step 4):** If agent fails to process context or use synthesis templates, retry. Check template validity. If persistent, notify User, consider manual synthesis or abandon.
*   **Context Saving Failure (Step 5):** If writing the temporary JSON file fails (both MCP and fallback), log the error, notify the user, and likely abandon the workflow as subsequent steps depend on it.
*   **Core Knowledge Generation Failure (Step 9):** If generation fails (MCP query, fallback synthesis, file insertion), log the error, notify the User. Ensure the `.mode.md` file reflects the failure (e.g., placeholder remains). Proceed if possible, but mode quality will be lower.
*   **KB Population Failure (Step 10):** If KB generation/population fails (including parsing JSON, creating subdirs, or file writing), notify the User, ensure the KB README reflects the failure, and proceed if possible (mode might function without KB initially). Check MCP/fallback tool status.
*   **File/Directory Operations Failure:** If the Mode Structure Agent fails critical operations (Step 7, 8, 10, 11, 12), retry. Log errors. Check MCP tool status and fallback execution. Persistent failure requires manual intervention or abandoning the workflow. Check if failure is related to reading/parsing the temporary JSON context file.
*   **QA Failures (Step 13):** Minor issues trigger corrections and re-QA. Repeated or significant failures (e.g., missing Core Knowledge) should trigger the Adaptive Failure Resolution (AFR) process (`.ruru/processes/afr-process.md`) to diagnose root causes.
*   **`build_roomodes.js` Failure (Step 15):** If the script fails, log the error output. Attempt to diagnose (e.g., syntax error in a mode file). If resolvable, fix and retry Step 15. If not, escalate the script error; the mode will not be available until resolved. **Ensure Step 16 (cleanup) is skipped or handled carefully if this step fails.**
*   **Temporary File Deletion Failure (Step 16):** If deletion fails (MCP and fallback), log the error. This is generally non-critical but should be noted. Manual cleanup might be required later.
*   **User Rejection (Step 14/18):** If the user rejects the final structure or cannot access the mode, gather detailed feedback. Attempt refinement loop (back to Step 14 or earlier). If fundamental issues persist, escalate or document the rejection and close.

## 9. PAL Validation Record 🧪
*(Process Assurance Lifecycle - defined in `.ruru/processes/pal-process.md`)*
*   **Date Validated:** (Needs re-validation for v4.0) # Updated
*   **Method:** (e.g., Walkthrough, Test Case Execution)
*   **Test Case(s):** (e.g., Create mode 'test-basic' with 'Standard KB' preference, Create mode 'dev-complex' with 'Deep Dive KB' preference and user files, Test 'Let me specify...' option in Step 1.5, Test AI Assessment (Step 3), Test KB Prompt options (Step 6), Test 'Comprehensive KB (Subfolders)' option (Steps 4, 10), Test context JSON file creation/read/parse/deletion, Test MCP tool preference/fallback for file ops, Test Core Knowledge generation via MCP, Test Core Knowledge generation via fallback (user files), Test Core Knowledge generation via fallback (base LLM)) # Updated test cases for v4.0
*   **Findings/Refinements:** (Document results of validation here)

## 10. Revision History 📜
*   **v4.0 (2025-04-26):** Added AI Assessment of context depth/breadth (Step 3). Revised KB prompt (Step 6) to present assessment and offer 'Comprehensive KB (Subfolders)' option. Updated Synthesis (Step 4) and KB Population (Step 10) to handle subfolder paths in JSON/file creation. Renumbered steps. Updated metadata, scope, success criteria, error handling, PAL tests. Set `pal_validated` to `false`.
*   **v3.5 (2025-04-26):** Refined Step 1.5 (Context Preferences) UX with simpler `ask_followup_question` options and conditional follow-up (1.5.1). Enhanced Step 2 (Context Gathering) instructions to explicitly request deeper research detail based on user preference. Updated metadata, objective, scope, roles, error handling, and PAL test cases.
*   **v3.4 (2025-04-26):** Added Step 8 for generating "Core Knowledge & Capabilities" section in `.mode.md`. Includes branching logic for using Vertex AI MCP (`explain_topic_with_docs`) if available, or falling back to user-provided files / base LLM generation. Added optional review step (`util-second-opinion`). Renumbered subsequent steps (9-17). Updated metadata, objective, scope, success/failure criteria, QA checks, error handling, and PAL test cases.
*   **v3.3 (2025-04-25):** Comprehensive update:
    *   Restructured Step 1 for refined requirements gathering (user files, KB focus, research level, doc preference).
    *   Updated Step 2 (Context Gathering) delegation to include user preferences, file processing (MCP pref), and iteration.
    *   Updated Step 3 (Context Synthesis) delegation to use synthesis task templates (`.ruru/templates/synthesis-task-sets/`) and output JSON.
    *   Changed temporary context file to `.json` extension throughout (Steps 4, 5, 7, 9, 10, 11, 15, Sections 1, 2, 7, 8).
    *   Updated Step 7 & 9 to read/parse JSON context for mode/KB file population.
    *   Added notes preferring MCP tools with fallbacks for file operations (Steps 4, 6, 7, 9, 10, 11, 15).
    *   Renumbered all steps and updated internal references.
    *   Updated metadata (version, date, tags, objective, scope, criteria).
    *   Updated error handling and PAL test cases.
*   **v3.2 (2025-04-25):** Restructured Step 1 (Initiation & Requirements Gathering) into iterative sub-steps including initial description prompt, similarity check against existing modes, and separate confirmations for slug/classification and emoji selection.
*   **v3.1 (2025-04-25):** Modified context handling to use a temporary file (`.ruru/temp/mode-creation-context-<new-slug>.md`). Inserted Step 3.1 (Save Context), modified Step 6 & 7 (Read Context), inserted Step 12.1 (Delete Context File). Renumbered subsequent steps and updated internal references. Updated metadata (version, date, status).
*   **v3.0 (2025-04-24):** Added Step 11 to run `build_roomodes.js` and Step 12 to remind user to reload VS Code window. Renumbered Finalization to Step 13. Updated TOML `objective` and `scope` to reflect registry build instead of manifest update. Removed duplicate v3.0 history entry. Standardized filename formatting. Enhanced clarity by removing "(No change)" placeholders and defining acronyms. Added detail to refinement (Step 10) and QA failure handling (Step 9, Section 8).
*   **v2.9 (2025-04-24):** Removed manifest steps/references. Added explicit reference to `available-modes-summary.md` for classification guidance in `related_docs` and Step 1. Corrected path for naming convention doc.
*   **v2.8 (2025-04-18):** Updated `related_templates` to reflect standard template v1.1 (containing refined KB guidance). No change to workflow steps themselves.
*   **v2.7 (2025-04-18):** Updated Step 5 to enforce population of the standard template. Updated verification check 3.
*   **v2.6 (2025-04-18):** Refined the "Generate basic KB" instruction in Step 6.
*   **v2.5 (2025-04-18):** Modified Step 3b prompt to offer "Generate basic KB content". Updated Step 6, 7, and 10.
*   **v2.4 (2025-04-18):** Enhanced Step 7 (README generation) and Step 8 (KB lookup rule). Adjusted verification check 5.
*   **v2.3 (2025-04-18):** Added Step 3b to handle insufficient initial context. Adjusted Step 6, 7, and 10.
*   **v2.2 (2025-04-18):** Updated Step 1/3 to use naming convention doc. Status back to draft.
*   **v2.1 (2025-04-18):** Incorporated conceptual review feedback. Added `domain`. Clarified manifest creation. Added `new_task`. Embedded KB rule content. Updated error handling. Added template compatibility note.
*   **v2.0 (2025-04-18):** Major revision for `.ruru/modes/` structure. Updated paths, added manifest/README/rule steps, refined naming.
*   **v1.1 (2025-04-16):** Incorporated conceptual review feedback.
*   **v1.0 (2025-04-16):** Initial draft.