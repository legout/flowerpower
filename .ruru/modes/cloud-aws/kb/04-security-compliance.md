# AWS Security & Compliance

This document outlines key responsibilities and best practices for ensuring the security and compliance of AWS infrastructure, aligning with the Security Pillar of the Well-Architected Framework.

## Core Security Responsibilities

*   **Security Design:** Design architectures with security embedded from the start ("Security by Design").
*   **Oversee Implementation:** Guide and review the implementation of security controls (network, IAM, data protection) by relevant workers (`infrastructure-specialist`, `security-specialist`).
*   **IAM Strategy:** Define the overall strategy for Identity and Access Management (roles, policies, users, groups).
*   **Network Security Design:** Define VPC structure, subnetting, Security Group strategy, NACL usage, and connectivity patterns (VPC Endpoints, NAT, VPN/Direct Connect).
*   **Data Protection Strategy:** Define requirements for encryption (at rest, in transit) and key management (KMS).
*   **Collaboration:** Work closely with `security-lead` and `security-specialist` on overall security posture, compliance requirements, and incident response.
*   **Review:** Review security configurations implemented via IaC or manually.

## Security Best Practices

### 1. Identity and Access Management (IAM)

*   **Least Privilege:** Grant *minimum* necessary permissions. Start small, add as needed. Avoid wildcard `*` permissions where possible.
*   **Roles over Keys:** Use IAM Roles for EC2 instances (Instance Profiles), Lambda functions (Execution Roles), ECS tasks, etc., to grant temporary credentials. Avoid long-lived access keys.
*   **Users & Groups:** Use IAM Users for individuals, assign to Groups, apply policies to Groups.
*   **Strong Credentials:** Enforce strong password policies and MANDATE MFA for root and privileged users. Encourage MFA for all.
*   **Conditions:** Use policy conditions (IP range, MFA, time, tags) to further restrict access.
*   **Regular Review:** Use IAM Access Analyzer to identify unused access and overly permissive policies. Periodically audit users, groups, roles, and policies.
*   **Credential Rotation:** Rotate access keys regularly if they must be used.

### 2. Network Security

*   **VPC Isolation:** Use VPCs for network boundaries.
*   **Public/Private Subnets:** Isolate backend resources in private subnets. Use public subnets only for necessary internet-facing resources (e.g., ELBs, NAT Gateways, Bastion Hosts).
*   **Security Groups (Stateful):** Primary instance-level firewall. Apply least privilege (allow specific ports from specific sources). Default to deny all inbound.
*   **NACLs (Stateless):** Subnet-level firewall. Use as a secondary defense layer if needed (e.g., blocking specific IPs). Remember stateless nature (need allow rules for both inbound and outbound return traffic).
*   **VPC Endpoints:** Use Gateway (S3, DynamoDB) and Interface (most other services via PrivateLink) endpoints to access AWS services without traversing the internet. Reduces exposure and potentially data transfer costs.
*   **NAT Gateways:** Use managed NAT Gateways for outbound internet access from private subnets. Avoid NAT Instances unless specific needs dictate.
*   **WAF:** Apply AWS WAF to CloudFront, ALB, or API Gateway to protect against common web attacks (SQLi, XSS). Use managed rule sets and custom rules.
*   **Shield:** Rely on Shield Standard (default DDoS protection). Consider Shield Advanced for enhanced protection and cost protection for specific resources.

### 3. Data Protection

*   **Encryption at Rest:**
    *   **MANDATORY:** Enable encryption for sensitive data stores.
    *   S3: SSE-S3 (default option), SSE-KMS (KMS managed keys), or SSE-C (client-managed keys). Enforce via bucket policies.
    *   EBS: Enable encryption by default at the account level. Encrypt volumes.
    *   RDS: Enable encryption at creation. Encrypt snapshots.
    *   Use AWS KMS for key management. Use Customer Managed Keys (CMKs) for granular control over key policies and rotation, if required.
*   **Encryption in Transit:**
    *   **MANDATORY:** Use TLS/HTTPS for all external traffic.
    *   Use ACM for managing public TLS certificates for ELB, CloudFront, API Gateway.
    *   Encrypt internal traffic between services where necessary based on sensitivity.
*   **Secrets Management:**
    *   **NEVER** hardcode secrets (passwords, API keys) in code, configuration files, or IaC templates.
    *   Use AWS Secrets Manager or AWS Systems Manager Parameter Store (SecureString type) to store and retrieve secrets securely.
    *   Grant IAM permissions for applications/services to access secrets. Reference secrets dynamically in IaC (e.g., Terraform data sources, CloudFormation dynamic references).

### 4. Logging, Monitoring & Auditing (Security Focus)

*   **CloudTrail:** Enable across all regions, log to secure S3 bucket (potentially in separate account), enable log file integrity validation. Send logs to CloudWatch Logs for alerting.
*   **GuardDuty:** Enable in all relevant regions for threat detection. Review findings.
*   **Security Hub:** Enable to aggregate findings from GuardDuty, Config, Inspector, Macie, etc. Monitor compliance against standards (e.g., CIS Benchmark).
*   **AWS Config:** Enable to track resource configuration changes. Implement Config Rules (managed and custom) to detect non-compliant resources (e.g., unencrypted volumes, public S3 buckets, permissive security groups).
*   **VPC Flow Logs:** Enable for critical VPCs/subnets/interfaces. Analyze for anomalous traffic patterns.
*   **Alerting:** Create CloudWatch Alarms based on security-critical CloudTrail events (Root login, IAM changes, SG changes), GuardDuty findings (High severity), Config rule non-compliance, and specific log patterns.

### 5. Compliance

*   Understand relevant compliance frameworks (e.g., PCI-DSS, HIPAA, SOC 2, GDPR).
*   Leverage AWS services and features designed for compliance (e.g., Artifact for reports, Config conformance packs, Security Hub standards).
*   Design architecture and implement controls to meet specific compliance requirements.
*   Ensure logging and auditing are sufficient to demonstrate compliance.
*   Collaborate with `security-lead` on compliance strategy and evidence gathering.

*(This is not exhaustive. Always consult the latest AWS security documentation, the Well-Architected Framework Security Pillar, and collaborate with the `security-lead`.)*