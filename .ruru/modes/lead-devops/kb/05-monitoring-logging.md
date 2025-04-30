# Monitoring, Logging, and Alerting

## Core Responsibility
Oversee the implementation and management of monitoring, logging, and alerting systems to ensure visibility into system health, performance, and security, enabling proactive issue detection and rapid response.

## Key Activities
*   **Monitoring Configuration Review:** Understand and review monitoring tool configurations (e.g., Prometheus rules, Grafana dashboards, Datadog monitors, CloudWatch alarms) and alerting rules submitted by `monitoring-specialist`. Use `read_file`.
*   **Strategy & Design:** Define the monitoring and logging strategy, including key metrics to track (system, application, business), log aggregation methods, and alerting thresholds. Collaborate with `technical-architect` and development leads.
*   **Task Delegation:** Delegate tasks related to setting up monitoring agents, configuring log shippers, building dashboards, and defining alert rules to `monitoring-specialist` using `new_task`.
*   **Alert Management:** Oversee the alert lifecycle, ensuring alerts are actionable, routed correctly, and reviewed periodically for effectiveness. Define on-call procedures if applicable.
*   **Analysis & Reporting:** Analyze monitoring data and logs to identify trends, performance bottlenecks, and potential issues. Report on system health and availability.
*   **Verification:** Verify that monitoring and logging systems are collecting the correct data and alerts are triggering as expected.

## Key Concepts
*   **Metrics:** Numerical measurements of system or application behavior over time (e.g., CPU utilization, request latency, error rates).
*   **Logs:** Timestamped records of events occurring within systems or applications.
*   **Traces:** Records of the path of a request as it travels through different services in a distributed system.
*   **Observability:** The ability to understand the internal state of a system by examining its outputs (metrics, logs, traces).
*   **Alerting:** Automatically notifying relevant personnel when predefined conditions or thresholds are met.
*   **Dashboards:** Visual representations of metrics and logs for easy monitoring.
*   **Log Aggregation:** Collecting logs from multiple sources into a centralized system for searching and analysis.

## Relevant Tools & Technologies
*   **Monitoring:** Prometheus, Grafana, Datadog, New Relic, Dynatrace, AWS CloudWatch, Azure Monitor, Google Cloud Monitoring (Stackdriver).
*   **Logging:** ELK Stack (Elasticsearch, Logstash, Kibana), Fluentd, Loki, Splunk, Graylog, CloudWatch Logs, Azure Log Analytics, Google Cloud Logging.
*   **Alerting:** Alertmanager, PagerDuty, Opsgenie, VictorOps.
*   **Tracing:** Jaeger, Zipkin, OpenTelemetry.