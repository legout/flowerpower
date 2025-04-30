# AWS Architecture Design Principles & Patterns

This document covers the principles, considerations, and common patterns for designing robust, scalable, and resilient solutions on AWS.

## Core Design Responsibilities

*   **Analyze Requirements:** Understand functional and non-functional requirements (performance, availability, security, cost).
*   **Select Services:** Choose appropriate AWS services (Compute, Storage, Networking, Database, Serverless, Containers, etc.) based on requirements. Refer to `01-aws-service-reference.md` for service details.
*   **Design Architecture:** Create architecture designs leveraging chosen services. Define network topology (VPC, subnets, routing), IAM strategy, data storage solutions, and compute layer.
*   **Diagramming:** Create or describe architecture diagrams for clarity (potentially using `diagramer`).
*   **Documentation:** Document the design, rationale, and key decisions.

## Key Design Principles (Well-Architected Framework)

Always strive to align designs with the AWS Well-Architected Framework:

*   **Operational Excellence:** Design for automation, monitoring, and continuous improvement. (See `08-operational-excellence.md`)
*   **Security:** Implement security at all layers, enforce least privilege, protect data. (See `04-security-compliance.md`)
*   **Reliability:** Design for fault tolerance, high availability, and automated recovery.
*   **Performance Efficiency:** Use resources efficiently, select appropriate types, monitor performance, and evolve the architecture.
*   **Cost Optimization:** Design with cost awareness, select cost-effective resources, and monitor spending. (See `05-cost-optimization.md`)

## Reliability & Resilience Design

*   **High Availability (HA):**
    *   Deploy critical components across multiple Availability Zones (AZs) within a Region.
    *   Use Elastic Load Balancing (ELB) to distribute traffic across instances in multiple AZs.
    *   Configure RDS Multi-AZ deployments for automatic database failover.
    *   Utilize Auto Scaling to automatically replace unhealthy instances.
*   **Fault Tolerance:** Design systems to withstand component failures (e.g., instance failure, AZ failure).
*   **Disaster Recovery (DR):** Plan for region-level failures if required by business continuity needs. Consider strategies like Backup & Restore, Pilot Light, Warm Standby, or Multi-Site Active-Active.
*   **Automated Backups:** Configure automated backups for stateful resources (EBS volumes via snapshots, RDS snapshots, S3 versioning/replication).
*   **Health Checks:** Implement health checks at multiple levels (ELB, Auto Scaling, Route 53) to detect and route around failures.
*   **Test Recovery:** Regularly test backup and recovery procedures.

## Performance Efficiency Design

*   **Select Appropriate Services:** Choose services that match performance needs (e.g., EC2 instance types, EBS volume types, DynamoDB vs. RDS).
*   **Scalability:**
    *   Design for horizontal scaling using Auto Scaling Groups (EC2) or service-level scaling (ECS, EKS, Lambda, DynamoDB).
    *   Use load balancing (ELB) to distribute load.
*   **Caching:** Implement caching strategies using CloudFront (CDN), ElastiCache (in-memory cache), or API Gateway caching to reduce latency and load on backend systems.
*   **Content Delivery Network (CDN):** Use CloudFront to cache static and dynamic content closer to users globally.
*   **Serverless:** Leverage serverless architectures (Lambda, Fargate, API Gateway, DynamoDB) where appropriate to benefit from automatic scaling and reduced operational overhead.
*   **Optimize Data Storage:** Choose appropriate database types (SQL vs. NoSQL) and storage options based on access patterns and performance requirements.

## Common Architecture Patterns

Refer to these common patterns as starting points, adapting them to specific needs:

*   **Three-Tier Web Application:** Classic separation of Web, Application, and Data tiers using services like ELB, EC2/ECS/Lambda, RDS/DynamoDB, S3, CloudFront.
*   **Serverless API Backend:** Uses API Gateway, Lambda, and DynamoDB/other data stores for scalable, event-driven APIs.
*   **Event-Driven Processing:** Decoupled architecture using services like S3 Events, SQS, SNS, EventBridge, Lambda, and Step Functions for asynchronous processing.
*   **Containerized Microservices (ECS/EKS):** Deploys applications as independent services in containers, managed by ECS or EKS, often using ECR, ELB, Service Discovery, and potentially Fargate.

*(For more details on specific patterns, refer to `../context/common-architecture-patterns.md` or official AWS documentation.)*

## Networking Design (VPC)

*   **Isolation:** Use VPCs to create private network spaces.
*   **Subnetting:** Design public and private subnets across multiple AZs. Place internet-facing resources in public subnets and internal resources in private subnets.
*   **Routing:** Configure Route Tables to control traffic flow between subnets, internet gateways, NAT gateways, VPC endpoints, and VPN/Direct Connect gateways.
*   **Security:** Use Security Groups (instance-level firewall) and NACLs (subnet-level firewall) to control traffic. Apply least privilege.
*   **Private Connectivity:** Use VPC Endpoints (Gateway and Interface types) to access AWS services privately without traversing the internet.
*   **Hybrid Connectivity:** Use VPN or Direct Connect to establish secure connections to on-premises networks. Consider Transit Gateway for managing connectivity across multiple VPCs and on-premises networks.

*(Refer to `04-security-compliance.md` for more detailed network security practices.)*