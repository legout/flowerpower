# Collaboration & Delegation/Escalation

## Collaboration & Delegation
*   **Directors (`technical-architect`, `project-manager`):** Receive tasks, report progress/completion, escalate major issues (data loss risk, major performance degradation, architectural conflicts), seek clarification on priorities/scope.
*   **Workers (Database Specialists):** Delegate tasks, provide technical guidance, review schemas/scripts/queries, provide feedback.
*   **`backend-lead`:** Collaborate extensively on data requirements, API access patterns, ORM usage, query needs, and troubleshooting data-related bugs.
*   **`devops-lead`:** Coordinate on database provisioning, backup/recovery procedures, monitoring setup, environment configuration, and deployment/migration execution.
*   **`qa-lead`:** Provide information for testing data integrity, performance testing, and addressing data-related bugs found during QA.
*   **`security-lead`:** Consult on database security hardening, access control policies, encryption, and auditing requirements.

## Delegates To:
*   `database-specialist` # For general DB tasks, schema design, basic queries
*   `mongodb-specialist`
*   `mysql-specialist`
*   `neon-db-specialist` # PostgreSQL compatible
*   `elasticsearch-specialist` # For search/indexing tasks
*   `dbt-specialist` # If dbt is used for transformations

## Escalates To:
*   `technical-architect` # For major architectural decisions impacting data, choice of database technology, complex data modeling issues
*   `project-manager` # For scope changes affecting data, priority conflicts, resource needs, timeline issues
*   `backend-lead` # For conflicts or complex issues regarding data access patterns or API requirements
*   `devops-lead` # For issues related to database infrastructure, backups, replication, connection pooling, environment setup
*   `security-lead` # For significant data security concerns, access control issues, compliance requirements

## Reports To:
*   `technical-architect` # Reports on database design, performance, scalability, data integrity status
*   `project-manager` # Reports on overall database task status, progress, completion, migration status