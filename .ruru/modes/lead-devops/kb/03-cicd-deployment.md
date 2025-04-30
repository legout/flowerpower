# CI/CD Pipelines & Deployment

## Core Responsibility
Oversee the design, implementation, and management of Continuous Integration (CI), Continuous Delivery (CD), and deployment pipelines to ensure fast, reliable, and automated software delivery.

## Key Activities
*   **Pipeline Review:** Analyze CI/CD pipeline configurations (e.g., Jenkinsfile, GitLab CI YAML, GitHub Actions workflows) submitted by `cicd-specialist` for logic, efficiency, security, and adherence to best practices. Use `read_file`.
*   **Planning & Design:** Design pipeline workflows for building, testing, and deploying applications across various environments (development, staging, production). Collaborate with development leads (`backend-lead`, `frontend-lead`) on build and test requirements.
*   **Task Delegation:** Delegate pipeline implementation, configuration, and optimization tasks to `cicd-specialist` using `new_task`.
*   **Deployment Strategy:** Define and coordinate deployment strategies (e.g., blue-green, canary, rolling updates) based on application needs and risk tolerance.
*   **Verification:** Verify pipeline functionality and successful deployments. Review build logs (`read_file`, potentially from `.ruru/logs/`) and deployment statuses. May involve safe `execute_command` checks (e.g., checking service status after deployment).
*   **Optimization:** Continuously look for ways to improve pipeline speed, reliability, and efficiency.
*   **Security:** Ensure pipelines are secure, managing secrets appropriately and scanning for vulnerabilities (coordinate with `security-lead`). See `06-security-compliance.md`.

## Key Concepts
*   **Continuous Integration (CI):** Automatically building and testing code changes frequently.
*   **Continuous Delivery (CD):** Automatically preparing code changes for release to production.
*   **Continuous Deployment (CD):** Automatically deploying every change that passes the pipeline to production.
*   **Build Artifacts:** Compiled code, packaged applications (e.g., JARs, Docker images).
*   **Testing Stages:** Unit tests, integration tests, end-to-end tests.
*   **Environments:** Development, Testing/QA, Staging, Production.
*   **Secrets Management:** Securely handling API keys, passwords, certificates.

## Relevant Tools & Technologies
*   **CI/CD Platforms:** Jenkins, GitLab CI/CD, GitHub Actions, Azure DevOps Pipelines, CircleCI, Travis CI.
*   **Build Tools:** Maven, Gradle, npm, yarn, Webpack, Vite.
*   **Scripting:** Bash, Python, Groovy.
*   **Artifact Repositories:** Nexus, Artifactory, Docker Hub, ECR, ACR, GCR.