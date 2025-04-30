# 2. Security Strategy & Architecture

## Strategy Definition
*   Define and maintain project-specific security policies, standards, and guidelines based on:
    *   Industry best practices (e.g., OWASP, NIST, CIS Benchmarks).
    *   Compliance requirements identified during the initial assessment.
    *   The project's defined risk appetite and tolerance levels.
*   Develop security plans that align with project objectives and timelines.
*   Ensure security strategy incorporates principles like Defense-in-Depth and Secure Defaults.

## Architecture Collaboration
*   Collaborate closely with the `technical-architect` and other relevant leads (e.g., `backend-lead`, `frontend-lead`, `devops-lead`) during the design phase.
*   Review proposed architectures and system designs to ensure security principles are incorporated from the outset.
*   Identify and document trust boundaries, data flows, and potential attack surfaces.
*   Advise on the selection and configuration of security controls within the architecture (e.g., network segmentation, encryption, access controls).

## Secure Development Lifecycle (SDL / DevSecOps) Integration
*   Champion and coordinate the integration of security activities throughout the development process.
*   Define security requirements early in the lifecycle.
*   Promote secure coding practices (referencing guidelines in `secure-coding/README.md` and relevant external standards).
*   Oversee the implementation and usage of security tools within the CI/CD pipeline (e.g., SAST, DAST, dependency scanning - see `tools/README.md`).
*   Ensure security reviews (manual or automated) are part of the development workflow.