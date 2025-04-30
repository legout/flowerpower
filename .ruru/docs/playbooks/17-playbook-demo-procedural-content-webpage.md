+++
# --- Metadata ---
id = "PLAYBOOK-DEMO-PROCGEN-V1"
title = "Capability Playbook: Procedural Content Generation (Web)"
status = "draft" # Start as draft until tested
created_date = "2025-04-24"
updated_date = "2025-04-24"
version = "1.0"
tags = ["playbook", "documentation", "capability-demo", "procedural-generation", "llm", "ai-content", "mcp", "openai", "vertex-ai", "frontend", "epic", "feature", "task"]
related_docs = [
    ".ruru/docs/standards/project-management-strategy-v1.md",
    ".ruru/planning/project-structure/00-epic-feature-task-plan.md",
    # Assumes an MCP server like vertex-ai-mcp-server is configured, or a direct specialist mode:
    # ".roo/mcp.json",
    # ".ruru/modes/spec-openai/spec-openai.mode.md"
]
objective = "Guide the creation of a simple web page that dynamically generates text content (e.g., descriptions, profiles) on user request by calling an LLM via an MCP server or specialist mode."
scope = "Covers defining the content type and prompts, setting up the frontend UI, implementing the call to the AI service, displaying results, and basic error handling."
target_audience = ["Users", "Developers", "AI Modes"]
# --- Document Specific Fields ---
example_project_type = "Creative Web Demo / AI Integration Example"
ai_service_placeholder = "[AI Service/Mode]" # e.g., "vertex-ai-mcp-server/answer_query_direct", "spec-openai"
content_type_placeholder = "[ContentType]" # e.g., "Fantasy Landscape Descriptions", "SciFi Character Bios"
prompt_placeholder = "[Example LLM Prompt]" # e.g., "Generate a short, unique description of a fantasy landscape."
+++

# Capability Playbook: Procedural Content Generation (Web)

This playbook demonstrates how Roo Commander can manage the development of a web page that uses an AI Large Language Model (LLM) to generate textual content on demand.

**Scenario:** You want to build a simple web page that allows a user to click a button and get a newly generated piece of text content, such as a `[ContentType]`, using `[AI Service/Mode]`.

## Phase 1: Concept & Setup

1.  **Define the Generation Goal (Epic/Feature):**
    *   **Goal:** Specify the type of content to generate and the purpose of the demonstration page.
    *   **Action:** Create an Epic or Feature (e.g., `.ruru/features/FEAT-200-procgen-[contentType]-page.md`).
    *   **Content:** Define `objective` (e.g., "Create a web page that generates unique `[ContentType]` using `[AI Service/Mode]` on button click"), scope (simple UI, one generation type per page), desired tone/style for generated content. Set `status` to "Planned".

2.  **Select AI Service & Define Prompts (Feature):**
    *   **Goal:** Choose the specific LLM service/tool and craft the prompt(s) to elicit the desired content.
    *   **Action:** Define as a Feature (`FEAT-201-procgen-ai-setup-prompts.md`). Requires User input/creative direction, potentially refined by AI specialist.
    *   **Tasks (Examples):**
        *   "Identify the target `[AI Service/Mode]` (e.g., `vertex-ai-mcp-server/answer_query_direct`, `spec-openai`)." (User/Coordinator decision). **Verify prerequisites/configuration for the chosen service (e.g., MCP server running, API keys set for `spec-openai`).**
        *   "Draft 1-3 variations of the prompt `[Example LLM Prompt]` to generate the desired `[ContentType]`. Consider instructing the AI on length, style, and uniqueness." (User/Coordinator task, maybe delegate refinement to `util-writer` or AI specialist).
        *   "Document the chosen `[AI Service/Mode]` and final prompt(s) in the Feature file."
    *   **Output:** Finalized AI target and prompt(s). Set `status` to "Ready for Dev".

3.  **Basic Web Page Setup (Feature):**
    *   **Goal:** Create the minimal HTML/CSS/JS structure to host the generator.
    *   **Action:** Define as a Feature (`FEAT-202-procgen-page-setup.md`). Delegate tasks to `dev-general` or relevant framework specialist.
    *   **Tasks (Examples):**
        *   "Create `index.html` with a 'Generate' button (`button#generate-button`) and an output area (`div#output-area` or `pre`)."
        *   "Create basic `style.css`."
        *   "Create `script.js` and link it."
    *   **Process:** Use MDTM workflow. Mark Feature "Done".

## Phase 2: Frontend Implementation

1.  **Implement UI Interaction & AI Call (Feature):**
    *   **Goal:** Wire up the button to trigger the AI call and display the results.
    *   **Action:** Define as a Feature (`FEAT-203-implement-procgen-frontend-logic.md`). Delegate tasks to `dev-general` or framework specialist.
    *   **Tasks (Examples):**
        *   "In `script.js`, add event listener to `button#generate-button`."
        *   "On click: Display a loading indicator in `#output-area`."
        *   "On click: Prepare the chosen `[LLM Prompt]` from FEAT-201."
        *   "On click: Implement the call to `[AI Service/Mode]`: "
            *   *If MCP:* Construct the appropriate tool call XML for the MCP server (e.g., `<tool_code><tool_name>vertex-ai-mcp-server/answer_query_direct</tool_name><prompt>[LLM Prompt]</prompt></tool_code>`). Execute via Coordinator's tool execution mechanism (or potentially directly if the frontend framework allows safe MCP interaction).
            *   *If Specialist Mode (e.g., `spec-openai`):* Delegate via `new_task`: `<mode>spec-openai</mode><message>Execute prompt: '[LLM Prompt]'. Return only the generated text.</message>`. **Ensure API key security is handled appropriately by the specialist mode or backend proxy.**
        *   "Handle the asynchronous response from the AI service/mode."
        *   "On success: Clear loading state and display the received text content in `#output-area`."
        *   "On failure: Clear loading state and display an error message in `#output-area`."
    *   **Process:** Use MDTM workflow, linking tasks to the Feature. Prioritize secure credential handling if not using an MCP server.

## Phase 3: Styling & Refinement

1.  **Apply Styling (Tasks):**
    *   **Goal:** Improve the visual presentation of the page and generated content.
    *   **Action:** Add Tasks to Feature FEAT-203 or create a new one (`FEAT-204-procgen-styling.md`). Delegate to `design-tailwind`, `design-ui`, `dev-general`.
    *   **Tasks (Examples):**
        *   "Style the 'Generate' button."
        *   "Style the `#output-area` (e.g., font, padding, background)."
        *   "Style loading and error states."
        *   "Add basic page layout/centering."

2.  **Refine Prompts & Output Handling (Iterative):**
    *   **Goal:** Improve the quality and consistency of the generated content.
    *   **Action:** User tests generation. Provides feedback. Coordinator creates tasks to refine prompts (FEAT-201) or frontend display logic (FEAT-203).
    *   **Process:** This is an iterative loop based on results.

## Phase 4: Documentation & Completion

1.  **Write README:**
    *   **Goal:** Explain the demo, the AI service used, the prompts, and how to run it (including any setup like API keys or running the MCP server).
    *   **Action:** Define Task. Delegate to `util-writer`.
    *   **Process:** Create/update `README.md`.

2.  **Final Review & Completion:**
    *   **Action:** Review the working demo. Mark Features and the parent Epic/Feature as "Done".

## Key Considerations for Procedural Content Generation:

*   **AI Service Choice:** Different models/providers excel at different types of creative text. Choose one appropriate for the `[ContentType]`.
*   **API Key Security:** As highlighted before, directly using specialist modes like `spec-openai` from the frontend requires careful thought about API key exposure. Using a pre-configured, securely running MCP server (like the Vertex AI one) is generally safer as the keys are handled server-side.
*   **Prompt Engineering:** The quality, style, length, and uniqueness of the output are highly dependent on the prompt design. Experimentation is key.
*   **Cost & Rate Limits:** Be mindful of API costs and rate limits of the underlying LLM service. Add user-side delays or limits if generating rapidly.
*   **Output Formatting:** The LLM might return unwanted preamble/postamble text. Add frontend logic in `script.js` to clean up the response before displaying it, if necessary.
*   **User Experience:** Provide clear loading indicators and handle errors gracefully.

This playbook provides a structure for building web pages that showcase dynamic content generation using LLMs coordinated by Roo Commander.