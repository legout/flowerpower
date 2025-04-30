+++
# --- Metadata ---
id = "PLAYBOOK-RESEARCH-POC-V1"
title = "Project Playbook: Research & Prototyping"
status = "published"
created_date = "2025-04-24"
updated_date = "2025-04-24"
version = "1.0"
tags = ["playbook", "documentation", "project-management", "research", "prototyping", "poc", "feasibility", "epic", "feature", "task"]
related_docs = [
    ".ruru/docs/standards/project-management-strategy-v1.md",
    ".ruru/planning/project-structure/00-epic-feature-task-plan.md",
    ".ruru/modes/agent-research/agent-research.mode.md",
    ".ruru/modes/core-architect/core-architect.mode.md"
]
objective = "Provide a structured approach for conducting research, exploring new technologies, and building proofs-of-concept (PoCs) using the Roo Commander Epic-Feature-Task hierarchy."
scope = "Covers defining research goals, conducting investigations, building experimental prototypes, and documenting findings and recommendations."
target_audience = ["Users", "Architects", "Developers", "Researchers", "AI Modes"]
# --- Document Specific Fields ---
example_project_type = "Technology evaluation, Feasibility study, New algorithm exploration, Proof-of-concept development"
+++

# Project Playbook: Research & Prototyping

This playbook outlines a recommended approach for structuring and managing research and prototyping projects using Roo Commander. The goal is often learning, validation, or demonstrating feasibility rather than creating production-ready code.

**Scenario:** You need to investigate a new technology, explore a different architectural approach, test the feasibility of an idea, or build a small proof-of-concept (PoC).

## Phase 1: Defining the Research Goal

1.  **Initiate Research Request:**
    *   Start by explaining the research goal to `roo-commander`. Use the "❓ Research a topic / Ask a technical question" or "💡 Plan/Design..." or "🤔 Something else..." initial options.
    *   Clearly state the primary question, technology to explore, or hypothesis to test.

2.  **Define the Research Scope (Epic or Feature):**
    *   **Goal:** Create a central artifact to track the overall research initiative.
    *   **Action:** Work with `roo-commander`, `core-architect`, or `agent-research` lead.
        *   For larger explorations (e.g., "Evaluate alternative state management solutions"), create an Epic (`.ruru/epics/EPIC-...). Define the `objective` (e.g., "Determine the best state management library for Project X based on performance, developer experience, and feature set") and `scope_description`.
        *   For smaller, focused investigations or PoCs (e.g., "Build PoC for using WebSockets for real-time updates"), a single Feature (`.ruru/features/FEAT-...`) might suffice initially. Define `description` and `acceptance_criteria` (which might be "Demonstrate basic functionality" or "Produce a comparison report"). Link to an Epic if applicable.
    *   Set initial `status` to "Research" or "Planned".

## Phase 2: Investigation & Information Gathering

1.  **Break Down Research Questions (Features/Tasks):**
    *   **Goal:** Decompose the high-level research goal into specific questions, areas to investigate, or experiments to run.
    *   **Action:** Define these as Features (if large enough) or directly as Tasks under the main Research Feature/Epic.
    *   **Feature Examples (under "Evaluate Vector DBs" Epic):**
        *   `FEAT-040-research-qdrant-features.md`
        *   `FEAT-041-research-weaviate-features.md`
        *   `FEAT-042-performance-test-setup.md`
    *   **Task Examples (under "Research Qdrant Features" Feature):**
        *   "Research Qdrant indexing strategies and parameters via docs/web." (Assign to `agent-research`)
        *   "Summarize Qdrant filtering capabilities." (Assign to `agent-research`)
        *   "Find tutorials on setting up Qdrant with Docker." (Assign to `agent-research`)

2.  **Execute Research Tasks:**
    *   **Goal:** Gather information from documentation, articles, code repositories, etc.
    *   **Action:** Delegate research tasks primarily to `agent-research`.
    *   **Process:** Follow MDTM workflow (Rule `04`). Tasks should clearly state the research question. `agent-research` uses tools (`browser`, `fetch`) and produces summaries or reports, saving them potentially to `.ruru/docs/research/` or linking them in the task file. Ensure `feature_id`/`epic_id` are linked.

## Phase 3: Prototyping (If Applicable)

1.  **Define Prototype Scope (Feature/Tasks):**
    *   **Goal:** If building a PoC, define the minimal scope required to test the core hypothesis or demonstrate feasibility. This might be a Feature itself.
    *   **Action:** Break down the PoC into small, buildable tasks.

2.  **Implement Prototype Tasks:**
    *   **Goal:** Build the experimental code.
    *   **Action:** Delegate coding tasks to relevant specialists (`util-senior-dev`, framework specialists, data specialists).
    *   **Process:** Follow MDTM workflow. Emphasize that this is *prototype* code – focus on speed and demonstrating the concept over production-level quality (unless specifically required). Code might live in a separate branch or directory (e.g., `/prototypes/`). Ensure tasks link to the PoC Feature/Epic.

3.  **Experimentation & Iteration:**
    *   **Goal:** Run experiments, measure results (if applicable), and iterate on the prototype based on findings.
    *   **Action:** Define tasks for running tests, gathering metrics, or making specific modifications to the prototype based on research outcomes. Delegate as needed.

## Phase 4: Analysis, Documentation & Recommendation

1.  **Synthesize Findings:**
    *   **Goal:** Consolidate research notes, prototype results, and experimental data.
    *   **Action:** Assign a task to `agent-research`, `util-writer`, or `core-architect` to read through relevant task logs, research reports (`.ruru/docs/research/`), and potentially prototype code (`read_file`).
    *   **Process:** Create a summary document (e.g., `.ruru/docs/research/[topic]-summary.md` or within the main Epic/Feature file).

2.  **Formulate Conclusion/Recommendation:**
    *   **Goal:** Answer the initial research question or determine the outcome of the PoC.
    *   **Action:** Based on the synthesized findings, work with `core-architect` or relevant leads to draw conclusions.
        *   Is the technology feasible?
        *   What are the pros and cons?
        *   What are the recommended next steps (e.g., adopt, reject, further research needed)?
    *   Document this conclusion clearly in the summary report or the main Epic/Feature file.

3.  **Create ADR (If Necessary):**
    *   **Goal:** Formalize significant decisions resulting from the research.
    *   **Action:** If the research leads to a decision to adopt or reject a technology/architecture for the main project, create an ADR (`.ruru/decisions/`) documenting the decision, rationale, and consequences, linking it back to the Research Epic/Feature.

4.  **Update Artifact Status:**
    *   **Action:** Mark the relevant Tasks, Features, and the main Epic (if applicable) as "Done" or "On Hold" based on the outcome.

## Key Considerations for Research/Prototyping:

*   **Clear Goals:** Even exploratory work benefits from a clear initial question or hypothesis.
*   **Timeboxing:** Research can be open-ended. Consider setting time limits or specific deliverable goals for tasks/features.
*   **Documentation:** Emphasize documenting findings *as you go* within task files or dedicated research notes. The final synthesis step is easier with good intermediate documentation.
*   **Prototype Scope:** Keep PoCs focused on the core question. Avoid over-engineering. The goal is learning or validation, not production code.
*   **Outcome Flexibility:** Be prepared for the outcome to be "this approach is not viable" – that's still a valuable result.

This playbook provides a flexible structure for managing the inherent uncertainty in research and prototyping while ensuring findings are captured and decisions are documented.