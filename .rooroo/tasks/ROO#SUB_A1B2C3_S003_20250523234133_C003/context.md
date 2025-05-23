Parent Task: [ROO#TASK_20250523213800_A1B2C3](/.rooroo/tasks/ROO#TASK_20250523213800_A1B2C3/context.md)
Parent Task ID: ROO#TASK_20250523213800_A1B2C3
Previous Sub-Task ID: [ROO#SUB_A1B2C3_S002_20250523234036_B002](/.rooroo/tasks/ROO#SUB_A1B2C3_S002_20250523234036_B002/context.md) (Initial App Setup & Basic Project UI)

Goal for Expert (rooroo-developer):
Implement the backend logic for Project Management features in the Sanic application.
1.  Develop Sanic endpoints and corresponding logic to:
    *   Create new FlowerPower projects (store project data, e.g., in-memory, JSON file, or simple DB for now).
    *   List existing projects.
    *   Edit existing project details.
    *   (Optional, if time permits) Delete projects.
2.  Connect the Datastar-powered frontend forms (from ROO#SUB_A1B2C3_S002) to these backend endpoints. Ensure data flows correctly and the UI updates reactively.
3.  Implement basic project configuration settings (e.g., allow editing project name and description).
4.  Develop a simple project overview dashboard page that displays a list of projects and their basic status (status can be static for now, e.g., "Active").

Key information from parent context:
- User Request (Lines [8-11](/.rooroo/tasks/ROO#TASK_20250523213800_A1B2C3/context.md:8)): Create, edit, manage projects; configure settings; project overview dashboard.
- Technical Requirements (Lines [32-34](/.rooroo/tasks/ROO#TASK_20250523213800_A1B2C3/context.md:32), [36-37](/.rooroo/tasks/ROO#TASK_20250523213800_A1B2C3/context.md:36)): Sanic, htpy, Datastar; responsive design with real-time updates; error handling.

Dependencies:
- Application structure and basic UI from [ROO#SUB_A1B2C3_S002_20250523234036_B002](/.rooroo/tasks/ROO#SUB_A1B2C3_S002_20250523234036_B002/context.md).
- Analysis report from [ROO#SUB_A1B2C3_S001_20250523233918_A001](/.rooroo/tasks/ROO#SUB_A1B2C3_S001_20250523233918_A001/context.md) for integration patterns.

Deliverables:
- Updated Sanic application source code with implemented project management backend logic and connected UI.
- Brief documentation on the API endpoints created for project management.
- Data persistence strategy for projects (e.g., file path if using JSON, or schema if using a simple DB).