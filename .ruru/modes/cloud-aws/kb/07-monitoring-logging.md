# AWS Monitoring & Logging Strategy

This document outlines the strategy, patterns, and best practices for monitoring and logging AWS resources and applications, aligning with the Operational Excellence pillar of the Well-Architected Framework.

## Core Monitoring & Logging Responsibilities

*   **Define Strategy:** Establish the overall approach for monitoring metrics, collecting logs, and setting up alerts for the AWS environment.
*   **Select Tools:** Primarily leverage CloudWatch (Metrics, Logs, Alarms, Dashboards, Events/EventBridge, Logs Insights, Agent) and potentially X-Ray for tracing. Consider integration with third-party tools if necessary (coordinate with `devops-lead`).
*   **Design Implementation:** Plan how metrics and logs will be collected, aggregated, and stored. Design alarm thresholds and notification mechanisms.
*   **Delegate Configuration:** Delegate specific tasks for setting up the CloudWatch Agent, configuring log shipping, creating specific alarms, and building dashboards to `infrastructure-specialist` or `devops-lead`.
*   **Oversee & Review:** Ensure the monitoring and logging setup provides adequate visibility into system health, performance, and security.

## Key Principles

*   **Monitor Everything Relevant:** Collect metrics and logs for all critical components (infrastructure, applications).
*   **Centralize Logs:** Aggregate logs into a central system (CloudWatch Logs) for easier analysis and correlation.
*   **Actionable Alerting:** Configure alerts for conditions that require attention or intervention. Avoid excessive noise.
*   **Visualize Key Metrics:** Use dashboards to provide clear views of system health and performance.
*   **Automate Responses:** Where appropriate, trigger automated actions based on alarms (e.g., Auto Scaling, notifications).
*   **Security Focus:** Ensure security-related events are logged and monitored (CloudTrail, VPC Flow Logs, GuardDuty findings).

## Monitoring & Logging Patterns

### 1. Foundational Monitoring (CloudWatch Metrics & Alarms)

*   **Metrics Collection:**
    *   Utilize standard metrics automatically published by AWS services (EC2, ELB, RDS, S3, Lambda, etc.).
    *   Install and configure the CloudWatch Agent on EC2 instances (and on-prem servers if applicable) to collect detailed OS-level metrics (memory, disk usage, network stats).
    *   Publish custom application metrics using the `PutMetricData` API or embedded metric format in logs.
*   **Alerting (CloudWatch Alarms):**
    *   Create alarms based on critical thresholds for key metrics (e.g., high CPU, low memory, high latency, error counts, queue depth).
    *   Use composite alarms for more complex conditions.
    *   Configure actions: Send notifications to SNS topics (for email, Slack via Chatbot, PagerDuty), trigger Auto Scaling actions, trigger Step Functions or Lambda for automated remediation.
*   **Visualization (CloudWatch Dashboards):**
    *   Create dashboards summarizing the health and performance of key applications or services.
    *   Include relevant metrics, alarm statuses, and potentially log query results.

### 2. Centralized Logging (CloudWatch Logs)

*   **Log Collection:**
    *   **EC2/On-Prem:** Use the CloudWatch Agent to push OS logs (`/var/log/messages`, Windows Event Logs) and application log files.
    *   **ECS/EKS:** Use the `awslogs` log driver or a sidecar/daemonset (Fluentd, Fluent Bit) configured to send container stdout/stderr and application logs to CloudWatch Logs.
    *   **Lambda:** Logs automatically sent to CloudWatch Logs.
    *   **AWS Services:** Configure services like VPC Flow Logs, Route 53 Query Logs, CloudTrail, ELB Access Logs to deliver logs to CloudWatch Logs (or S3, potentially via Kinesis Firehose).
*   **Organization:**
    *   Use meaningful Log Group names (e.g., `/aws/ec2/my-app`, `/aws/lambda/my-function`, `/aws/vpc/flow-logs`).
    *   Use meaningful Log Stream names (often instance ID, container ID, or date-based).
*   **Retention:** Configure appropriate log retention periods per Log Group based on operational and compliance needs.
*   **Analysis (Logs Insights):** Use CloudWatch Logs Insights query language to search, analyze, and visualize log data interactively. Save common queries.

### 3. Log-Based Alerting (Metric Filters)

*   **Implementation:**
    *   Create Metric Filters on Log Groups to match specific patterns (errors, security events, specific codes).
    *   Configure filters to publish custom CloudWatch Metrics (e.g., `ApplicationErrors`, `FailedLogins`).
    *   Create CloudWatch Alarms based on these custom metrics.

### 4. Security Monitoring & Auditing

*   **CloudTrail:** Ensure enabled, logging API calls. Create alarms for critical events (Root login, IAM changes, SG changes).
*   **GuardDuty:** Enable for threat detection. Monitor findings. Create EventBridge rules/Alarms for high-severity findings.
*   **AWS Config:** Enable for configuration tracking. Use rules for compliance checks. Alert on non-compliant resources.
*   **VPC Flow Logs:** Analyze for network security issues.

### 5. Distributed Tracing (X-Ray)

*   **Implementation:**
    *   Integrate X-Ray SDK into application code.
    *   Enable tracing in supported AWS services (API Gateway, Lambda, ELB, etc.).
    *   Use the X-Ray console service map and traces to debug performance bottlenecks and errors in distributed systems.

## Best Practices

*   **Structured Logging:** Use JSON or another structured format for application logs to facilitate querying in Logs Insights. Include context (request IDs, user IDs).
*   **Consistent Naming & Tagging:** Apply consistent naming and tagging to CloudWatch resources.
*   **Alarm Actionability:** Ensure alarms are meaningful and trigger appropriate responses (manual or automated). Tune thresholds to avoid excessive noise.
*   **Dashboard Design:** Create focused, easy-to-understand dashboards for specific audiences or purposes.
*   **Regular Review:** Periodically review monitoring coverage, alarm thresholds, and dashboard relevance.

*(Coordinate with `devops-lead` on overall monitoring strategy and tool choices.)*