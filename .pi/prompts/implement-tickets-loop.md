# Ticket Implementation Loop

You are implementing tickets from the flowerpower refactoring plan. Execute this loop until `tk ready` returns empty.

## Per-Ticket Cycle

### 1. Pick the next ticket
```bash
tk ready | head -1
```
Parse the ticket ID from the output. If no output, **stop** — all tickets are done.

### 2. Start the ticket
```bash
tk start <id>
```

### 3. Read the ticket and build context
```bash
tk show <id>
```
Read the ticket's `external-ref` and `Analysis` references from its References section — those are plan docs in `.plans/`. Read those files. Then read every source file the ticket touches.

### 4. Spawn a worker subagent to implement
Use the `worker` agent. Give it:
- The full ticket content (task, context, acceptance criteria)
- The relevant plan/analysis doc excerpts
- A list of files to read and modify
- Instructions to write a progress.md when done

The subagent should:
- Read all relevant source files first
- Implement the changes per the acceptance criteria
- Run a quick smoke check (`python -c "import flowerpower"`) if it touched imports
- Write a concise progress.md listing every file changed and what changed

### 5. Code review — spawn a reviewer subagent
Use the `reviewer` agent. Give it:
- The ticket's acceptance criteria
- The list of changed files (from progress.md)
- Instructions to do a focused review of only the changes (use `git diff`)

The reviewer outputs a review with severity-tagged issues.

### 6. Fix review issues — spawn a fixer subagent (if needed)
If the review found Critical or Major issues, use the `fixer` agent with the review output and the ticket context. Have it fix issues and update progress.md.

### 7. Run linters
```bash
ty check
mypy
```
If either fails, spawn the `fixer` agent with the lint output and have it fix the issues. Re-run the linters until clean.

### 8. Run tests
```bash
pytest
```
If tests fail, analyze the output yourself. If the failures are clearly caused by the ticket's changes, spawn the `fixer` agent with the test output. Re-run until all tests pass.

### 9. Close the ticket
```bash
tk close <id>
```

### 10. Go to step 1

## Rules

- **One ticket at a time.** Never work on multiple tickets in parallel.
- **Fresh subagent per step.** Each worker/reviewer/fixer gets a fresh context. Never reuse a subagent across tickets.
- **Do not skip steps.** Even if a ticket looks trivial, still do review → lint → test.
- **If blocked**, add a note to the ticket (`tk add-note <id> "blocked because..."`) and move to the next ready ticket.
- **If a ticket's dependencies aren't actually resolved** (i.e., `tk ready` shows it but the prerequisite code isn't there), that's a bug — add a note and skip it.
- **Preserve the existing code style.** This is a Python project using msgspec structs, typer CLI, and Rich console output.
- **Don't over-engineer.** If the acceptance criteria say "remove X", just remove X — don't also refactor Y.
