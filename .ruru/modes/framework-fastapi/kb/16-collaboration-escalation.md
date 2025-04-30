# 16. Collaboration & Escalation

## Proactive Identification

-   Based on the task requirements and the project's Stack Profile, identify if parts of the task fall outside core FastAPI expertise.

## Escalate When Necessary

-   **Database Interactions:** For complex database design, migrations, or advanced ORM usage beyond standard patterns (e.g., complex queries, performance tuning), escalate to `database-specialist`.
-   **Authentication/Authorization:** For complex security logic, custom auth flows, or integration with specific providers (e.g., OAuth2 details, SSO), escalate to `security-specialist` or a provider-specific mode (e.g., `clerk-auth-specialist`, `supabase-auth-specialist`).
-   **Frontend Integration:** For issues related to how the frontend consumes the API (e.g., client-side state management, framework-specific data fetching), escalate to the relevant frontend mode (e.g., `react-specialist`, `vuejs-developer`).
-   **Deployment/Infrastructure:** For deployment pipelines, containerization (Docker), server configuration (Nginx/Gunicorn), or cloud infrastructure setup, escalate to `infrastructure-specialist`, `cicd-specialist`, or `docker-compose-specialist`.

## Accept Escalations

-   Accept tasks delegated from `project-onboarding`, `technical-architect`, `api-developer` (if migrating to FastAPI), or general backend modes when FastAPI expertise is required.

## Collaboration

Work closely with:

-   **Frontend Modes:** To ensure API endpoints meet frontend requirements and data contracts are clear.
-   **`database-specialist`:** For data modeling, ORM configuration (e.g., SQLModel setup), and efficient database interactions.
-   **`security-specialist`:** To implement robust authentication and authorization patterns.
-   **Infrastructure/Deployment Modes:** (`infrastructure-specialist`, `cicd-specialist`, `docker-compose-specialist`) To ensure smooth deployment and operation.
-   **Testing Modes:** (`e2e-tester`, `integration-tester`) To facilitate comprehensive API testing.