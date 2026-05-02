<!-- execflow-generated -->
# pi-execflow Workflow

Use this repository's execflow workflow for planning and ticket execution.

Primary tracker selected during init-execflow: `tk`

## ExecPlans

When writing complex features or significant refactors, use an ExecPlan (as described in `.execflow/PLANS.md`) from design to implementation.

## Planning workflow

- Use `/init-execflow [--tk|--br]` to scaffold planning files and initialize the chosen tracker.
- Use `/sync-models` after editing `.execflow/settings.yml` to sync `.pi/prompts/` frontmatter.
- Treat `.execflow/settings.yml` `prompts:` as the source of truth for model-owning leaf prompts only; wrapper prompts like `/plan`, `/plan-chain`, `/ef-implement`, `/ef-implement-delegated`, `/refresh-prompts`, and `/sync-models` are intentionally omitted.
- Prompt taxonomy:
  - wrappers without model ownership: `/plan`, `/plan-chain`, `/ef-implement`, `/ef-implement-delegated`, `/refresh-prompts`, `/sync-models`
  - local model-owning leaves: planning/execution/review prompts such as `/architect`, `/plan-create`, `/implementation-plan`, `/validation-plan`, `/implement`, `/validation-fix`, `/ef-review`, `/ef-review-followups`, `/execplan-review`, `/execplan-review-followups`, `/change-review`, `/change-review-followups`
  - delegated model-owning leaves: `/worker-implement`, `/worker-validation-fix`
  - deterministic + LLM setup leaf: `/init-execflow`
- Use `/brainstorm <topic>` to explore the problem before locking a design.
- Use `/plan <topic>` to go from brainstorming through ExecPlan creation.
- Use `/plan-chain <topic>` only when brainstorming is already complete and the remaining planning steps are non-interactive.
- Use `/architect [topic]` to create or refresh `ARCHITECTURE.md` when the codebase context matters.
- ExecPlans live at `.execflow/plans/<topic-slug>/execplan.md`.
- Brainstorms live at `.execflow/plans/<topic-slug>/brainstorm.md`.

## Tracker workflow

### br mode

- Use `br` for issue tracking.
- Use `/create-work-items <topic>` to auto-select the primary tracker.
- Use `/create-issues <topic>` to convert an ExecPlan into dependency-aware `br` issues.
- Use `/ef-implement <issue-ref>` for fast validation-only implementation: `/implement` edits code/tests without running validation commands, then `/validation-fix` owns bounded validation/fix looping before finalization.
- Use `/ef-implement-delegated <issue-ref>` for larger/noisier work: parent-owned planning/finalization with worker-subagent implementation and validation/fix.
- Use `/ef-review <issue-ref>` for a fresh read-only focused work-item review. Use `/ef-review-followups <issue-ref>` to record the review and create linked follow-up issues, or pass `--create-followups` to `/ef-review` when mutation is explicitly desired.
- Use `/execplan-review <plan> [--create-followups]` for whole-plan delivery audits across derived issues/tickets.
- Use `/change-review [--base <ref>] [--create-followups]` for broad arbitrary branch/diff/path reviews.
- Use focused local prompts (`/resolve`, `/spec`, `/implement`, `/validation-fix`, `/validate`, `/fix`, `/finalize`) for narrower manual passes.
- Optional external delegated `/execflow-queue` commands, when available in the environment, are `tk`-oriented and should not be treated as the primary `br` execution path.

### tk mode

- Use `tk` for ticket tracking when the repository explicitly chooses it.
- Use `/create-work-items <topic>` to auto-select the primary tracker.
- Use `/create-tickets <topic>` to convert an ExecPlan into dependency-aware `tk` tickets.
- Use `/ef-implement <ticket-ref>` for fast validation-only implementation: `/implement` edits code/tests without running validation commands, then `/validation-fix` owns bounded validation/fix looping before finalization.
- Use `/ef-implement-delegated <ticket-ref>` for larger/noisier work: parent-owned planning/finalization with worker-subagent implementation and validation/fix.
- Use `/ef-review <ticket-ref>` for a fresh read-only focused work-item review. Use `/ef-review-followups <ticket-ref>` to record the review and create linked follow-up tickets, or pass `--create-followups` to `/ef-review` when mutation is explicitly desired.
- Use `/execplan-review <plan> [--create-followups]` for whole-plan delivery audits across derived issues/tickets.
- Use `/change-review [--base <ref>] [--create-followups]` for broad arbitrary branch/diff/path reviews.
- If your environment provides the optional external delegated `tk` workflow, use `/execflow-queue` for sequential batch execution.
- If your environment provides the optional external delegated `tk` workflow, use `/execflow-reset` to clear stale orchestrator state.

## Artifact locations

### Planning artifacts

- `.execflow/plans/<topic-slug>/brainstorm.md`
- `.execflow/plans/<topic-slug>/execplan.md`
- `.execflow/settings.yml`
- `.pi/prompts/*.md`
- `ARCHITECTURE.md`

### Optional delegated runtime artifacts (`tk` delegated flow only)

- `execflow/state.json`
- `execflow/<ticket-id>/implementation-<run-token>.md`
- `execflow/<ticket-id>/validation-<run-token>.md`
- `execflow/<ticket-id>/review-<run-token>.md`
- `execflow/progress.md`
- `execflow/lessons-learned.md`

## Work-item guidance

- If a ticket or issue contains an `ExecPlan Reference` block, read the referenced ExecPlan before implementing or reviewing.
- `/ef-implement` closure means validation passed and acceptance criteria were met; it does not imply independent review.
- `/ef-implement-delegated` uses prompt-template subagent frontmatter and requires `PI_SUBAGENT_RUNTIME_ROOT` when `pi-subagents` is installed as a package outside `~/.pi/agent/extensions/subagent`.
- Track reviews by adding review summary comments/notes to the original item and creating linked follow-up items from `/ef-review-followups`, `/execplan-review-followups`, or `/change-review-followups` when material findings exist.
- Keep ExecPlans and architecture documentation aligned with reality as work progresses.
<!-- /execflow-generated -->
