---
id: flo-m7pr
status: closed
deps: []
links: [flo-en6e]
created: 2026-03-26T18:00:00Z
type: task
priority: 2
assignee: legout
external-ref: .plans/2025-10-16/cleanup-refactor-plan-spec.md
tags: [tf, backlog, plan, component:cli, bug:low]
---
# Fix CLI broad exception handling catching KeyboardInterrupt

## Task
Change CLI command exception handlers from bare `except Exception` to exclude `KeyboardInterrupt` and `SystemExit`.

## Context
Every CLI command in `cli/pipeline.py` wraps its body in:
```python
except Exception as e:
    logger.error(f"Pipeline execution failed: {e}")
    raise typer.Exit(1)
```
This catches `KeyboardInterrupt` (Ctrl+C) and `SystemExit`, preventing clean cancellation. Users pressing Ctrl+C during a long pipeline run would see an error message instead of a clean exit.

## Acceptance Criteria
- [ ] All CLI command handlers use `except (ValueError, RuntimeError, FileNotFoundError, ...)` instead of bare `except Exception`.
- [ ] `KeyboardInterrupt` and `SystemExit` propagate normally (not caught).
- [ ] Ctrl+C during `pipeline run` produces a clean exit without error logging.

## References
- Plan: .plans/2025-10-16/cleanup-refactor-plan-spec.md
- Analysis: .plans/2026-03-26/deep-analysis-and-refactoring-plan.md — Finding #28

## Notes

**2026-04-01T10:00:00Z**

AUDIT: Status changed from closed → open. The fix was **never implemented**:

- `cli/pipeline.py` still uses `except Exception as e:` in all command handlers (lines 217, 229, 440, 511, 742).
- KeyboardInterrupt and SystemExit are still caught, preventing clean Ctrl+C handling.

**2026-05-02T21:17:03Z**

Gate: PASS — Replaced 5 bare `except Exception` in cli/pipeline.py with specific tuples ((ValueError, TypeError) for executor config; (RuntimeError, TypeError) for run/show-dag/save-dag/add-hook fallbacks). Added 5 unit tests (all pass) covering KeyboardInterrupt/SystemExit propagation and narrowed exception catching. Structural AST test guards against regression. grep confirms 0 bare except Exception remaining. 14/14 existing CLI tests pass (2 pre-existing integration failures unrelated). Review not run.
