+++
id = "PRIME-RULE-CMD-CONSTRAINT-V1"
title = "Prime Coordinator: Rule - Roo Commander Delegation Constraint"
context_type = "rules"
scope = "Constraint required when delegating tasks to roo-commander"
target_audience = ["prime"]
granularity = "snippet"
status = "active"
last_updated = "2025-04-21"
tags = ["rules", "constraint", "delegation", "safety", "roo-commander", "prime"]
related_context = ["01-operational-principles.md"]
+++

# Rule: Roo Commander Delegation Constraint

**Constraint Text:**

When delegating *any* task to the operational `roo-commander` mode using `new_task`, you **MUST** include the following explicit constraint within the `<message>` tag:

"**Constraint:** You MUST NOT modify files matching these patterns: `.roo/rules/**`, `.roo/rules-prime*/**`, `.modes/prime*/**`, `.roomodes*`, `build_*.js`, `create_build.js`."

**Rationale:** This prevents the operational commander from accidentally altering workspace standards or the Prime configuration files during its execution.