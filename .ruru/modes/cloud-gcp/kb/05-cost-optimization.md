# Cost Optimization

## Principles
*   **Cost Awareness:** Maintain constant awareness of GCP service pricing and cost implications of architectural choices.
*   **Right-Sizing:** Provision resources (VMs, disks, databases) appropriately sized for the workload to avoid overspending.
*   **Elasticity:** Leverage auto-scaling and serverless options where appropriate to match resource allocation to demand.
*   **Resource Lifecycle Management:** Implement policies for identifying and removing unused or underutilized resources.

## Process
1.  **Cost Estimation:** Estimate costs during the design phase using the GCP Pricing Calculator.
2.  **Budgeting & Alerts:**
    *   Set up GCP Budgets to track spending against forecasts.
    *   Configure budget alerts to notify stakeholders of potential overruns.
3.  **Resource Optimization:**
    *   Implement resource right-sizing based on monitoring data.
    *   Utilize Committed Use Discounts (CUDs) or Sustained Use Discounts (SUDs) where applicable.
    *   Choose appropriate storage classes (e.g., Nearline, Coldline, Archive) for data lifecycle management.
    *   Configure auto-scaling policies for relevant services (e.g., Managed Instance Groups, Cloud Run).
4.  **Monitoring & Review:**
    *   Regularly review cost reports (e.g., Billing reports, Cost Table) to identify spending trends and anomalies.
    *   Use cost management tools and recommendations provided by GCP (e.g., Cost Recommendations).
5.  **Documentation:**
    *   Document cost optimization strategies and implemented controls.

## Key Considerations
*   Balance cost optimization with performance and reliability requirements.
*   Use tagging strategies to allocate costs effectively to different projects or teams.
*   Stay informed about GCP pricing updates and new cost-saving features.
*   Consult context files like `v7.1/modes/lead/devops/gcp/gcp-architect/context/cost-optimization-checklist.md`.