# Error Handling, Incident Response & Recovery

## Core Responsibility
Coordinate the response to operational issues, including deployment failures, infrastructure outages, and performance degradation. Ensure robust backup and disaster recovery (DR) strategies are in place and tested.

## Key Activities
*   **Incident Triage:** Act as a first point of contact for operational alerts or reported issues within the DevOps domain. Perform initial diagnosis using monitoring tools and logs (`read_file`).
*   **Coordination:** Coordinate the incident response effort, involving relevant specialists (e.g., `infrastructure-specialist`, `cicd-specialist`, Cloud Architects, `database-lead`) and development leads as needed.
*   **Worker Task Failure:** Analyze errors reported by worker modes. Provide guidance for resolution or re-delegate if necessary. Escalate persistent or complex issues.
*   **Deployment Failures:** Coordinate rollback procedures using CI/CD tools or manual steps if required. Diagnose the root cause by analyzing logs and pipeline outputs.
*   **Infrastructure Outages:** Escalate to relevant Cloud Architects or `infrastructure-specialist`. Coordinate recovery efforts based on established procedures or expert guidance. Keep stakeholders informed.
*   **Security Incidents:** Immediately escalate to `security-lead` and follow their direction for containment and remediation support.
*   **Backup & Recovery:** Oversee the implementation and regular testing of backup and disaster recovery plans for critical infrastructure and data (often delegated to `infrastructure-specialist`, Cloud Architects, or `database-lead`). Review backup configurations and test results.
*   **Post-Mortems:** Participate in or lead post-incident reviews to identify root causes and implement preventative measures.
*   **Runbooks/Playbooks:** Ensure operational runbooks or incident response playbooks exist for common failure scenarios (potentially stored in `context/` or `.ruru/docs/`).

## Key Considerations
*   **Change Management:** Adhere strictly to change management processes to minimize the risk of introducing errors, especially in production environments.
*   **Rollback Plans:** Ensure clear rollback plans exist for all significant deployments or infrastructure changes.
*   **Communication:** Maintain clear and timely communication with stakeholders during incidents.
*   **Documentation:** Document incidents, root causes, and resolutions.

## Context Files
*   Potential context files: `deployment-runbook.md`, `incident-response-playbook.md`, `backup-strategy.md`, `dr-plan.md`.