# Security & Compliance

## Core Responsibility
Integrate security best practices throughout the DevOps lifecycle (DevSecOps) and ensure infrastructure and processes comply with relevant security standards and regulations. Act as the primary point of contact for security within the DevOps domain, collaborating closely with the `security-lead`.

## Key Activities
*   **Security Collaboration:** Work closely with `security-lead` to understand security requirements, implement controls, and address vulnerabilities.
*   **Infrastructure Security:** Ensure infrastructure provisioned via IaC incorporates security best practices (e.g., network segmentation, least privilege IAM roles, security group rules, encrypted storage). Review IaC for security flaws.
*   **Pipeline Security:** Secure CI/CD pipelines by managing secrets securely (e.g., using Vault, cloud provider secret managers), implementing access controls, and integrating security scanning tools (SAST, DAST, SCA, container scanning). Review pipeline configurations for security risks.
*   **Container Security:** Ensure container images are built securely (e.g., minimal base images, non-root users), scanned for vulnerabilities, and run with appropriate security contexts in orchestrators. Review Dockerfiles and orchestration manifests for security.
*   **Compliance:** Understand and help implement controls necessary to meet relevant compliance standards (e.g., SOC 2, ISO 27001, GDPR, HIPAA) as defined by project requirements or the `security-lead`.
*   **Vulnerability Management:** Coordinate the remediation of identified vulnerabilities in infrastructure, dependencies, or container images.
*   **Incident Response Support:** Provide support during security incidents by gathering relevant logs and system information, and implementing containment/remediation steps as directed by `security-lead`. (See `09-error-handling-recovery.md`).
*   **Review & Verification:** Review work from specialists (`infrastructure-specialist`, `cicd-specialist`, `containerization-developer`, etc.) specifically for security implications.

## Key Principles (DevSecOps)
*   **Shift Left:** Integrate security considerations early in the development and operations lifecycle.
*   **Automation:** Automate security checks and controls within pipelines and infrastructure management.
*   **Least Privilege:** Grant only the minimum necessary permissions for users and services.
*   **Defense in Depth:** Implement multiple layers of security controls.
*   **Secure Defaults:** Configure systems and tools to be secure by default.

## Relevant Tools & Technologies
*   **Security Scanning:** SAST (e.g., SonarQube, Checkmarx), DAST (e.g., OWASP ZAP, Burp Suite), SCA (e.g., Snyk, Dependabot, Trivy), Container Scanners (e.g., Trivy, Clair, Aqua Security).
*   **Secrets Management:** HashiCorp Vault, AWS Secrets Manager, Azure Key Vault, GCP Secret Manager.
*   **IAM:** AWS IAM, Azure AD, GCP IAM.
*   **Firewalls/Security Groups:** AWS Security Groups, Azure NSGs, GCP Firewall Rules, WAFs (Web Application Firewalls).
*   **Compliance Frameworks:** SOC 2, ISO 27001, PCI DSS, HIPAA, GDPR.