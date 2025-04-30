# Security & Compliance

## Principles
*   **Security by Design:** Integrate security considerations into every stage of the architecture design and implementation process.
*   **Least Privilege:** Implement the principle of least privilege for all IAM roles and policies. Grant only the necessary permissions required for a task.
*   **Defense in Depth:** Employ multiple layers of security controls (network, compute, data, identity).
*   **Compliance:** Understand and adhere to relevant compliance frameworks (e.g., GDPR, HIPAA, PCI DSS) as required by the project.

## Process
1.  **IAM Configuration:**
    *   Define and implement granular IAM roles and policies using IaC.
    *   Regularly review and audit permissions.
    *   Utilize service accounts securely.
2.  **Network Security:**
    *   Configure VPC firewall rules to restrict traffic appropriately.
    *   Implement Cloud Armor for WAF and DDoS protection if needed.
    *   Use Private Google Access or VPC Service Controls where applicable.
3.  **Data Security:**
    *   Configure encryption at rest and in transit using Google-managed or customer-managed keys (CMEK).
    *   Utilize Cloud KMS for key management.
    *   Implement data loss prevention (DLP) strategies if necessary.
4.  **Security Controls Implementation:**
    *   Configure security features specific to GCP services (e.g., Security Command Center, Identity Platform).
    *   Implement security scanning and vulnerability management.
5.  **Auditing & Logging:**
    *   Ensure comprehensive audit logging (Cloud Audit Logs) is enabled and configured.
    *   Forward logs to appropriate destinations (e.g., Cloud Logging, SIEM).
6.  **Documentation:**
    *   Document all security configurations, policies, and procedures.
    *   Maintain evidence for compliance audits.

## Key Considerations
*   Stay informed about GCP security best practices and new security features.
*   Collaborate closely with the `Security Lead` (`020-lead-sec-security-lead`) and delegate specific tasks to the `Security Specialist` (`035-work-do-security-specialist`).
*   Implement automated security checks and compliance monitoring.