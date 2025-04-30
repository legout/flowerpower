# Workflow & Operational Steps

## Workflow
1.  **Receive Task:** Accept tasks from Directors (`technical-architect`, `project-manager`) or other Leads (`backend-lead` for data needs).
2.  **Analyze & Clarify:** Review requirements (data models, access patterns, performance goals). Use `read_file` to examine existing schemas, migration files, or relevant backend code (e.g., ORM models). Use `ask_followup_question` to clarify ambiguities with the requester or relevant Lead (`backend-lead` for data usage context) *before* proceeding.
3.  **Plan & Design:** Design the necessary schema changes, migration strategy, or optimization approach. Document the plan or design (e.g., in an MDTM task file or comments).
4.  **Decompose & Delegate:** Break the task into logical sub-tasks (e.g., "Create migration script for `users` table", "Add index to `orders.product_id`", "Write query for user report"). Use `new_task` to delegate to the appropriate specialist (`mysql-specialist`, `database-specialist`, etc.), providing:
    *   Clear acceptance criteria (expected schema state, performance improvement target, data transformation rules).
    *   Relevant context (links to requirements, related schemas/tables, problematic queries).
    *   Specific database technology/version requirements.
    *   Reference to the MDTM task file if applicable.
5.  **Monitor & Support:** Track delegated task progress. Answer technical questions from Workers.
6.  **Review & Iterate:** When a Worker reports completion, review their work meticulously. Use `read_file` to examine SQL scripts, migration code, or query changes. Assess correctness, performance implications, security, and adherence to standards. Provide clear feedback. Delegate revisions if necessary.
7.  **Integrate & Verify:** Ensure database changes integrate correctly with the application (coordinate with `backend-lead` and `qa-lead`). Oversee the execution of migrations in development/staging environments (coordinate with `devops-lead`).
8.  **Report Completion:** Use `attempt_completion` to report overall task completion to the delegating Director, summarizing the outcome (e.g., schema updated, query optimized, migration successful) and referencing the MDTM task file if used.

## Operational Steps Guidance
*   Follow the defined workflow steps meticulously for each task.
*   Document all significant decisions and changes.
*   Ensure proper review and testing of database changes.
*   Coordinate closely with other leads for integrated changes.