Parent Task: [ROO#TASK_20250523213800_A1B2C3](/.rooroo/tasks/ROO#TASK_20250523213800_A1B2C3/context.md)
Parent Task ID: ROO#TASK_20250523213800_A1B2C3
Previous Sub-Task ID: [ROO#SUB_A1B2C3_S001_20250523233918_A001](/.rooroo/tasks/ROO#SUB_A1B2C3_S001_20250523233918_A001/context.md) (Analysis Report)

Goal for Expert (rooroo-developer):
Based on the analysis report from ROO#SUB_A1B2C3_S001_20250523233918_A001, set up the initial FlowerPower web application structure.
1.  Initialize a Sanic project.
2.  Integrate htpy for HTML templating.
3.  Integrate Datastar for reactive UI components, using the Datastar Python SDK (specifically `datastar_py/sanic.py`).
4.  Create the basic layout for the web application (e.g., navigation bar, main content area).
5.  Implement the initial UI for Project Management:
    *   A page to list existing FlowerPower projects (initially, this can be mock data or an empty list).
    *   A basic form (using htpy and Datastar components) to create a new project (name, description). This form should submit data, but full backend processing will be in a subsequent task.
6.  Ensure the application runs and basic navigation works.

Key information from parent context:
- User Request (Lines [2](/.rooroo/tasks/ROO#TASK_20250523213800_A1B2C3/context.md:2), [8-11](/.rooroo/tasks/ROO#TASK_20250523213800_A1B2C3/context.md:8), [35](/.rooroo/tasks/ROO#TASK_20250523213800_A1B2C3/context.md:35)): Create a web app for FlowerPower, starting with project management.
- Technical Requirements (Lines [32-34](/.rooroo/tasks/ROO#TASK_20250523213800_A1B2C3/context.md:32)): Sanic, htpy, Datastar.

Dependencies:
- Analysis report from [ROO#SUB_A1B2C3_S001_20250523233918_A001](/.rooroo/tasks/ROO#SUB_A1B2C3_S001_20250523233918_A001/context.md). This report will provide guidance on integration.

Deliverables:
- Source code for the initial Sanic application with basic project listing and creation UI.
- Instructions on how to run the application.
- All new files should be placed in a new subdirectory, e.g., `web_ui/`.