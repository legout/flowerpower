# GCP Architecture Design

## Process
1.  **Requirements Analysis:**
    *   Thoroughly review project requirements, constraints, and non-functional requirements (NFRs).
    *   Identify and document key architectural drivers (e.g., scalability needs, latency targets, compliance mandates).
    *   Log initial analysis and drivers in the relevant task file (e.g., using `.ruru/templates/toml-md/01_mdtm_feature.md`).
2.  **Service Selection:**
    *   Choose the most appropriate GCP services (Compute, Storage, Networking, Databases, AI/ML, etc.) based on requirements, cost, performance, and manageability.
    *   Leverage knowledge of GCP service capabilities and limits.
3.  **Network Design:**
    *   Design a secure and efficient network topology (VPCs, subnets, firewall rules, load balancing, interconnects).
4.  **Security Planning:**
    *   Integrate security considerations from the start (IAM, encryption, network security, compliance controls).
5.  **Resource Configuration:**
    *   Define appropriate configurations for selected services (machine types, storage classes, scaling parameters).
6.  **Diagramming:**
    *   Create clear architecture diagrams (e.g., using Mermaid or dedicated tools) to visualize the proposed solution. Reference `.ruru/docs/standards/diagramming.md`.
7.  **Documentation:**
    *   Document design decisions, trade-offs, and rationale, potentially using ADRs (`.ruru/templates/toml-md/07_adr.md`).

## Key Considerations
*   Design for scalability, reliability, and high availability.
*   Incorporate security best practices and compliance requirements early.
*   Optimize for performance based on application needs.
*   Consider cost implications of service choices and configurations.
*   Plan for disaster recovery and business continuity.