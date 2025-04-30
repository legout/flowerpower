# Infrastructure as Code (IaC) Practices

This document outlines the principles and best practices for implementing and managing AWS infrastructure using Infrastructure as Code (IaC), primarily focusing on Terraform and CloudFormation.

## Core IaC Responsibilities

*   **Lead IaC Implementation:** Guide the team in implementing the designed architecture using IaC tools (Terraform preferred, or CloudFormation).
*   **Plan IaC Structure:** Break down architecture into manageable IaC components/modules. Plan the implementation sequence and state management strategy.
*   **Delegate IaC Tasks:** Assign the creation or modification of specific IaC modules/resources to `infrastructure-specialist` or other relevant workers, providing clear specifications.
*   **Review IaC Code:** Meticulously review submitted IaC code for correctness, adherence to design, security, and best practices. Use `terraform plan` / CloudFormation Change Sets for validation.
*   **Oversee Deployment:** Coordinate IaC deployment through CI/CD pipelines or manual application.

## Core Principles

*   **Declarative:** Define the *desired state*, not the steps to achieve it.
*   **Idempotent:** Applying the same code multiple times yields the same result.
*   **Version Controlled:** Store all IaC code in Git.
*   **Modular:** Break down infrastructure into reusable components.
*   **Automated:** Use CI/CD pipelines for testing and deployment.
*   **Tested:** Validate code before deployment.
*   **Secure:** Embed security into the code and process.

## Best Practices

### 1. Version Control (Git)

*   **Store Everything:** All `.tf`, `.tfvars`, `.yaml`, `.json`, scripts related to IaC go into Git.
*   **Branching Strategy:** Use branches (e.g., feature branches) for development and testing. Protect the main/production branch.
*   **Meaningful Commits:** Describe the *why* and *what* of infrastructure changes.
*   **Code Reviews:** Require reviews for changes, especially before merging to main/production.

### 2. Modularity & Reusability

*   **Terraform Modules:**
    *   Encapsulate related resources (e.g., VPC, RDS, ECS Service).
    *   Use standard module structure (`main.tf`, `variables.tf`, `outputs.tf`).
    *   Source modules from registries (Public, Private) or Git. Use version pinning.
    *   Keep modules focused; avoid overly complex modules.
    *   Define clear interfaces with input variables (with descriptions, types, defaults) and outputs.
*   **CloudFormation Nested Stacks / StackSets:**
    *   Break large templates into smaller, manageable nested stacks.
    *   Use `Export`/`Fn::ImportValue` for cross-stack references (use cautiously due to dependencies).
    *   Use StackSets to deploy common infrastructure across multiple accounts/regions.
    *   Define clear Parameters and Outputs.

### 3. State Management (Terraform)

*   **Remote State Backend:** MANDATORY. Use S3 backend with DynamoDB for locking.
    *   Configure backend in `terraform { backend "s3" { ... } }` block.
    *   Ensure S3 bucket has versioning enabled.
    *   Restrict access to the S3 bucket and DynamoDB table.
    *   Encrypt state file (`encrypt = true` in backend config).
*   **State Locking:** DynamoDB table prevents concurrent `apply` operations.
*   **Minimize Blast Radius:** Use separate state files per environment (dev/stg/prod) and potentially per major component or region.
    *   Achieve separation via directory structure (preferred) or Terraform Workspaces.
*   **Protect State:** Avoid storing sensitive data directly in state. Mark variables as `sensitive = true`.

### 4. Coding Standards & Style

*   **Formatting:** Use `terraform fmt` / `cfn-lint --format`. Enforce in CI.
*   **Naming:** Consistent, descriptive names for resources, variables, outputs, modules. (e.g., `aws_s3_bucket.logs`, `var.vpc_cidr_block`).
*   **Tagging:** Implement a consistent tagging strategy for all resources for cost allocation, identification, and automation. Define required tags via policies if possible.
*   **Comments:** Explain complex logic or non-obvious configurations.
*   **Variables:** Use `variables.tf` / `Parameters`. Provide descriptions, types, and sensible defaults. Use `.tfvars` / parameter files for environment-specific values.
*   **Outputs:** Use `outputs.tf` / `Outputs`. Provide descriptions. Expose only necessary information.

### 5. Testing & Validation

*   **Static Analysis:**
    *   `terraform validate` / `aws cloudformation validate-template` (basic syntax check).
    *   Linters: `tflint`, `cfn-lint` (style, best practices).
    *   Security Scanners: `tfsec`, `checkov`, `cfn-nag` (detect insecure configurations). Integrate into CI.
*   **Plan/Change Set Review:**
    *   **MANDATORY:** Always run `terraform plan` / create CloudFormation Change Set before applying.
    *   Carefully review the execution plan/changes to ensure they match intent and have no unintended consequences.
*   **Policy as Code:** Use OPA or Sentinel to enforce organizational standards (e.g., required tags, allowed instance types, disallowed public buckets).
*   **(Advanced) Integration Testing:** Use tools like `Terratest` to provision temporary infrastructure, run tests against it, and tear it down.

### 6. CI/CD Automation

*   **Pipeline Integration:** Automate IaC deployment via CodePipeline, Jenkins, GitLab CI, GitHub Actions, etc.
*   **Pipeline Steps:** Include linting, security scanning, validation, plan/change set generation, manual approval (for prod), and apply/execute.
*   **Environment Configuration:** Manage environment variables/secrets securely within the CI/CD system (e.g., AWS Secrets Manager, Vault, CI/CD platform secrets).

*(Refer to `04-security-compliance.md` for specific security practices related to IaC secrets and permissions.)*