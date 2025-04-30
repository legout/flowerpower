# Azure Architecture Design

*   **Requirement Analysis:** Thoroughly analyze functional, performance, security, and cost constraints before designing. (Source: Line 25)
*   **Service Selection:** Leverage deep knowledge of core Azure services (compute, storage, networking, database, serverless, containers, identity, security, monitoring) to select the most appropriate services for the requirements. Examples include VNets, VMs, App Service, AKS, Azure Functions, Azure SQL Database, Cosmos DB, Storage Accounts, etc. (Source: Lines 14, 26, 45)
*   **Network Design:** Define robust network topology, including VNet design, subnets, routing (UDRs), connectivity (VPN Gateway, ExpressRoute), and traffic management (Load Balancer, Application Gateway). (Source: Lines 17, 26)
*   **Scalability &amp; Performance:** Design solutions that meet performance requirements and can scale effectively using appropriate Azure services and patterns. (Source: Lines 13, 26, 49)
*   **Reliability &amp; Resilience:** Design for high availability, fault tolerance, and disaster recovery. Explicitly design for failure scenarios. (Source: Lines 13, 26, 50, 74)
*   **Cloud Patterns:** Apply established cloud architecture patterns where applicable. (Source: Line 85)
*   **Documentation:** Clearly document all architecture designs and decisions. (Source: Lines 20, 33, 52)