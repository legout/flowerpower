# Django: Collaboration & Escalation

Guidelines for interacting with other modes and escalating tasks.

## Invocation

*   This mode (`django-developer`) should typically be invoked by discovery agents or coordinators when Django projects are detected (e.g., presence of `manage.py`, Django in `requirements.txt` or `pyproject.toml`).

## Collaboration

Work closely with:

*   **Frontend Developer / Framework Specialists** (React, Vue, Angular, Svelte, etc.): For integrating the Django backend with separate frontends, often via APIs built with DRF (see `13-drf-basics.md`). Define API contracts clearly.
*   **API Developer:** For complex API integrations or if DRF expertise is insufficient for specific requirements (e.g., non-standard protocols, advanced GraphQL).
*   **Database Specialist:** For advanced schema design, complex migrations, performance tuning beyond standard ORM optimization (`select_related`/`prefetch_related`).
*   **Infrastructure Specialist / CI/CD Specialist / DevOps Lead:** For deployment pipelines, server setup, environment configuration, monitoring.
*   **Containerization Developer / Docker Compose Specialist:** For Dockerizing the Django application and managing container orchestration.
*   **Testing modes (E2E Tester, Integration Tester):** For comprehensive testing strategies beyond unit/integration tests within Django's framework.
*   **Security Specialist:** For security reviews, implementing advanced security measures, or handling security incidents.

## Escalation / Delegation

Escalate or delegate tasks outside core Django/DRF expertise:

*   **Frontend Implementation** (beyond basic Django templates) -> Relevant Frontend Specialist.
*   **Complex Database Optimization/Design** (beyond standard ORM usage) -> Database Specialist.
*   **Deployment/Infrastructure Setup** -> Infrastructure Specialist / CI/CD Specialist / DevOps Lead.
*   **Containerization** (Dockerfiles, orchestration) -> Containerization Developer / Docker Compose Specialist.
*   **Highly Complex/Specialized API Design** (if requirements exceed DRF capabilities or involve niche protocols) -> API Developer.
*   **UI/UX Design** -> UI Designer / Design Lead.
*   **Advanced Security Audits/Implementation** -> Security Specialist.

## Reporting

*   Report task progress and completion to the invoking coordinator (e.g., `roo-commander`, `technical-architect`, `project-manager`).
*   Reference the relevant task log file (e.g., `.ruru/tasks/[TaskID].md`) in completion reports.