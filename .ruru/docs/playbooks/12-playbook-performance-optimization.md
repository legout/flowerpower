+++
# --- Metadata ---
id = "PLAYBOOK-PERF-OPT-V1"
title = "Project Playbook: Performance Optimization Audit & Fix"
status = "published"
created_date = "2025-04-24"
updated_date = "2025-04-24"
version = "1.0"
tags = ["playbook", "documentation", "project-management", "performance", "optimization", "audit", "profiling", "frontend", "backend", "database", "epic", "feature", "task"]
related_docs = [
    ".ruru/docs/standards/project-management-strategy-v1.md",
    ".ruru/planning/project-structure/00-epic-feature-task-plan.md",
    ".ruru/modes/util-performance/util-performance.mode.md",
    ".ruru/modes/lead-frontend/lead-frontend.mode.md",
    ".ruru/modes/lead-backend/lead-backend.mode.md",
    ".ruru/modes/lead-db/lead-db.mode.md",
    ".ruru/modes/agent-research/agent-research.mode.md" # For researching tools/techniques
]
objective = "Provide a structured process for identifying, analyzing, implementing fixes for, and verifying performance bottlenecks across frontend, backend, and database layers using the Roo Commander Epic-Feature-Task hierarchy."
scope = "Covers establishing performance goals, baseline measurement, bottleneck analysis using various tools, implementing targeted optimizations, and verifying impact."
target_audience = ["Users", "Developers", "Architects", "DevOps Engineers", "AI Modes"]
# --- Document Specific Fields ---
example_project_type = "Existing Web/Mobile/Backend Application experiencing slowness"
optimization_area_placeholder = "[SpecificArea]" # e.g., "Initial Page Load", "API Endpoint X", "Dashboard Query"
metric_placeholder = "[Metric]" # e.g., "LCP", "API P95 Latency", "Query Execution Time"
tool_placeholder = "[AnalysisTool]" # e.g., "Lighthouse", "Browser DevTools", "APM", "Database EXPLAIN"
+++

# Project Playbook: Performance Optimization Audit & Fix

This playbook outlines a recommended approach for systematically identifying and addressing performance issues in an existing application using Roo Commander's Epic-Feature-Task hierarchy. Performance optimization is often an iterative process of measure, analyze, fix, and verify.

**Scenario:** Users are reporting slowness, infrastructure costs are rising due to inefficiency, or specific performance targets (SLOs/SLAs) are not being met.

## Phase 1: Goal Setting & Baseline Measurement

1.  **Define the Optimization Initiative (Epic):**
    *   **Goal:** Establish the high-level objective and scope of the performance improvement effort.
    *   **Action:** Create the main Epic (e.g., `.ruru/epics/EPIC-035-improve-application-performance-q3.md`).
    *   **Content:** Define `objective` (e.g., "Reduce user-perceived latency for key workflows and decrease backend resource consumption"), `scope_description` (e.g., "Focus on initial page load, product search API, and user dashboard queries"), context (user reports, SLO targets). Set `status` to "Planned".

2.  **Establish Baselines & Define Targets (Feature):**
    *   **Goal:** Quantify the *current* performance and set *specific, measurable* improvement goals. This is critical for knowing if optimizations are effective.
    *   **Action:** Define as a Feature (`FEAT-120-perf-baseline-and-targets.md`). Delegate tasks to relevant leads and `util-performance`.
    *   **Tasks (Examples):**
        *   "Measure current Frontend metrics (LCP, FCP, TTI) for key pages using Lighthouse/WebPageTest." (Delegate to `lead-frontend`)
        *   "Measure current API response time (Avg, P95, P99) for critical endpoints (e.g., `/api/search`, `/api/dashboard`) using APM tool." (Delegate to `lead-backend`)
        *   "Identify and measure execution time of slowest database queries during peak load using DB monitoring/logs." (Delegate to `lead-db`)
        *   "Define target metrics based on user impact and SLOs (e.g., LCP < 2.5s, API P95 < 400ms, Query X < 100ms)." (Coordinate with user/product owner). Document targets in Feature/Epic.
        *   "Set up performance monitoring/dashboards (if not already in place)." (Delegate to `lead-devops`)
    *   **Output:** Baseline measurements recorded (e.g., in `.ruru/reports/performance/`), specific targets documented in the Feature/Epic. Update Feature status to "Done".

## Phase 2: Bottleneck Analysis (Iterative Features per Area)

*For each `[SpecificArea]` identified as needing optimization based on baseline data:*

1.  **Define Analysis Feature:**
    *   **Goal:** Investigate the root cause of slowness in the `[SpecificArea]`.
    *   **Action:** Create a Feature (e.g., `FEAT-121-analyze-[SpecificArea]-performance.md`). Set `status` to "Ready for Dev". Decompose into Tasks.

2.  **Execute Analysis Tasks:**
    *   **Goal:** Use appropriate tools to pinpoint the bottleneck(s).
    *   **Action:** Delegate analysis tasks to relevant specialists (`util-performance`, leads, framework specialists).
    *   **Tasks (Examples):**
        *   *(Frontend Load):* "Analyze Network waterfall chart in Browser DevTools for [Page X]."
        *   *(Frontend Load):* "Analyze bundle composition using Webpack Bundle Analyzer / `source-map-explorer`."
        *   *(Frontend Runtime):* "Profile component rendering times using React/Vue/etc. DevTools."
        *   *(Backend API):* "Trace `/api/[endpoint]` request using APM tool to identify slow spans (DB, external calls, code execution)."
        *   *(Database Query):* "Run `EXPLAIN ANALYZE` on query [Query ID/Text] and interpret the plan."
        *   *(Infrastructure):* "Check CPU/Memory/Network utilization on relevant servers/containers during peak load."
    *   **Process:** Use MDTM workflow. Specialists document findings, profile results, and specific bottleneck hypotheses within their `TASK-...md` files or linked analysis notes.

3.  **Synthesize Findings & Prioritize Fixes:**
    *   **Goal:** Collate analysis results and identify the most impactful optimizations to implement first.
    *   **Action:** Task for `util-performance` or Lead to review analysis tasks for the Feature.
    *   **Output:** Update the Feature (`FEAT-...-analyze-...`) description with summarized findings and prioritized hypotheses for fixes. Mark Feature as "Done".

## Phase 3: Implementing Optimizations (Features or Tasks per Fix)

1.  **Define Optimization Feature/Task:**
    *   **Goal:** Describe the specific optimization to be implemented based on Phase 2 findings.
    *   **Action:** Create a Feature (if complex) or directly a Task (if simple) for the fix (e.g., `FEAT-125-implement-api-caching-for-search.md` or `TASK-...-add-db-index-for-users-table.md`). Link to the Analysis Feature/Task and overall Epic.
    *   **Content:** Clearly state the change (e.g., "Add Redis caching layer", "Implement code splitting", "Add database index", "Optimize image formats/sizes") and the expected outcome (referencing target metrics).

2.  **Implement Optimization Task(s):**
    *   **Goal:** Apply the specific performance fix.
    *   **Action:** Decompose the Optimization Feature into Tasks (if needed) and delegate to appropriate specialists (`lead-backend`, `lead-frontend`, `lead-db`, `framework-*`, `infra-*`).
    *   **Process:** Use MDTM workflow. Implementation MUST include verification steps:
        *   Running relevant unit/integration tests to ensure *no functional regressions* were introduced.
        *   Local testing/profiling to get an initial sense the optimization is working as intended.

## Phase 4: Verification & Measurement

1.  **Measure Impact (Task):**
    *   **Goal:** Quantify the performance change after the optimization is deployed (ideally to a staging environment first).
    *   **Action:** Create a Task linked to the Optimization Feature/Task. Delegate to the same specialist/tool used for the baseline measurement in Phase 1.
    *   **Process:** Re-run the specific performance measurement (Lighthouse, API load test, DB query timing) related to the optimization. Record the new measurement.

2.  **Compare & Analyze Results:**
    *   **Goal:** Determine if the optimization met its target and didn't negatively impact other areas.
    *   **Action:** Task for `util-performance` or Lead.
    *   **Process:** Compare the new measurement against the baseline (Phase 1) and the target goal. Analyze if the improvement is significant and if any other metrics regressed unexpectedly. Document findings in the Task/Feature.

3.  **Iterate or Complete:**
    *   **If Goal Met:** Mark the Optimization Feature/Task as "Done". Update the main Epic's progress.
    *   **If Goal Not Met (or new bottlenecks found):** Either create further optimization tasks for this area OR return to Phase 2 (Analysis) to investigate deeper or explore alternative solutions.
    *   **If Regressions Introduced:** Create bug-fix tasks (`dev-fixer`) to address the regressions before marking the optimization as complete.

## Phase 5: Documentation & Monitoring

1.  **Document Changes:**
    *   **Goal:** Record what was changed, why, and the measured impact.
    *   **Action:** Create/update documentation (e.g., in `.ruru/docs/performance/`, linked ADRs, or within the completed Feature/Epic files) detailing the optimization, baseline vs. final metrics, and any key learnings. Delegate to `util-writer`.

2.  **Ongoing Monitoring:**
    *   **Goal:** Ensure performance gains are maintained over time.
    *   **Action:** Verify that performance monitoring dashboards (setup in Phase 1) reflect the improvements and configure alerts for future regressions if possible. (Task for `lead-devops`).

## Key Considerations for Performance Optimization:

*   **Measure First:** Don't optimize without baseline data and clear goals. Guesswork often leads to wasted effort.
*   **Focus on Bottlenecks:** Target the areas identified through analysis that have the biggest impact. Premature optimization is the root of much evil.
*   **Iterate:** Performance work is rarely a one-shot fix. Apply changes incrementally and measure often.
*   **Test for Regressions:** Performance fixes must not break functionality. Run unit, integration, and E2E tests after changes.
*   **Consider Trade-offs:** Optimizations might involve trade-offs (e.g., increased memory for faster CPU, increased complexity for better load times). Document these trade-offs (ADRs are good for this).
*   **Use the Right Tools:** Leverage browser devtools, APM (Application Performance Monitoring) tools, database query planners (`EXPLAIN`), load testing tools, and profilers specific to your language/framework.

This playbook provides a systematic way to tackle performance issues, ensuring changes are data-driven and verified.