# Monitoring, Logging & Performance

## Principles
*   **Observability:** Ensure systems are designed and instrumented to be observable, providing insights into their state and behavior through metrics, logs, and traces.
*   **Proactive Monitoring:** Set up monitoring and alerting to detect potential issues before they impact users.
*   **Performance Optimization:** Continuously monitor and optimize infrastructure performance based on requirements and observed behavior.

## Process
1.  **Monitoring Setup:**
    *   Configure Cloud Monitoring for key infrastructure metrics (CPU, memory, disk, network).
    *   Set up monitoring for specific GCP services (e.g., Load Balancer health checks, Cloud SQL metrics).
    *   Define meaningful alerting policies based on thresholds or anomalies.
    *   Create dashboards to visualize key performance indicators (KPIs).
2.  **Logging Setup:**
    *   Configure Cloud Logging to collect logs from applications and infrastructure components.
    *   Set up log-based metrics and alerts.
    *   Ensure audit trails (Cloud Audit Logs) are captured and retained appropriately.
    *   Consider centralized logging solutions if needed.
3.  **Performance Analysis & Optimization:**
    *   Analyze performance metrics to identify bottlenecks.
    *   Optimize resource configurations (e.g., machine types, disk types).
    *   Tune application and database performance in collaboration with relevant leads.
    *   Implement caching strategies where appropriate.
4.  **Documentation:**
    *   Document the monitoring and logging strategy, including configured alerts and dashboards.
    *   Maintain performance tuning records and rationale.

## Key Considerations
*   Define Service Level Objectives (SLOs) and Service Level Indicators (SLIs) to measure reliability and performance.
*   Collaborate with the `Monitoring Specialist` (`035-work-do-monitoring-specialist`) for advanced setups.
*   Integrate monitoring with incident response procedures.
*   Regularly review and refine monitoring configurations and alert thresholds.