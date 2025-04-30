# Cloud Platforms (AWS, Azure, GCP)

## Core Responsibility
Oversee the utilization of cloud platforms (AWS, Azure, GCP), ensuring alignment with architectural decisions, best practices, security, and cost-efficiency. Coordinate with specialized Cloud Architects.

## Key Activities
*   **Platform Awareness:** Maintain a good understanding of the core services and paradigms of the major cloud providers (AWS, Azure, GCP) relevant to the project.
*   **Collaboration with Architects:** Work closely with `aws-architect`, `azure-architect`, and `gcp-architect` on:
    *   Reviewing cloud-specific infrastructure designs and IaC.
    *   Delegating tasks involving platform-specific services (e.g., setting up managed Kubernetes, serverless functions, database services).
    *   Ensuring adherence to cloud provider best practices.
    *   Optimizing cloud resource usage and costs (See `10-cost-optimization.md`).
*   **Service Selection Guidance:** Provide input on cloud service selection based on operational requirements, coordinating with `technical-architect` and Cloud Architects.
*   **Account Management (Coordination):** Coordinate aspects of cloud account structure, IAM policies, and billing, often guided by `technical-architect` or specific Cloud Architects.
*   **Verification:** Review configurations and deployments within cloud environments, potentially using provider consoles/CLIs (via safe `execute_command`) or reviewing outputs from Cloud Architects.

## Key Considerations per Platform
*   **AWS (Amazon Web Services):** EC2, S3, RDS, VPC, IAM, CloudFormation, EKS, ECS, Lambda, CloudWatch, etc.
*   **Azure:** Virtual Machines, Blob Storage, Azure SQL Database, VNet, Azure Active Directory, ARM/Bicep, AKS, Container Instances, Azure Functions, Azure Monitor, etc.
*   **GCP (Google Cloud Platform):** Compute Engine, Cloud Storage, Cloud SQL, VPC Network, IAM, Cloud Deployment Manager, GKE, Cloud Run, Cloud Functions, Cloud Monitoring (Stackdriver), etc.

## Context Files
*   Refer to potential context files like `aws-best-practices.md`, `azure-security-checklist.md`, `gcp-networking-patterns.md` within the `context/` directory (or delegate creation/sourcing to relevant architects).