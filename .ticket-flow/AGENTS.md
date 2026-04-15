# pi-ticket-flow Workflow

Use this repository's ticket-flow workflow for planning and ticket execution.

## ExecPlans

When writing complex features or significant refactors, use an ExecPlan (as described in `.ticket-flow/PLANS.md`) from design to implementation.

## Planning workflow

- Use `/plan <topic>` to go from brainstorming through ExecPlan creation.
- Use `/plan-chain <topic>` only when brainstorming is already complete and the remaining planning steps are non-interactive.
- ExecPlans live at `.ticket-flow/plans/<topic-slug>/execplan.md`.
- Brainstorms live at `.ticket-flow/plans/<topic-slug>/brainstorm.md`.

## Ticket workflow

- Use `tk` for ticket tracking.
- Use `/ticketize <topic>` to convert an ExecPlan into tk tickets.
- Use `/ticket-flow` for one-ticket delegated execution.
- Use `/ticket-queue` for sequential batch execution.
- Use `/ticket-reset` to clear stale orchestrator state.

## Artifact locations

- `ticket-flow/current.md`
- `ticket-flow/<ticket-id>/implementation.md`
- `ticket-flow/<ticket-id>/review.md`
- `ticket-flow/progress.md`
- `ticket-flow/lessons-learned.md`

## Ticket guidance

- If a ticket contains an `ExecPlan Reference` block, read the referenced ExecPlan before implementing or reviewing.
- Keep ExecPlans and architecture documentation aligned with reality as work progresses.
