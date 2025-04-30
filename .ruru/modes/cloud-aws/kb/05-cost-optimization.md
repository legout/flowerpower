# AWS Cost Optimization

This document outlines responsibilities, principles, and strategies for optimizing costs on AWS, aligning with the Cost Optimization pillar of the Well-Architected Framework.

## Core Cost Optimization Responsibilities

*   **Design for Cost-Effectiveness:** Incorporate cost considerations into the initial architecture design phase. Select appropriate services and configurations with cost in mind.
*   **Identify Opportunities:** Regularly review AWS usage and costs using available tools (Cost Explorer, Compute Optimizer, Trusted Advisor) to identify potential savings.
*   **Delegate Implementation:** Delegate specific cost-saving tasks (e.g., right-sizing instances, implementing lifecycle policies, purchasing RIs/Savings Plans based on analysis) to relevant workers.
*   **Monitor & Govern:** Establish mechanisms for tracking costs, setting budgets, and detecting anomalies. Implement tagging for cost allocation.
*   **Report:** Communicate cost projections, actuals, and optimization efforts to `project-manager` and `technical-architect`.

## Core Principles

*   **Cloud Financial Management:** Practice cost awareness and accountability across the team.
*   **Adopt Consumption Model:** Pay only for what you use; scale resources according to demand.
*   **Measure Efficiency:** Understand the cost per unit of business value delivered.
*   **Stop Undifferentiated Heavy Lifting:** Leverage managed services to reduce operational costs.
*   **Analyze & Attribute Expenditure:** Use tagging and cost allocation tools for visibility.

## Cost Optimization Strategies & Checklist

### 1. Compute (EC2, Lambda, Containers)

*   [ ] **Right-Size Instances/Functions:** Use CloudWatch metrics, AWS Compute Optimizer, or third-party tools to match compute resources (EC2 type/size, Lambda memory) to actual workload needs. Avoid overprovisioning.
*   [ ] **Leverage Correct Pricing Models:**
    *   **Savings Plans:** Commit to compute usage (EC2, Fargate, Lambda) for 1 or 3 years for significant discounts. Choose Compute or EC2 Instance Savings Plans based on flexibility needs. Analyze usage before committing.
    *   **Reserved Instances (RIs):** Purchase RIs (Standard or Convertible) for stable EC2, RDS, ElastiCache, Elasticsearch, Redshift workloads. Analyze usage before committing.
    *   **Spot Instances:** Use Spot for fault-tolerant, stateless, or flexible workloads (batch, dev/test, some container workloads) for up to 90% savings. Use Spot Fleet or ASGs with mixed instance policies.
*   [ ] **Implement Auto Scaling:** Scale EC2 instances, ECS services, EKS node groups, or DynamoDB capacity dynamically based on demand.
*   [ ] **Stop/Terminate Idle Resources:** Shut down or terminate unused EC2 instances, especially in non-production environments. Automate cleanup.
*   [ ] **Use Graviton (ARM):** Consider Graviton-based instances/Lambda functions for potential price-performance benefits.

### 2. Storage (S3, EBS, EFS)

*   [ ] **S3 Storage Classes & Lifecycle Policies:**
    *   Use S3 Intelligent-Tiering for data with unknown or changing access patterns.
    *   Define Lifecycle Policies to automatically transition objects to lower-cost tiers (Standard-IA, One Zone-IA, Glacier Instant Retrieval, Glacier Flexible Retrieval, Glacier Deep Archive) or expire them.
    *   Analyze access patterns using S3 Storage Lens or Analytics.
*   [ ] **EBS Optimization:**
    *   Delete unattached/unused EBS volumes.
    *   Delete old/unnecessary EBS snapshots. Implement Snapshot Lifecycle Policies.
    *   Choose the most cost-effective volume type (gp3 often offers better price/performance than gp2). Provision IOPS/throughput separately with gp3.
*   [ ] **EFS Optimization:** Use EFS Lifecycle Management to transition files to EFS Infrequent Access (IA).

### 3. Databases (RDS, DynamoDB, ElastiCache)

*   [ ] **Right-Size Instances/Nodes:** Monitor database performance and resize RDS instances or ElastiCache nodes if overprovisioned.
*   [ ] **Use Reserved Instances/Nodes:** Purchase RIs/Reserved Nodes for stable database workloads.
*   [ ] **Stop Non-Prod Databases:** Stop RDS instances (up to 7 days) or ElastiCache clusters in non-production environments when not in use.
*   [ ] **DynamoDB Capacity Mode:** Choose On-Demand for unpredictable traffic or Provisioned (with Auto Scaling) for predictable traffic. Monitor closely and adjust provisioned throughput. Consider Reserved Capacity for predictable provisioned workloads.
*   [ ] **DynamoDB TTL:** Use Time To Live to automatically expire old items.

### 4. Networking & Content Delivery

*   [ ] **Minimize Data Transfer Costs:**
    *   Use CloudFront CDN to cache content globally, reducing Data Transfer Out costs.
    *   Keep traffic within the same AWS Region and AZ whenever possible.
    *   Use VPC Interface Endpoints (PrivateLink) to access services privately, avoiding NAT Gateway data processing charges and potentially public internet data transfer costs.
    *   Compress data before transfer.
*   [ ] **Optimize NAT Gateway Usage:** Consolidate NAT Gateways using Transit Gateway if applicable. Use VPC Endpoints instead where possible.
*   [ ] **Clean Up Unused Elastic IPs:** Release EIPs not associated with running resources.

### 5. Monitoring & Governance

*   [ ] **Implement Tagging:** MANDATORY. Tag all resources consistently for cost allocation. Activate cost allocation tags in the Billing console.
*   [ ] **Use AWS Cost Explorer:** Regularly analyze spending, identify trends and cost drivers, view Savings Plans/RI utilization and recommendations.
*   [ ] **Set AWS Budgets:** Create budgets (cost, usage, RI/Savings Plan utilization/coverage) with alerts to track spending against targets.
*   [ ] **Enable Cost Anomaly Detection:** Automatically detect unusual spending.
*   [ ] **Review Trusted Advisor:** Check cost optimization recommendations.
*   [ ] **Use AWS Compute Optimizer:** Get right-sizing recommendations.

*(Cost optimization is an ongoing process. Continuously monitor, analyze, and refine.)*