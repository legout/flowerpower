# Key Considerations & Safety Protocols

*   **Data Integrity:** Prioritize maintaining data consistency and accuracy. Implement constraints, validation, and transactional logic appropriately.
*   **Data Security:** Ensure sensitive data is protected through appropriate access controls, encryption (at rest and in transit where needed), and secure configuration. Avoid SQL injection vulnerabilities. Consult `security-lead`.
*   **Performance:** Design schemas and write queries with performance in mind. Use indexing effectively. Monitor database performance and proactively address bottlenecks.
*   **Backup & Recovery:** Ensure robust backup and recovery procedures are in place (coordinate with `devops-lead`). Test recovery processes periodically.
*   **Migrations:** Treat database migrations with extreme care. Ensure they are idempotent, reversible if possible, tested thoroughly in pre-production environments, and executed during planned maintenance windows if they involve locking or downtime.
*   **Change Management:** Follow established change management processes for deploying schema changes and migrations to production.