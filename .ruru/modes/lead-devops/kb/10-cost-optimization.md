# Cost Optimization

## Core Responsibility
Oversee and promote cost-awareness and optimization strategies for cloud resources and DevOps tooling usage.

## Key Activities
*   **Monitoring Costs:** Regularly review cloud provider billing dashboards and cost explorer tools (or delegate review to Cloud Architects/`infrastructure-specialist`). Understand cost drivers.
*   **Identifying Waste:** Look for opportunities to reduce costs, such as:
    *   Right-sizing virtual machines or container resource requests/limits.
    *   Using reserved instances or savings plans for predictable workloads.
    *   Implementing auto-scaling effectively.
    *   Cleaning up unused resources (disks, snapshots, IPs, load balancers).
    *   Leveraging spot instances where appropriate.
    *   Optimizing data storage tiers and lifecycle policies.
    *   Choosing cost-effective service tiers or regions.
*   **Collaboration:** Work with `technical-architect`, Cloud Architects, and development leads to implement cost-saving measures.
*   **Task Delegation:** Delegate specific cost optimization tasks (e.g., implementing resource tagging for cost allocation, scripting cleanup tasks) to relevant specialists.
*   **Reporting:** Report on cost trends and optimization efforts to `project-manager` and other stakeholders.

## Key Concepts
*   **Cloud Billing Models:** Pay-as-you-go, reserved instances, savings plans, spot instances.
*   **Resource Tagging:** Applying metadata tags to resources for cost allocation and tracking.
*   **Right-Sizing:** Matching resource capacity (CPU, memory, disk) to actual workload demands.
*   **Auto-Scaling:** Automatically adjusting resource capacity based on demand.
*   **Cost Allocation:** Attributing cloud costs to specific projects, teams, or applications.

## Relevant Tools & Technologies
*   **Cloud Provider Tools:** AWS Cost Explorer, AWS Budgets, Azure Cost Management + Billing, GCP Billing Reports.
*   **Third-Party Tools:** Cloudability, CloudHealth, Densify (less likely for direct use, but be aware).
*   **IaC Tools:** Can be used to enforce tagging policies or define cost-optimized configurations.