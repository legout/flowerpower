+++
# --- Metadata ---
id = "PLAYBOOK-CI-CD-SETUP-V1"
title = "Project Playbook: Setting up a CI/CD Pipeline"
status = "published"
created_date = "2025-04-24"
updated_date = "2025-04-24"
version = "1.0"
tags = ["playbook", "documentation", "project-management", "ci-cd", "devops", "automation", "github-actions", "docker", "deployment", "epic", "feature", "task"]
related_docs = [
    ".ruru/docs/standards/project-management-strategy-v1.md",
    ".ruru/planning/project-structure/00-epic-feature-task-plan.md",
    ".ruru/modes/lead-devops/lead-devops.mode.md",
    ".ruru/modes/infra-compose/infra-compose.mode.md", # If Docker involved
    # Add cloud-specific modes if deploying to cloud
    # ".ruru/modes/cloud-aws/cloud-aws.mode.md",
    # ".ruru/modes/cloud-azure/cloud-azure.mode.md",
    # ".ruru/modes/cloud-gcp/cloud-gcp.mode.md"
]
objective = "Provide a structured process for planning, implementing, and verifying a Continuous Integration and Continuous Deployment (CI/CD) pipeline using common tools like GitHub Actions, Docker, and cloud services, managed via the Roo Commander Epic-Feature-Task hierarchy."
scope = "Covers defining pipeline stages (build, test, deploy), configuring the CI/CD platform, containerization (optional), environment management, and basic workflow setup."
target_audience = ["Users", "DevOps Engineers", "Technical Leads", "Architects", "AI Modes"]
# --- Document Specific Fields ---
example_project_type = "Web Application, API, or Service needing automated build/test/deploy"
ci_cd_platform_example = "GitHub Actions"
containerization_example = "Docker"
deployment_target_example = "Cloud Service (e.g., AWS S3/ECS, Azure App Service, Vercel)"
+++

# Project Playbook: Setting up a CI/CD Pipeline

This playbook outlines a recommended approach for establishing an automated CI/CD pipeline for your project using Roo Commander's Epic-Feature-Task hierarchy. Automating build, test, and deployment improves consistency, speed, and reliability.

**Scenario:** You want to automate the process of building, testing, and deploying your application whenever changes are pushed to your Git repository. We'll use GitHub Actions as the example platform.

## Phase 1: Planning & Design

1.  **Define the CI/CD Initiative (Epic):**
    *   **Goal:** Establish the high-level goals for the automation pipeline.
    *   **Action:** Create the main Epic (e.g., `.ruru/epics/EPIC-020-setup-automated-ci-cd.md`).
    *   **Content:** Define `objective` (e.g., "Automate the build, unit/integration testing, and deployment to staging for the main branch"), `scope_description` (which repository, which branches trigger which actions, target deployment environments), key tools (GitHub Actions, Docker, [Cloud Provider]). Set `status` to "Planned".

2.  **Pipeline Strategy & Tooling Decisions (Feature / ADRs):**
    *   **Goal:** Define the specific stages, triggers, tools, and environments.
    *   **Action:** Define as a Feature (`FEAT-080-cicd-pipeline-design.md`) or break into smaller design Features. Delegate to `lead-devops` or `core-architect`.
    *   **Tasks (Examples):**
        *   "Define pipeline stages (e.g., Lint, Unit Test, Build, Integration Test, Deploy Staging, Deploy Prod)."
        *   "Define triggers (e.g., push to `main`, pull request to `main`, tag creation)."
        *   "Choose base runner environment (e.g., `ubuntu-latest`)."
        *   "Determine build artifact strategy (e.g., compiled code, Docker image)."
        *   "Define deployment strategy for each environment (e.g., static site sync, container registry push + service update)."
        *   "Identify required environment variables and secrets (e.g., API keys, cloud credentials)."
    *   **Output:** Document the design in the Feature file or linked ADRs (`.ruru/decisions/`).

## Phase 2: Pipeline Implementation (Iterative Features)

1.  **Basic CI Workflow Setup (Feature):**
    *   **Goal:** Create the initial workflow file and implement basic linting and unit testing stages triggered on push/pull requests.
    *   **Action:** Define as a Feature (`FEAT-081-cicd-basic-lint-test.md`). Set `status` to "Ready for Dev". Decompose into Tasks.
    *   **Tasks (Examples - Delegate to `lead-devops`, `util-senior-dev`):**
        *   "Create workflow file `.github/workflows/ci.yml`." (Use `write_to_file`)
        *   "Define `on: [push, pull_request]` triggers for relevant branches."
        *   "Add job `lint`: checkout code, setup [Node/Python/etc.], run lint command."
        *   "Add job `unit-test`: checkout code, setup environment, run unit test command."
    *   **Process:** Use MDTM workflow, link tasks to Feature. Verify workflow syntax. Commit and push to test triggers.

2.  **Build Artifact Generation (Feature):**
    *   **Goal:** Add a stage to build the application artifact (e.g., compiled code, executable).
    *   **Action:** Define as a Feature (`FEAT-082-cicd-build-artifact.md`). Set `status` to "Ready for Dev". Decompose into Tasks.
    *   **Tasks (Examples - Delegate to `lead-devops`):**
        *   "Add job `build` (dependent on test jobs): checkout code, setup env, run build command (e.g., `npm run build`)."
        *   "Configure caching for dependencies (e.g., `actions/cache`)."
        *   "Upload build artifact using `actions/upload-artifact`."
    *   **Process:** Use MDTM workflow, link tasks to Feature. Update workflow file. Test.

3.  **Containerization (Feature - If Applicable):**
    *   **Goal:** Create a Docker image for the application.
    *   **Action:** Define as a Feature (`FEAT-083-cicd-containerization.md`). Set `status` to "Ready for Dev". Decompose into Tasks.
    *   **Tasks (Examples - Delegate to `infra-compose`, `lead-devops`):**
        *   "Create `Dockerfile` for the application."
        *   "Add job `build-push-image` (dependent on build/test): checkout code, setup Docker buildx."
        *   "Implement step to log in to container registry (Docker Hub, AWS ECR, etc.) using secrets." **(Handle Secrets Securely!)**
        *   "Implement step to build the Docker image (using `docker buildx build`)."
        *   "Implement step to push the Docker image to the registry with appropriate tags (e.g., commit SHA, latest)."
    *   **Process:** Use MDTM workflow. Emphasize secure handling of registry credentials using GitHub Secrets.

4.  **Deployment to Staging Environment (Feature):**
    *   **Goal:** Automate deployment to a non-production environment (e.g., triggered on merge to `main`).
    *   **Action:** Define as a Feature (`FEAT-084-cicd-deploy-staging.md`). Set `status` to "Ready for Dev". Decompose into Tasks.
    *   **Tasks (Examples - Delegate to `lead-devops`, Cloud Specialist):**
        *   "Add job `deploy-staging` (dependent on build/test/image jobs, conditional on branch `main`)."
        *   "Implement checkout step."
        *   "Configure cloud provider credentials securely using GitHub Secrets (e.g., `aws-actions/configure-aws-credentials`)." **(Security Critical!)**
        *   "Implement deployment steps based on strategy (e.g., `aws s3 sync`, `vercel deploy --prod --token=$VERCEL_TOKEN`, `az webapp deploy`, update ECS/K8s deployment)."
    *   **Process:** Use MDTM workflow. **Extreme caution with secrets.** Use platform-specific secrets management.

5.  **Deployment to Production Environment (Feature - Often Manual Trigger):**
    *   **Goal:** Define the process for deploying to production (often requires manual approval or tag trigger).
    *   **Action:** Define as a Feature (`FEAT-085-cicd-deploy-production.md`). Set `status` to "Ready for Dev".
    *   **Tasks (Examples):**
        *   "Add job `deploy-production` (similar to staging, but with production secrets/targets)."
        *   "Configure trigger (e.g., `on: workflow_dispatch` for manual trigger, or `on: release: types: [published]`)."
        *   "Implement GitHub Environments with required approvers for production deployment step."
    *   **Process:** Use MDTM workflow. Focus on safety, approval workflows, and distinct production secrets.

## Phase 3: Verification, Documentation & Monitoring

1.  **Pipeline Testing:**
    *   **Goal:** Ensure the pipeline runs reliably for different triggers (PRs, merges, tags).
    *   **Action:** Create PRs, merge code, create tags to trigger different workflow paths. Monitor GitHub Actions runs, debug failures. Create tasks for fixing pipeline issues.

2.  **Documentation:**
    *   **Goal:** Explain how the CI/CD pipeline works, how to use it, and how secrets are managed.
    *   **Action:** Define as a Feature (`FEAT-086-cicd-documentation.md`). Delegate to `util-writer` or `lead-devops`.
    *   **Content:** Update project `README.md` or create a dedicated `CONTRIBUTING.md` or `docs/ci-cd.md` explaining triggers, stages, artifacts, deployment process, and where secrets are configured (e.g., "in GitHub repository secrets").

3.  **Monitoring & Alerting (Optional Enhancement):**
    *   **Goal:** Get notified about pipeline failures.
    *   **Action:** Define as a Feature.
    *   **Tasks:** "Configure GitHub Actions notifications (e.g., Slack, email) on workflow failure."

4.  **Update Epic Status:** Once the core pipeline (e.g., build, test, deploy-staging) is stable and documented, update the main CI/CD Epic status to "In Progress" or "Done" (for V1).

## Key Considerations for CI/CD:

*   **Security:** **SECRET MANAGEMENT IS CRITICAL.** Never commit secrets directly to code. Use the CI/CD platform's secret management system (e.g., GitHub Secrets, GitLab CI/CD Variables, Azure Key Vault). Rotate secrets regularly. Limit permissions granted to deployment credentials.
*   **Idempotency:** Deployment steps should ideally be idempotent (running them multiple times has the same effect as running them once).
*   **Environment Parity:** Keep staging and production environments as similar as possible. Use environment variables for configuration differences.
*   **Testing Strategy:** Decide which tests run in the pipeline (unit, integration, E2E). Balance coverage with execution time.
*   **Build Speed:** Optimize build times using caching, parallel jobs, and efficient build steps.
*   **Rollback Strategy:** Define how to quickly revert to a previous working version if a deployment fails or introduces critical issues.
*   **Cost:** Be mindful of runner costs on the CI/CD platform, especially for complex builds or long-running tests.

This playbook provides a framework for systematically building out your CI/CD pipeline with Roo Commander, promoting automation and reliability.