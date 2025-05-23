Parent Task: [ROO#TASK_20250523213800_A1B2C3](/.rooroo/tasks/ROO#TASK_20250523213800_A1B2C3/context.md)
Parent Task ID: ROO#TASK_20250523213800_A1B2C3
Previous Sub-Task ID: [ROO#SUB_A1B2C3_S004_20250523234205_D004](/.rooroo/tasks/ROO#SUB_A1B2C3_S004_20250523234205_D004/context.md) (Basic Pipeline UI/Backend)

Goal for Expert (rooroo-developer):
Implement advanced Pipeline Management features: execution, queuing, and scheduling.
1.  UI and Backend for Pipeline Execution:
    *   Allow users to select a pipeline and provide runtime arguments (form using htpy+Datastar).
    *   Sanic endpoint to trigger immediate execution of a FlowerPower pipeline using the FlowerPower library's `PipelineRunner` or equivalent. (Refer to [`src/flowerpower/pipeline/runner.py`](/src/flowerpower/pipeline/runner.py:1)).
    *   Display execution status/feedback to the user.
2.  UI and Backend for Pipeline Queuing:
    *   Allow users to queue a pipeline run with specified arguments.
    *   Sanic endpoint to add a pipeline execution job to a queue (this will likely involve integrating with FlowerPower's `JobQueueManager` - see [`src/flowerpower/job_queue/base.py`](/src/flowerpower/job_queue/base.py:1) and specific implementations like [`src/flowerpower/job_queue/apscheduler/manager.py`](/src/flowerpower/job_queue/apscheduler/manager.py:1) or [`src/flowerpower/job_queue/rq/manager.py`](/src/flowerpower/job_queue/rq/manager.py:1)).
3.  UI and Backend for Pipeline Scheduling:
    *   Allow users to schedule pipeline executions with cron-like expressions and argument settings.
    *   Sanic endpoint to interface with FlowerPower's scheduling capabilities (likely via `JobQueueManager` and its scheduling features).

Key information from parent context:
- User Request (Lines [16-18](/.rooroo/tasks/ROO#TASK_20250523213800_A1B2C3/context.md:16)): Execute pipelines, queue runs, schedule executions.
- FlowerPower library components for pipeline running ([`src/flowerpower/pipeline/runner.py`](/src/flowerpower/pipeline/runner.py:1)), job queuing ([`src/flowerpower/job_queue/base.py`](/src/flowerpower/job_queue/base.py:1)), and specific queue managers.

Dependencies:
- Application with basic pipeline management from [ROO#SUB_A1B2C3_S004_20250523234205_D004](/.rooroo/tasks/ROO#SUB_A1B2C3_S004_20250523234205_D004/context.md).
- Analysis report from [ROO#SUB_A1B2C3_S001_20250523233918_A001](/.rooroo/tasks/ROO#SUB_A1B2C3_S001_20250523233918_A001/context.md).

Deliverables:
- Updated Sanic application with pipeline execution, queuing, and scheduling functionalities.
- Documentation for new API endpoints and notes on integration with FlowerPower's core library for these features.