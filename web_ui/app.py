"""
FlowerPower Web Application
Main Sanic application with htpy templates and Datastar integration
"""

import asyncio
import json as json_module
import os
import uuid
from datetime import datetime
from typing import Any, Dict, List

import htpy as h
from datastar_py.sanic import (SSE_HEADERS, ServerSentEventGenerator,
                               datastar_respond)
from sanic import Request, Sanic
from sanic.response import html, json
from sanic_ext import Extend

# Import FlowerPower components for pipeline execution and job management
try:
    from src.flowerpower.cfg import PipelineConfig, ProjectConfig
    from src.flowerpower.fs import get_filesystem
    from src.flowerpower.job_queue.apscheduler.manager import APSManager
    from src.flowerpower.pipeline.runner import PipelineRunner
    from src.flowerpower.pipeline.visualizer import PipelineVisualizer

    FLOWERPOWER_AVAILABLE = True
except ImportError as e:
    print(f"FlowerPower imports not available: {e}")
    FLOWERPOWER_AVAILABLE = False

# Initialize Sanic app
# Create the main Sanic application instance
app = Sanic("FlowerPowerWeb")
# Allow cross-origin requests from any origin (for development/demo)
app.config.CORS_ORIGINS = "*"
# Extend Sanic with additional features (e.g., OpenAPI, CORS)
Extend(app)

# Global SSE connections storage
sse_connections = set()

# Data storage file path
PROJECTS_DATA_FILE = os.path.join(os.path.dirname(__file__), "projects_data.json")


def load_data():
    """Load all data from JSON file"""
    if os.path.exists(PROJECTS_DATA_FILE):
        try:
            with open(PROJECTS_DATA_FILE, "r") as f:
                data = json_module.load(f)
                return data
        except Exception as e:
            print(f"Error loading data: {e}")
    return {"projects": [], "pipelines": [], "last_updated": datetime.now().isoformat()}


def save_data(data):
    """Save all data to JSON file"""
    try:
        data["last_updated"] = datetime.now().isoformat()
        with open(PROJECTS_DATA_FILE, "w") as f:
            json_module.dump(data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving data: {e}")
        return False


def load_projects():
    """Load projects from JSON file"""
    data = load_data()
    return data.get("projects", [])


def save_projects(projects):
    """Save projects to JSON file"""
    data = load_data()
    data["projects"] = projects
    return save_data(data)


def load_pipelines():
    """Load pipelines from JSON file"""
    data = load_data()
    return data.get("pipelines", [])


def save_pipelines(pipelines):
    """Save pipelines to JSON file"""
    data = load_data()
    data["pipelines"] = pipelines
    return save_data(data)


def get_project_pipelines(project_id):
    """Get pipelines for a specific project"""
    pipelines = load_pipelines()
    return [p for p in pipelines if p.get("project_id") == project_id]


def get_pipeline_execution_status():
    """Get real-time pipeline execution status from FlowerPower"""
    try:
        if not FLOWERPOWER_AVAILABLE:
            return {}

        # This would connect to the job queue manager to get actual status
        # For now, return mock status based on our data
        pipelines = load_pipelines()
        status = {}
        for pipeline in pipelines:
            status[pipeline["id"]] = {
                "status": pipeline.get("status", "Inactive"),
                "last_run": pipeline.get("metadata", {}).get("last_run"),
                "next_run": pipeline.get("metadata", {}).get("next_run"),
                "run_count": pipeline.get("metadata", {}).get("run_count", 0),
            }
        return status
    except Exception as e:
        print(f"Error getting pipeline status: {e}")
        return {}


def load_job_queue_manager():
    """Load and configure the FlowerPower job queue manager"""
    try:
        if not FLOWERPOWER_AVAILABLE:
            return None

        # Initialize APScheduler manager with default configuration
        manager = APSManager(
            name="flowerpower_web_ui",
            base_dir="./",  # Use current directory as base
        )
        return manager
    except Exception as e:
        print(f"Error loading job queue manager: {e}")
        return None


def execute_pipeline_with_flowerpower(pipeline_id: int, runtime_args: dict = None):
    """
    Execute a pipeline using FlowerPower PipelineRunner.

    Loads the pipeline and project configuration, runs the pipeline, and updates metadata.
    Handles error cases and updates error counts accordingly.
    """
    try:
        if not FLOWERPOWER_AVAILABLE:
            return {"status": "error", "message": "FlowerPower not available"}

        pipelines = load_pipelines()
        pipeline = next((p for p in pipelines if p["id"] == pipeline_id), None)
        if not pipeline:
            return {"status": "error", "message": "Pipeline not found"}

        projects = load_projects()
        project = next((p for p in projects if p["id"] == pipeline["project_id"]), None)
        if not project:
            return {"status": "error", "message": "Project not found"}

        # Create FlowerPower configurations (simplified for demo)
        project_cfg = ProjectConfig(
            name=project["name"],
            base_dir="./",
        )

        pipeline_cfg = PipelineConfig(
            name=pipeline["name"],
            run={
                "inputs": runtime_args or {},
                "final_vars": [],  # Would be configured in real pipeline
                "config": {},
            },
        )

        # Execute pipeline and update metadata on success
        with PipelineRunner(project_cfg, pipeline_cfg) as runner:
            result = runner.run(inputs=runtime_args)

            # Update pipeline metadata after successful run
            pipelines = load_pipelines()
            for i, p in enumerate(pipelines):
                if p["id"] == pipeline_id:
                    pipelines[i]["metadata"]["last_run"] = datetime.now().isoformat()
                    pipelines[i]["metadata"]["run_count"] = (
                        p["metadata"].get("run_count", 0) + 1
                    )
                    pipelines[i]["metadata"]["success_count"] = (
                        p["metadata"].get("success_count", 0) + 1
                    )
                    pipelines[i]["status"] = "Active"
                    break
            save_pipelines(pipelines)

            return {
                "status": "success",
                "result": result,
                "message": "Pipeline executed successfully",
            }

    except Exception as e:
        # On error, increment error count and update status
        pipelines = load_pipelines()
        for i, p in enumerate(pipelines):
            if p["id"] == pipeline_id:
                pipelines[i]["metadata"]["error_count"] = (
                    p["metadata"].get("error_count", 0) + 1
                )
                pipelines[i]["status"] = "Error"
                break
        save_pipelines(pipelines)

        return {"status": "error", "message": f"Pipeline execution failed: {str(e)}"}


def queue_pipeline_execution(
    pipeline_id: int, runtime_args: dict = None, run_at: str = None
):
    """Queue a pipeline for execution using FlowerPower job queue"""
    try:
        if not FLOWERPOWER_AVAILABLE:
            return {"status": "error", "message": "FlowerPower not available"}

        manager = load_job_queue_manager()
        if not manager:
            return {"status": "error", "message": "Job queue manager not available"}

        pipelines = load_pipelines()
        pipeline = next((p for p in pipelines if p["id"] == pipeline_id), None)
        if not pipeline:
            return {"status": "error", "message": "Pipeline not found"}

        # Define the job function that will execute the pipeline
        def pipeline_job():
            return execute_pipeline_with_flowerpower(pipeline_id, runtime_args)

        # Add job to queue
        if run_at:
            # Schedule for later execution
            run_at_dt = (
                datetime.fromisoformat(run_at) if isinstance(run_at, str) else run_at
            )
            job_id = manager.add_job(pipeline_job, run_at=run_at_dt)
        else:
            # Queue for immediate execution
            job_id = manager.add_job(pipeline_job)

        return {
            "status": "success",
            "job_id": job_id,
            "message": f"Pipeline queued successfully with job ID: {job_id}",
        }

    except Exception as e:
        return {"status": "error", "message": f"Failed to queue pipeline: {str(e)}"}


def schedule_pipeline_execution(
    pipeline_id: int, cron_expression: str, runtime_args: dict = None
):
    """Schedule a pipeline for recurring execution using cron expression"""
    try:
        if not FLOWERPOWER_AVAILABLE:
            return {"status": "error", "message": "FlowerPower not available"}

        manager = load_job_queue_manager()
        if not manager:
            return {"status": "error", "message": "Job queue manager not available"}

        pipelines = load_pipelines()
        pipeline = next((p for p in pipelines if p["id"] == pipeline_id), None)
        if not pipeline:
            return {"status": "error", "message": "Pipeline not found"}

        # Define the job function that will execute the pipeline
        def pipeline_job():
            return execute_pipeline_with_flowerpower(pipeline_id, runtime_args)

        # Add schedule
        schedule_id = manager.add_schedule(
            pipeline_job,
            cron=cron_expression,
            schedule_id=f"pipeline_{pipeline_id}_schedule",
        )

        # Update pipeline configuration
        pipelines = load_pipelines()
        for i, p in enumerate(pipelines):
            if p["id"] == pipeline_id:
                pipelines[i]["config"]["schedule"]["enabled"] = True
                pipelines[i]["config"]["schedule"]["cron"] = cron_expression
                pipelines[i]["status"] = "Scheduled"
                break
        save_pipelines(pipelines)

        return {
            "status": "success",
            "schedule_id": schedule_id,
            "message": f"Pipeline scheduled successfully with ID: {schedule_id}",
        }

    except Exception as e:
        return {"status": "error", "message": f"Failed to schedule pipeline: {str(e)}"}


def get_pipeline_dag_data(pipeline_id: int):
    """Extract DAG structure from FlowerPower pipeline for visualization"""
    try:
        if not FLOWERPOWER_AVAILABLE:
            return {"status": "error", "message": "FlowerPower not available"}

        pipelines = load_pipelines()
        pipeline = next((p for p in pipelines if p["id"] == pipeline_id), None)
        if not pipeline:
            return {"status": "error", "message": "Pipeline not found"}

        projects = load_projects()
        project = next((p for p in projects if p["id"] == pipeline["project_id"]), None)
        if not project:
            return {"status": "error", "message": "Project not found"}

        # Create FlowerPower configurations
        project_cfg = ProjectConfig(
            name=project["name"],
            base_dir="./",
        )

        # Get filesystem
        fs = get_filesystem("./")

        # Create visualizer
        visualizer = PipelineVisualizer(project_cfg, fs)

        try:
            # Get the raw DAG object from Hamilton
            dag_obj = visualizer.show_dag(name=pipeline["name"], raw=True)

            # Extract node and edge data from the graphviz object
            nodes = []
            edges = []

            # Parse the graphviz source to extract nodes and edges
            if hasattr(dag_obj, "source"):
                lines = dag_obj.source.split("\n")
                for line in lines:
                    line = line.strip()
                    if "->" in line:
                        # This is an edge
                        parts = line.split("->")
                        if len(parts) == 2:
                            source = parts[0].strip().strip('"').strip()
                            target = (
                                parts[1]
                                .strip()
                                .split("[")[0]
                                .strip()
                                .strip('"')
                                .strip()
                            )
                            if source and target:
                                edges.append({
                                    "id": f"{source}->{target}",
                                    "source": source,
                                    "target": target,
                                })
                    elif "[label=" in line and not "->" in line:
                        # This is a node definition
                        node_name = line.split("[")[0].strip().strip('"')
                        if node_name and node_name not in ["digraph", "}", "{"]:
                            # Extract label if available
                            label = node_name
                            if "[label=" in line:
                                try:
                                    label_part = line.split("[label=")[1].split("]")[0]
                                    label = label_part.strip('"').strip("'")
                                except:
                                    pass

                            nodes.append({
                                "id": node_name,
                                "label": label,
                                "type": "function",
                            })

            # If we couldn't parse nodes from source, create basic nodes from edges
            if not nodes:
                all_node_ids = set()
                for edge in edges:
                    all_node_ids.add(edge["source"])
                    all_node_ids.add(edge["target"])

                for node_id in all_node_ids:
                    nodes.append({"id": node_id, "label": node_id, "type": "function"})

            return {
                "status": "success",
                "pipeline": {
                    "id": pipeline_id,
                    "name": pipeline["name"],
                    "project": project["name"],
                },
                "dag": {"nodes": nodes, "edges": edges},
            }

        except Exception as viz_error:
            # Fallback: create a simple mock DAG structure
            print(f"Error getting actual DAG, creating mock: {viz_error}")
            return {
                "status": "success",
                "pipeline": {
                    "id": pipeline_id,
                    "name": pipeline["name"],
                    "project": project["name"],
                },
                "dag": {
                    "nodes": [
                        {"id": "input", "label": "Input Data", "type": "input"},
                        {"id": "process", "label": "Process", "type": "function"},
                        {"id": "output", "label": "Output", "type": "output"},
                    ],
                    "edges": [
                        {
                            "id": "input->process",
                            "source": "input",
                            "target": "process",
                        },
                        {
                            "id": "process->output",
                            "source": "process",
                            "target": "output",
                        },
                    ],
                },
            }

    except Exception as e:
        return {"status": "error", "message": f"Failed to get pipeline DAG: {str(e)}"}


async def emit_to_all(element_id: str, data: Dict[str, Any]):
    """Send data to all connected SSE clients"""
    if not sse_connections:
        return

    message = {"selector": f"#{element_id}", "merge_type": "innerHTML", **data}

    # Remove disconnected connections
    disconnected = set()
    for connection in sse_connections:
        try:
            await connection.put(message)
        except Exception:
            disconnected.add(connection)

    sse_connections.difference_update(disconnected)


def base_layout(title: str, content: Any) -> str:
    """Base HTML layout with navigation and Datastar setup"""
    return str(
        h.html[
            h.head[
                h.meta(charset="utf-8"),
                h.meta(name="viewport", content="width=device-width, initial-scale=1"),
                h.title[f"{title} - FlowerPower"],
                h.link(
                    href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css",
                    rel="stylesheet",
                ),
                h.script(src="https://unpkg.com/@starfederation/datastar@latest"),
            ],
            h.body(**{"data-ds-stream": "/datastar/stream"})[
                h.nav(class_="navbar navbar-expand-lg navbar-dark bg-primary")[
                    h.div(class_="container-fluid")[
                        h.a(class_="navbar-brand", href="/")["FlowerPower"],
                        h.ul(class_="navbar-nav")[
                            h.li(class_="nav-item")[
                                h.a(class_="nav-link", href="/dashboard")["Dashboard"]
                            ],
                            h.li(class_="nav-item")[
                                h.a(class_="nav-link", href="/projects")["Projects"]
                            ],
                            h.li(class_="nav-item")[
                                h.a(class_="nav-link", href="/projects/new")[
                                    "New Project"
                                ]
                            ],
                            h.li(class_="nav-item")[
                                h.a(class_="nav-link", href="/pipelines")["Pipelines"]
                            ],
                            h.li(class_="nav-item")[
                                h.a(class_="nav-link", href="/jobs")["Job Queue"]
                            ],
                        ],
                    ],
                ],
                h.div(class_="main-content")[h.div(class_="container mt-4")[content],],
            ],
        ]
    )


def project_card(project: Dict[str, Any]) -> Any:
    """Generate a project card component"""
    status = project.get("status", "Unknown")
    status_class = {
        "Active": "success",
        "Inactive": "secondary",
        "Error": "danger",
    }.get(status, "secondary")

    # Count pipelines for this project
    pipelines = get_project_pipelines(project["id"])
    pipeline_count = len(pipelines)

    return h.div(class_="col-md-6 col-lg-4 mb-3")[
        h.div(class_="card")[
            h.div(class_="card-body")[
                h.h5(class_="card-title")[project["name"]],
                h.p(class_="card-text")[project.get("description", "No description")],
                h.div(class_="d-flex justify-content-between align-items-center mb-2")[
                    h.span(class_=f"badge bg-{status_class}")[status],
                    h.small(class_="text-muted")[
                        f"{pipeline_count} pipeline{'s' if pipeline_count != 1 else ''}"
                    ],
                ],
                h.div(class_="d-flex justify-content-between align-items-center")[
                    h.div[
                        h.a(
                            class_="btn btn-primary btn-sm me-2",
                            href=f"/projects/{project['id']}",
                        )["View"],
                        h.a(
                            class_="btn btn-outline-secondary btn-sm me-2",
                            href=f"/projects/{project['id']}/edit",
                        )["Edit"],
                    ],
                    h.div[
                        h.a(
                            class_="btn btn-outline-info btn-sm me-1",
                            href=f"/projects/{project['id']}/pipelines",
                        )["Pipelines"],
                        h.a(
                            class_="btn btn-outline-success btn-sm",
                            href=f"/projects/{project['id']}/pipelines/new",
                        )["+ Pipeline"],
                    ],
                ],
            ]
        ]
    ]


def pipeline_card(pipeline: Dict[str, Any], project_name: str = None) -> Any:
    """Generate a pipeline card component"""
    status = pipeline.get("status", "Unknown")
    status_class = {
        "Active": "success",
        "Inactive": "secondary",
        "Error": "danger",
        "Running": "primary",
        "Scheduled": "info",
    }.get(status, "secondary")

    pipeline_type = pipeline.get("type", "batch")
    type_class = {
        "batch": "secondary",
        "streaming": "info",
        "scheduled": "warning",
    }.get(pipeline_type, "secondary")

    return h.div(class_="col-md-6 col-lg-4 mb-3")[
        h.div(class_="card")[
            h.div(class_="card-body")[
                h.h5(class_="card-title")[pipeline["name"]],
                h.p(class_="card-text")[pipeline.get("description", "No description")],
                h.div(class_="d-flex justify-content-between align-items-center mb-2")[
                    h.div[
                        h.span(class_=f"badge bg-{status_class} me-2")[status],
                        h.span(class_=f"badge bg-{type_class}")[pipeline_type],
                    ]
                ],
                (
                    h.div(class_="mb-2")[
                        h.small(class_="text-muted")[f"Project: {project_name}"]
                    ]
                    if project_name
                    else h.div()
                ),
                h.div(class_="d-flex justify-content-between align-items-center")[
                    h.div[
                        h.a(
                            class_="btn btn-primary btn-sm me-2",
                            href=f"/pipelines/{pipeline['id']}",
                        )["View"],
                        h.a(
                            class_="btn btn-outline-secondary btn-sm me-2",
                            href=f"/pipelines/{pipeline['id']}/edit",
                        )["Edit"],
                    ],
                    h.div[
                        h.a(
                            class_="btn btn-success btn-sm me-1",
                            href=f"/pipelines/{pipeline['id']}/run",
                        )["Run"],
                        h.a(
                            class_="btn btn-outline-info btn-sm me-1",
                            href=f"/pipelines/{pipeline['id']}/visualize",
                        )["DAG"],
                        h.a(
                            class_="btn btn-outline-secondary btn-sm",
                            href=f"/pipelines/{pipeline['id']}/schedule",
                        )["Schedule"],
                    ],
                ],
            ]
        ]
    ]


def get_pipeline_status_from_flowerpower(pipeline_name: str) -> str:
    """Get pipeline status from FlowerPower library"""
    try:
        # Import FlowerPower pipeline manager
        from src.flowerpower.pipeline import PipelineManager

        # Create manager instance - this might need project-specific config
        manager = PipelineManager()

        # Check if pipeline exists in FlowerPower
        available_pipelines = manager.list_pipelines()
        if pipeline_name in available_pipelines:
            # For now, return 'Active' if pipeline exists
            # In future, we could check actual execution status
            return "Active"
        else:
            return "Inactive"
    except Exception as e:
        print(f"Error checking FlowerPower status for {pipeline_name}: {e}")
        return "Unknown"


@app.route("/")
async def index(request: Request):
    """Homepage"""
    projects = load_projects()
    total_projects = len(projects)

    content = h.div[
        h.h1["Welcome to FlowerPower"],
        h.p(class_="lead")["Manage your automation projects with ease."],
        h.div(class_="row")[
            h.div(class_="col-md-6")[
                h.div(class_="card")[
                    h.div(class_="card-body text-center")[
                        h.h3(class_="card-title")[str(total_projects)],
                        h.p(class_="card-text")["Total Projects"],
                    ]
                ]
            ],
        ],
        h.div(class_="mt-4")[
            h.a(class_="btn btn-primary btn-lg me-3", href="/dashboard")["Dashboard"],
            h.a(class_="btn btn-outline-primary btn-lg", href="/projects")[
                "View Projects"
            ],
        ],
    ]

    return html(base_layout("Home", content))


@app.route("/projects")
async def projects_list(request: Request):
    """Projects listing page"""
    projects = load_projects()

    content = h.div[
        h.h1["Projects"],
        h.a(class_="btn btn-success mb-3", href="/projects/new")["Create New Project"],
        h.div(id="projects-list", **{"data-ds-id": "projects-list"})[
            h.div(class_="row")[[project_card(project) for project in projects]]
            if projects
            else h.div(class_="text-center p-4")[
                h.p(class_="text-muted")["No projects found."],
                h.a(class_="btn btn-primary", href="/projects/new")[
                    "Create your first project"
                ],
            ]
        ],
    ]

    return html(base_layout("Projects", content))


@app.route("/projects/new")
async def new_project(request: Request):
    """New project form"""
    content = h.div[
        h.h1["Create New Project"],
        h.form(
            action="/projects",
            method="post",
            **{"data-ds-post": "/projects", "data-ds-target": "#form-result"},
        )[
            h.div(class_="mb-3")[
                h.label(for_="name", class_="form-label")["Project Name"],
                h.input_(
                    type="text",
                    id="name",
                    name="name",
                    class_="form-control",
                    required=True,
                ),
            ],
            h.div(class_="mb-3")[
                h.label(for_="description", class_="form-label")["Description"],
                h.textarea(
                    id="description",
                    name="description",
                    class_="form-control",
                    rows="3",
                ),
            ],
            h.div(class_="mb-3")[
                h.button(
                    "Create Project", type="submit", class_="btn btn-primary me-2"
                ),
                h.a("Cancel", href="/projects", class_="btn btn-secondary"),
            ],
        ],
        h.div(id="form-result", **{"data-ds-id": "form-result"}),
    ]
    return html(base_layout("New Project", content))


@app.route("/projects", methods=["POST"])
async def create_project(request: Request):
    """Create a new project"""
    try:
        name = request.form.get("name")
        description = request.form.get("description", "")

        if not name:
            await emit_to_all(
                "form-result",
                {
                    "content": str(
                        h.div("Project name is required.", class_="alert alert-danger")
                    )
                },
            )
            return json({"status": "error", "message": "Project name is required"})

        projects = load_projects()

        # Check if project name already exists
        if any(p["name"].lower() == name.lower() for p in projects):
            await emit_to_all(
                "form-result",
                {
                    "content": str(
                        h.div(
                            "A project with this name already exists.",
                            class_="alert alert-danger",
                        )
                    )
                },
            )
            return json({"status": "error", "message": "Project name already exists"})

        # Create new project
        new_project = {
            "id": len(projects) + 1,
            "name": name,
            "description": description,
            "status": "Active",
            "created_at": datetime.now().isoformat(),
            "config": {
                "environment": "development",
                "auto_run": False,
                "notifications": False,
                "retry_attempts": 3,
            },
        }

        projects.append(new_project)

        if not save_projects(projects):
            await emit_to_all(
                "form-result",
                {
                    "content": str(
                        h.div(
                            "Error saving project. Please try again.",
                            class_="alert alert-danger",
                        )
                    )
                },
            )
            return json({"status": "error", "message": "Failed to save project"})

        # Success response
        success_content = h.div[
            h.div(
                f"Project '{name}' created successfully!", class_="alert alert-success"
            ),
            h.script["setTimeout(() => window.location.href = '/projects', 2000);"],
        ]

        await emit_to_all("form-result", {"content": str(success_content)})

        return json({"status": "success", "project_id": new_project["id"]})

    except Exception as e:
        await emit_to_all(
            "form-result",
            {
                "content": str(
                    h.div(
                        f"Error creating project: {str(e)}", class_="alert alert-danger"
                    )
                )
            },
        )
        return json({"status": "error", "message": str(e)})


@app.route("/projects/<project_id:int>")
async def project_detail(request: Request, project_id: int):
    """Project detail page"""
    projects = load_projects()
    project = next((p for p in projects if p["id"] == project_id), None)

    if not project:
        content = h.div[
            h.h1["Project Not Found"],
            h.p["The requested project could not be found."],
            h.a("Back to Projects", href="/projects", class_="btn btn-primary"),
        ]
        return html(base_layout("Project Not Found", content))

    status = project.get("status", "Unknown")
    status_class = {
        "Active": "success",
        "Inactive": "secondary",
        "Error": "danger",
    }.get(status, "secondary")

    config = project.get("config", {})

    content = h.div[
        h.div(class_="d-flex justify-content-between align-items-center mb-4")[
            h.div[
                h.h1(class_="d-inline me-3")[project["name"]],
                h.span(class_=f"badge bg-{status_class}")[status],
            ],
            h.div[
                h.a(
                    "Back to Projects",
                    href="/projects",
                    class_="btn btn-outline-secondary me-2",
                ),
                h.a(
                    "Edit Project",
                    href=f"/projects/{project_id}/edit",
                    class_="btn btn-primary me-2",
                ),
                h.a(
                    "Configuration",
                    href=f"/projects/{project_id}/config",
                    class_="btn btn-outline-info",
                ),
            ],
        ],
        h.div(class_="card mb-3")[
            h.div(class_="card-body")[
                h.h5["Description"],
                h.p[project.get("description") or "No description provided."],
            ],
        ],
        h.div(class_="card mb-3")[
            h.div(class_="card-body")[
                h.h5["Project Details"],
                h.dl(class_="row")[
                    h.dt(class_="col-sm-3")["ID"],
                    h.dd(class_="col-sm-9")[str(project["id"])],
                    h.dt(class_="col-sm-3")["Status"],
                    h.dd(class_="col-sm-9")[status],
                    h.dt(class_="col-sm-3")["Created"],
                    h.dd(class_="col-sm-9")[
                        project["created_at"][:19].replace("T", " ")
                    ],
                    h.dt(class_="col-sm-3")["Updated"],
                    h.dd(class_="col-sm-9")[
                        project.get("updated_at", "N/A")[:19].replace("T", " ")
                        if project.get("updated_at") != "N/A"
                        else "N/A"
                    ],
                ],
            ],
        ],
        h.div(class_="card")[
            h.div(class_="card-body")[
                h.h5["Configuration"],
                h.dl(class_="row")[
                    h.dt(class_="col-sm-3")["Environment"],
                    h.dd(class_="col-sm-9")[config.get("environment", "N/A")],
                    h.dt(class_="col-sm-3")["Auto Run"],
                    h.dd(class_="col-sm-9")["Yes" if config.get("auto_run") else "No"],
                    h.dt(class_="col-sm-3")["Notifications"],
                    h.dd(class_="col-sm-9")[
                        "Enabled" if config.get("notifications") else "Disabled"
                    ],
                    h.dt(class_="col-sm-3")["Retry Attempts"],
                    h.dd(class_="col-sm-9")[str(config.get("retry_attempts", "N/A"))],
                ],
            ],
        ],
    ]
    return html(base_layout(f"Project: {project['name']}", content))


@app.route("/dashboard")
async def dashboard(request: Request):
    """Dashboard page"""
    projects = load_projects()

    # Calculate statistics
    total_projects = len(projects)
    active_projects = len([p for p in projects if p.get("status") == "Active"])
    inactive_projects = len([p for p in projects if p.get("status") == "Inactive"])
    error_projects = len([p for p in projects if p.get("status") == "Error"])

    # Get recent projects (last 5)
    recent_projects = sorted(
        projects, key=lambda x: x.get("created_at", ""), reverse=True
    )[:5]

    content = h.div[
        h.h1["Project Dashboard"],
        # Statistics cards
        h.div(class_="row mb-4")[
            h.div(class_="col-md-3")[
                h.div(class_="card")[
                    h.div(class_="card-body text-center")[
                        h.h3(class_="card-title text-primary")[str(total_projects)],
                        h.p(class_="card-text")["Total Projects"],
                    ],
                ],
            ],
            h.div(class_="col-md-3")[
                h.div(class_="card")[
                    h.div(class_="card-body text-center")[
                        h.h3(class_="card-title text-success")[str(active_projects)],
                        h.p(class_="card-text")["Active Projects"],
                    ],
                ],
            ],
            h.div(class_="col-md-3")[
                h.div(class_="card")[
                    h.div(class_="card-body text-center")[
                        h.h3(class_="card-title text-secondary")[
                            str(inactive_projects)
                        ],
                        h.p(class_="card-text")["Inactive Projects"],
                    ],
                ],
            ],
            h.div(class_="col-md-3")[
                h.div(class_="card")[
                    h.div(class_="card-body text-center")[
                        h.h3(class_="card-title text-danger")[str(error_projects)],
                        h.p(class_="card-text")["Error Projects"],
                    ],
                ],
            ],
        ],
        # Recent projects
        h.div(class_="mb-4")[
            h.h2["Recent Projects"],
            h.div(class_="row")[[project_card(project) for project in recent_projects]]
            if recent_projects
            else h.div(class_="text-center p-4")[
                h.p(class_="text-muted")["No projects found."],
                h.a(
                    "Create your first project",
                    href="/projects/new",
                    class_="btn btn-primary",
                ),
            ],
        ],
        # Quick actions
        h.div[
            h.h2["Quick Actions"],
            h.div(class_="mb-3")[
                h.a(
                    "Create New Project",
                    href="/projects/new",
                    class_="btn btn-primary me-2",
                ),
                h.a(
                    "View All Projects",
                    href="/projects",
                    class_="btn btn-outline-primary",
                ),
            ],
        ],
    ]
    return html(base_layout("Dashboard", content))


# ================== PIPELINE ROUTES ==================


@app.route("/pipelines")
async def pipelines_list(request: Request):
    """Pipelines listing page"""
    pipelines = load_pipelines()
    projects = load_projects()

    # Create a mapping of project IDs to names for display
    project_map = {p["id"]: p["name"] for p in projects}

    content = h.div[
        h.h1["Pipelines"],
        h.div(class_="d-flex justify-content-between align-items-center mb-3")[
            h.div[
                h.a(class_="btn btn-success me-2", href="/pipelines/new")[
                    "Create New Pipeline"
                ],
                h.a(class_="btn btn-outline-primary", href="/projects")[
                    "Manage Projects"
                ],
            ]
        ],
        h.div(id="pipelines-list", **{"data-ds-id": "pipelines-list"})[
            h.div(class_="row")[
                [
                    pipeline_card(pipeline, project_map.get(pipeline.get("project_id")))
                    for pipeline in pipelines
                ]
            ]
            if pipelines
            else h.div(class_="text-center p-4")[
                h.p(class_="text-muted")["No pipelines found."],
                h.a(class_="btn btn-primary", href="/pipelines/new")[
                    "Create your first pipeline"
                ],
            ]
        ],
    ]

    return html(base_layout("Pipelines", content))


@app.route("/pipelines/new")
async def new_pipeline(request: Request):
    """New pipeline form"""
    projects = load_projects()

    if not projects:
        content = h.div[
            h.h1["Create New Pipeline"],
            h.div(class_="alert alert-warning")[
                h.p["You need to create a project first before adding pipelines."],
                h.a("Create Project", href="/projects/new", class_="btn btn-primary"),
            ],
        ]
        return html(base_layout("New Pipeline", content))

    content = h.div[
        h.h1["Create New Pipeline"],
        h.form(
            action="/pipelines",
            method="post",
            **{"data-ds-post": "/pipelines", "data-ds-target": "#form-result"},
        )[
            h.div(class_="mb-3")[
                h.label(for_="project_id", class_="form-label")["Project"],
                h.select(
                    id="project_id",
                    name="project_id",
                    class_="form-select",
                    required=True,
                )[
                    h.option(value="", selected=True)["Select a project..."],
                    [
                        h.option(value=str(project["id"]))[project["name"]]
                        for project in projects
                    ],
                ],
            ],
            h.div(class_="mb-3")[
                h.label(for_="name", class_="form-label")["Pipeline Name"],
                h.input_(
                    type="text",
                    id="name",
                    name="name",
                    class_="form-control",
                    required=True,
                    placeholder="e.g., data_processing_pipeline",
                ),
            ],
            h.div(class_="mb-3")[
                h.label(for_="description", class_="form-label")["Description"],
                h.textarea(
                    id="description",
                    name="description",
                    class_="form-control",
                    rows="3",
                    placeholder="Brief description of what this pipeline does...",
                ),
            ],
            h.div(class_="mb-3")[
                h.label(for_="type", class_="form-label")["Pipeline Type"],
                h.select(id="type", name="type", class_="form-select")[
                    h.option(value="batch", selected=True)["Batch Processing"],
                    h.option(value="streaming")["Streaming"],
                    h.option(value="scheduled")["Scheduled"],
                ],
            ],
            h.div(class_="mb-3")[
                h.h5["Configuration Options"],
                h.div(class_="row")[
                    h.div(class_="col-md-6")[
                        h.div(class_="form-check")[
                            h.input_(
                                class_="form-check-input",
                                type="checkbox",
                                id="auto_run",
                                name="auto_run",
                            ),
                            h.label(class_="form-check-label", for_="auto_run")[
                                "Auto-run on schedule"
                            ],
                        ],
                    ],
                    h.div(class_="col-md-6")[
                        h.div(class_="form-check")[
                            h.input_(
                                class_="form-check-input",
                                type="checkbox",
                                id="notifications",
                                name="notifications",
                                checked=True,
                            ),
                            h.label(class_="form-check-label", for_="notifications")[
                                "Enable notifications"
                            ],
                        ],
                    ],
                ],
                h.div(class_="row mt-2")[
                    h.div(class_="col-md-6")[
                        h.label(for_="retry_attempts", class_="form-label")[
                            "Retry Attempts"
                        ],
                        h.input_(
                            type="number",
                            id="retry_attempts",
                            name="retry_attempts",
                            class_="form-control",
                            value="3",
                            min="0",
                            max="10",
                        ),
                    ],
                    h.div(class_="col-md-6")[
                        h.label(for_="timeout", class_="form-label")[
                            "Timeout (seconds)"
                        ],
                        h.input_(
                            type="number",
                            id="timeout",
                            name="timeout",
                            class_="form-control",
                            value="3600",
                            min="1",
                        ),
                    ],
                ],
            ],
            h.div(class_="mb-3")[
                h.button(
                    "Create Pipeline", type="submit", class_="btn btn-primary me-2"
                ),
                h.a("Cancel", href="/pipelines", class_="btn btn-secondary"),
            ],
        ],
        h.div(id="form-result", **{"data-ds-id": "form-result"}),
    ]
    return html(base_layout("New Pipeline", content))


@app.route("/pipelines", methods=["POST"])
async def create_pipeline(request: Request):
    """Create a new pipeline"""
    try:
        project_id = request.form.get("project_id")
        name = request.form.get("name")
        description = request.form.get("description", "")
        pipeline_type = request.form.get("type", "batch")
        auto_run = bool(request.form.get("auto_run"))
        notifications = bool(request.form.get("notifications"))
        retry_attempts = int(request.form.get("retry_attempts", 3))
        timeout = int(request.form.get("timeout", 3600))

        if not project_id or not name:
            await emit_to_all(
                "form-result",
                {
                    "content": str(
                        h.div(
                            "Project and pipeline name are required.",
                            class_="alert alert-danger",
                        )
                    )
                },
            )
            return json({
                "status": "error",
                "message": "Project and pipeline name are required",
            })

        # Validate project exists
        projects = load_projects()
        project = next((p for p in projects if p["id"] == int(project_id)), None)
        if not project:
            await emit_to_all(
                "form-result",
                {
                    "content": str(
                        h.div(
                            "Selected project does not exist.",
                            class_="alert alert-danger",
                        )
                    )
                },
            )
            return json({"status": "error", "message": "Project not found"})

        pipelines = load_pipelines()

        # Check if pipeline name already exists in this project
        if any(
            p["name"].lower() == name.lower() and p["project_id"] == int(project_id)
            for p in pipelines
        ):
            await emit_to_all(
                "form-result",
                {
                    "content": str(
                        h.div(
                            "A pipeline with this name already exists in the selected project.",
                            class_="alert alert-danger",
                        )
                    )
                },
            )
            return json({
                "status": "error",
                "message": "Pipeline name already exists in project",
            })

        # Create new pipeline
        new_pipeline = {
            "id": len(pipelines) + 1,
            "project_id": int(project_id),
            "name": name,
            "description": description,
            "type": pipeline_type,
            "status": "Inactive",  # Default status, will be updated based on FlowerPower integration
            "created_at": datetime.now().isoformat(),
            "config": {
                "auto_run": auto_run,
                "notifications": notifications,
                "retry_attempts": retry_attempts,
                "timeout": timeout,
                "executor": "local",
                "schedule": {"enabled": False, "cron": None, "interval": None},
            },
            "metadata": {
                "last_run": None,
                "next_run": None,
                "run_count": 0,
                "success_count": 0,
                "error_count": 0,
            },
        }

        pipelines.append(new_pipeline)

        if not save_pipelines(pipelines):
            await emit_to_all(
                "form-result",
                {
                    "content": str(
                        h.div(
                            "Error saving pipeline. Please try again.",
                            class_="alert alert-danger",
                        )
                    )
                },
            )
            return json({"status": "error", "message": "Failed to save pipeline"})

        # Success response
        success_content = h.div[
            h.div(
                f"Pipeline '{name}' created successfully in project '{project['name']}'!",
                class_="alert alert-success",
            ),
            h.script["setTimeout(() => window.location.href = '/pipelines', 2000);"],
        ]

        await emit_to_all("form-result", {"content": str(success_content)})

        return json({"status": "success", "pipeline_id": new_pipeline["id"]})

    except Exception as e:
        await emit_to_all(
            "form-result",
            {
                "content": str(
                    h.div(
                        f"Error creating pipeline: {str(e)}",
                        class_="alert alert-danger",
                    )
                )
            },
        )
        return json({"status": "error", "message": str(e)})


@app.route("/pipelines/<pipeline_id:int>")
async def pipeline_detail(request: Request, pipeline_id: int):
    """Pipeline detail page"""
    pipelines = load_pipelines()
    pipeline = next((p for p in pipelines if p["id"] == pipeline_id), None)

    if not pipeline:
        content = h.div[
            h.h1["Pipeline Not Found"],
            h.p["The requested pipeline could not be found."],
            h.a("Back to Pipelines", href="/pipelines", class_="btn btn-primary"),
        ]
        return html(base_layout("Pipeline Not Found", content))

    # Get project information
    projects = load_projects()
    project = next((p for p in projects if p["id"] == pipeline["project_id"]), None)
    project_name = project["name"] if project else "Unknown Project"

    status = pipeline.get("status", "Unknown")
    status_class = {
        "Active": "success",
        "Inactive": "secondary",
        "Error": "danger",
        "Running": "primary",
        "Scheduled": "info",
    }.get(status, "secondary")

    config = pipeline.get("config", {})
    metadata = pipeline.get("metadata", {})

    content = h.div[
        h.div(class_="d-flex justify-content-between align-items-center mb-4")[
            h.div[
                h.h1(class_="d-inline me-3")[pipeline["name"]],
                h.span(class_=f"badge bg-{status_class} me-2")[status],
                h.span(class_="badge bg-secondary")[pipeline.get("type", "batch")],
            ],
            h.div[
                h.a(
                    "Back to Pipelines",
                    href="/pipelines",
                    class_="btn btn-outline-secondary me-2",
                ),
                h.a(
                    "Edit Pipeline",
                    href=f"/pipelines/{pipeline_id}/edit",
                    class_="btn btn-primary me-2",
                ),
                h.a(
                    "Run Now",
                    href=f"/pipelines/{pipeline_id}/run",
                    class_="btn btn-success",
                ),
            ],
        ],
        h.div(class_="row")[
            h.div(class_="col-md-8")[
                h.div(class_="card mb-3")[
                    h.div(class_="card-body")[
                        h.h5["Description"],
                        h.p[pipeline.get("description") or "No description provided."],
                    ],
                ],
                h.div(class_="card mb-3")[
                    h.div(class_="card-body")[
                        h.h5["Pipeline Details"],
                        h.dl(class_="row")[
                            h.dt(class_="col-sm-3")["ID"],
                            h.dd(class_="col-sm-9")[str(pipeline["id"])],
                            h.dt(class_="col-sm-3")["Project"],
                            h.dd(class_="col-sm-9")[
                                h.a(
                                    project_name,
                                    href=f"/projects/{pipeline['project_id']}",
                                    class_="text-decoration-none",
                                )
                            ],
                            h.dt(class_="col-sm-3")["Type"],
                            h.dd(class_="col-sm-9")[pipeline.get("type", "batch")],
                            h.dt(class_="col-sm-3")["Status"],
                            h.dd(class_="col-sm-9")[status],
                            h.dt(class_="col-sm-3")["Created"],
                            h.dd(class_="col-sm-9")[
                                pipeline["created_at"][:19].replace("T", " ")
                            ],
                        ],
                    ],
                ],
                h.div(class_="card")[
                    h.div(class_="card-body")[
                        h.h5["Configuration"],
                        h.dl(class_="row")[
                            h.dt(class_="col-sm-3")["Auto Run"],
                            h.dd(class_="col-sm-9")[
                                "Yes" if config.get("auto_run") else "No"
                            ],
                            h.dt(class_="col-sm-3")["Notifications"],
                            h.dd(class_="col-sm-9")[
                                "Enabled" if config.get("notifications") else "Disabled"
                            ],
                            h.dt(class_="col-sm-3")["Retry Attempts"],
                            h.dd(class_="col-sm-9")[
                                str(config.get("retry_attempts", "N/A"))
                            ],
                            h.dt(class_="col-sm-3")["Timeout"],
                            h.dd(class_="col-sm-9")[
                                f"{config.get('timeout', 'N/A')} seconds"
                            ],
                            h.dt(class_="col-sm-3")["Executor"],
                            h.dd(class_="col-sm-9")[config.get("executor", "local")],
                        ],
                    ],
                ],
            ],
            h.div(class_="col-md-4")[
                h.div(class_="card mb-3")[
                    h.div(class_="card-body")[
                        h.h5["Runtime Statistics"],
                        h.dl(class_="row")[
                            h.dt(class_="col-sm-6")["Total Runs"],
                            h.dd(class_="col-sm-6")[str(metadata.get("run_count", 0))],
                            h.dt(class_="col-sm-6")["Successful"],
                            h.dd(class_="col-sm-6")[
                                str(metadata.get("success_count", 0))
                            ],
                            h.dt(class_="col-sm-6")["Errors"],
                            h.dd(class_="col-sm-6")[
                                str(metadata.get("error_count", 0))
                            ],
                            h.dt(class_="col-sm-6")["Last Run"],
                            h.dd(class_="col-sm-6")[
                                metadata.get("last_run", "Never")[:19].replace("T", " ")
                                if metadata.get("last_run") != "Never"
                                else "Never"
                            ],
                            h.dt(class_="col-sm-6")["Next Run"],
                            h.dd(class_="col-sm-6")[
                                metadata.get("next_run", "Not scheduled")[:19].replace(
                                    "T", " "
                                )
                                if metadata.get("next_run")
                                and metadata.get("next_run") != "Not scheduled"
                                else "Not scheduled"
                            ],
                        ],
                    ],
                ],
                h.div(class_="card")[
                    h.div(class_="card-body")[
                        h.h5["Quick Actions"],
                        h.div(class_="d-grid gap-2")[
                            h.a(
                                "Run Pipeline",
                                href=f"/pipelines/{pipeline_id}/run",
                                class_="btn btn-success",
                            ),
                            h.a(
                                "Schedule",
                                href=f"/pipelines/{pipeline_id}/schedule",
                                class_="btn btn-outline-primary",
                            ),
                            h.a(
                                "Visualize DAG",
                                href=f"/pipelines/{pipeline_id}/visualize",
                                class_="btn btn-outline-info",
                            ),
                            h.a(
                                "View Logs",
                                href=f"/pipelines/{pipeline_id}/logs",
                                class_="btn btn-outline-info",
                            ),
                            h.a(
                                "Export Config",
                                href=f"/pipelines/{pipeline_id}/export",
                                class_="btn btn-outline-secondary",
                            ),
                        ],
                    ],
                ],
            ],
        ],
    ]
    return html(base_layout(f"Pipeline: {pipeline['name']}", content))


@app.route("/projects/<project_id:int>/pipelines")
async def project_pipelines(request: Request, project_id: int):
    """Show pipelines for a specific project"""
    projects = load_projects()
    project = next((p for p in projects if p["id"] == project_id), None)

    if not project:
        content = h.div[
            h.h1["Project Not Found"],
            h.p["The requested project could not be found."],
            h.a("Back to Projects", href="/projects", class_="btn btn-primary"),
        ]
        return html(base_layout("Project Not Found", content))

    pipelines = get_project_pipelines(project_id)

    content = h.div[
        h.div(class_="d-flex justify-content-between align-items-center mb-4")[
            h.div[
                h.h1[f"Pipelines - {project['name']}"],
                h.p(class_="text-muted")[project.get("description", "")],
            ],
            h.div[
                h.a(
                    "Back to Project",
                    href=f"/projects/{project_id}",
                    class_="btn btn-outline-secondary me-2",
                ),
                h.a(
                    "New Pipeline",
                    href=f"/projects/{project_id}/pipelines/new",
                    class_="btn btn-success",
                ),
            ],
        ],
        h.div(id="project-pipelines-list", **{"data-ds-id": "project-pipelines-list"})[
            h.div(class_="row")[[pipeline_card(pipeline) for pipeline in pipelines]]
            if pipelines
            else h.div(class_="text-center p-4")[
                h.p(class_="text-muted")["No pipelines found for this project."],
                h.a(
                    class_="btn btn-primary",
                    href=f"/projects/{project_id}/pipelines/new",
                )["Create your first pipeline"],
            ]
        ],
    ]

    return html(base_layout(f"Pipelines - {project['name']}", content))


@app.route("/projects/<project_id:int>/pipelines/new")
async def new_project_pipeline(request: Request, project_id: int):
    """New pipeline form for a specific project"""
    projects = load_projects()
    project = next((p for p in projects if p["id"] == project_id), None)

    if not project:
        content = h.div[
            h.h1["Project Not Found"],
            h.p["The requested project could not be found."],
            h.a("Back to Projects", href="/projects", class_="btn btn-primary"),
        ]
        return html(base_layout("Project Not Found", content))

    content = h.div[
        h.h1[f"Create New Pipeline - {project['name']}"],
        h.form(
            action="/pipelines",
            method="post",
            **{"data-ds-post": "/pipelines", "data-ds-target": "#form-result"},
        )[
            # Hidden field for project ID
            h.input_(type="hidden", name="project_id", value=str(project_id)),
            h.div(class_="mb-3")[
                h.label(class_="form-label")["Project"],
                h.input_(
                    type="text",
                    class_="form-control",
                    value=project["name"],
                    disabled=True,
                ),
            ],
            h.div(class_="mb-3")[
                h.label(for_="name", class_="form-label")["Pipeline Name"],
                h.input_(
                    type="text",
                    id="name",
                    name="name",
                    class_="form-control",
                    required=True,
                    placeholder="e.g., data_processing_pipeline",
                ),
            ],
            h.div(class_="mb-3")[
                h.label(for_="description", class_="form-label")["Description"],
                h.textarea(
                    id="description",
                    name="description",
                    class_="form-control",
                    rows="3",
                    placeholder="Brief description of what this pipeline does...",
                ),
            ],
            h.div(class_="mb-3")[
                h.label(for_="type", class_="form-label")["Pipeline Type"],
                h.select(id="type", name="type", class_="form-select")[
                    h.option(value="batch", selected=True)["Batch Processing"],
                    h.option(value="streaming")["Streaming"],
                    h.option(value="scheduled")["Scheduled"],
                ],
            ],
            h.div(class_="mb-3")[
                h.h5["Configuration Options"],
                h.div(class_="row")[
                    h.div(class_="col-md-6")[
                        h.div(class_="form-check")[
                            h.input_(
                                class_="form-check-input",
                                type="checkbox",
                                id="auto_run",
                                name="auto_run",
                            ),
                            h.label(class_="form-check-label", for_="auto_run")[
                                "Auto-run on schedule"
                            ],
                        ],
                    ],
                    h.div(class_="col-md-6")[
                        h.div(class_="form-check")[
                            h.input_(
                                class_="form-check-input",
                                type="checkbox",
                                id="notifications",
                                name="notifications",
                                checked=True,
                            ),
                            h.label(class_="form-check-label", for_="notifications")[
                                "Enable notifications"
                            ],
                        ],
                    ],
                ],
                h.div(class_="row mt-2")[
                    h.div(class_="col-md-6")[
                        h.label(for_="retry_attempts", class_="form-label")[
                            "Retry Attempts"
                        ],
                        h.input_(
                            type="number",
                            id="retry_attempts",
                            name="retry_attempts",
                            class_="form-control",
                            value="3",
                            min="0",
                            max="10",
                        ),
                    ],
                    h.div(class_="col-md-6")[
                        h.label(for_="timeout", class_="form-label")[
                            "Timeout (seconds)"
                        ],
                        h.input_(
                            type="number",
                            id="timeout",
                            name="timeout",
                            class_="form-control",
                            value="3600",
                            min="1",
                        ),
                    ],
                ],
            ],
            h.div(class_="mb-3")[
                h.button(
                    "Create Pipeline", type="submit", class_="btn btn-primary me-2"
                ),
                h.a(
                    "Cancel",
                    href=f"/projects/{project_id}/pipelines",
                    class_="btn btn-secondary",
                ),
            ],
        ],
        h.div(id="form-result", **{"data-ds-id": "form-result"}),
    ]
    return html(base_layout(f"New Pipeline - {project['name']}", content))


# ================== ADVANCED PIPELINE EXECUTION ROUTES ==================


@app.route("/pipelines/<pipeline_id:int>/run")
async def pipeline_run_form(request: Request, pipeline_id: int):
    """Pipeline execution form with runtime arguments"""
    pipelines = load_pipelines()
    pipeline = next((p for p in pipelines if p["id"] == pipeline_id), None)

    if not pipeline:
        content = h.div[
            h.h1["Pipeline Not Found"],
            h.p["The requested pipeline could not be found."],
            h.a("Back to Pipelines", href="/pipelines", class_="btn btn-primary"),
        ]
        return html(base_layout("Pipeline Not Found", content))

    # Get project information
    projects = load_projects()
    project = next((p for p in projects if p["id"] == pipeline["project_id"]), None)
    project_name = project["name"] if project else "Unknown Project"

    content = h.div[
        h.div(class_="d-flex justify-content-between align-items-center mb-4")[
            h.div[
                h.h1[f"Run Pipeline: {pipeline['name']}"],
                h.p(class_="text-muted")[f"Project: {project_name}"],
            ],
            h.div[
                h.a(
                    "Back to Pipeline",
                    href=f"/pipelines/{pipeline_id}",
                    class_="btn btn-outline-secondary me-2",
                ),
                h.a(
                    "View Logs",
                    href=f"/pipelines/{pipeline_id}/logs",
                    class_="btn btn-outline-info",
                ),
            ],
        ],
        h.div(class_="row")[
            h.div(class_="col-md-8")[
                h.div(class_="card")[
                    h.div(class_="card-body")[
                        h.h5["Runtime Configuration"],
                        h.form(**{
                            "data-ds-post": f"/pipelines/{pipeline_id}/execute",
                            "data-ds-target": "#execution-result",
                        })[
                            h.div(class_="mb-3")[
                                h.label(for_="execution_mode", class_="form-label")[
                                    "Execution Mode"
                                ],
                                h.select(
                                    id="execution_mode",
                                    name="execution_mode",
                                    class_="form-select",
                                )[
                                    h.option(value="immediate", selected=True)[
                                        "Run Immediately"
                                    ],
                                    h.option(value="queue")["Add to Queue"],
                                    h.option(value="schedule")["Schedule for Later"],
                                ],
                            ],
                            h.div(
                                class_="mb-3",
                                id="schedule_options",
                                style="display: none;",
                            )[
                                h.label(for_="run_at", class_="form-label")[
                                    "Schedule Run Time"
                                ],
                                h.input_(
                                    type="datetime-local",
                                    id="run_at",
                                    name="run_at",
                                    class_="form-control",
                                ),
                                h.small(class_="form-text text-muted")[
                                    "Select when to execute the pipeline"
                                ],
                            ],
                            h.div(class_="mb-3")[
                                h.label(for_="runtime_args", class_="form-label")[
                                    "Runtime Arguments (JSON)"
                                ],
                                h.textarea(
                                    id="runtime_args",
                                    name="runtime_args",
                                    class_="form-control",
                                    rows="6",
                                    placeholder='{\n  "input_file": "/path/to/data.csv",\n  "output_dir": "/tmp/output",\n  "batch_size": 1000\n}',
                                ),
                                h.small(class_="form-text text-muted")[
                                    "Enter runtime arguments as JSON. Leave empty for default configuration."
                                ],
                            ],
                            h.div(class_="mb-3")[
                                h.button(
                                    "Execute Pipeline",
                                    type="submit",
                                    class_="btn btn-success me-2",
                                ),
                                h.a(
                                    "Cancel",
                                    href=f"/pipelines/{pipeline_id}",
                                    class_="btn btn-secondary",
                                ),
                            ],
                        ],
                    ],
                ],
            ],
            h.div(class_="col-md-4")[
                h.div(class_="card")[
                    h.div(class_="card-body")[
                        h.h5["Pipeline Information"],
                        h.dl(class_="row")[
                            h.dt(class_="col-sm-6")["Type"],
                            h.dd(class_="col-sm-6")[pipeline.get("type", "batch")],
                            h.dt(class_="col-sm-6")["Status"],
                            h.dd(class_="col-sm-6")[pipeline.get("status", "Unknown")],
                            h.dt(class_="col-sm-6")["Executor"],
                            h.dd(class_="col-sm-6")[
                                pipeline.get("config", {}).get("executor", "local")
                            ],
                            h.dt(class_="col-sm-6")["Timeout"],
                            h.dd(class_="col-sm-6")[
                                f"{pipeline.get('config', {}).get('timeout', 3600)}s"
                            ],
                        ],
                    ],
                ],
                h.div(class_="card mt-3")[
                    h.div(class_="card-body")[
                        h.h5["Recent Runs"],
                        h.dl(class_="row")[
                            h.dt(class_="col-sm-6")["Total"],
                            h.dd(class_="col-sm-6")[
                                str(pipeline.get("metadata", {}).get("run_count", 0))
                            ],
                            h.dt(class_="col-sm-6")["Success"],
                            h.dd(class_="col-sm-6")[
                                str(
                                    pipeline.get("metadata", {}).get("success_count", 0)
                                )
                            ],
                            h.dt(class_="col-sm-6")["Errors"],
                            h.dd(class_="col-sm-6")[
                                str(pipeline.get("metadata", {}).get("error_count", 0))
                            ],
                            h.dt(class_="col-sm-6")["Last Run"],
                            h.dd(class_="col-sm-6")[
                                pipeline.get("metadata", {})
                                .get("last_run", "Never")[:19]
                                .replace("T", " ")
                                if pipeline.get("metadata", {}).get("last_run")
                                != "Never"
                                else "Never"
                            ],
                        ],
                    ],
                ],
            ],
        ],
        h.div(class_="mt-4")[
            h.div(id="execution-result", **{"data-ds-id": "execution-result"})
        ],
        h.script[
            """
            document.getElementById('execution_mode').addEventListener('change', function() {
                const scheduleOptions = document.getElementById('schedule_options');
                if (this.value === 'schedule') {
                    scheduleOptions.style.display = 'block';
                } else {
                    scheduleOptions.style.display = 'none';
                }
            });
        """
        ],
    ]
    return html(base_layout(f"Run Pipeline: {pipeline['name']}", content))


@app.route("/pipelines/<pipeline_id:int>/execute", methods=["POST"])
async def execute_pipeline(request: Request, pipeline_id: int):
    """Execute pipeline with runtime arguments"""
    try:
        execution_mode = request.form.get("execution_mode", "immediate")
        runtime_args_str = request.form.get("runtime_args", "")
        run_at = request.form.get("run_at")

        # Parse runtime arguments if provided
        runtime_args = {}
        if runtime_args_str.strip():
            try:
                import json

                runtime_args = json.loads(runtime_args_str)
            except json.JSONDecodeError as e:
                await emit_to_all(
                    "execution-result",
                    {
                        "content": str(
                            h.div(
                                f"Invalid JSON in runtime arguments: {str(e)}",
                                class_="alert alert-danger",
                            )
                        )
                    },
                )
                return json({
                    "status": "error",
                    "message": "Invalid JSON in runtime arguments",
                })

        if execution_mode == "immediate":
            # Execute immediately
            result = execute_pipeline_with_flowerpower(pipeline_id, runtime_args)

            if result["status"] == "success":
                success_content = h.div[
                    h.div(
                        f"Pipeline executed successfully! Result: {result.get('message', 'Completed')}",
                        class_="alert alert-success",
                    ),
                    h.div(class_="mt-3")[
                        h.h6["Execution Details:"],
                        h.pre(
                            style="background-color: #f8f9fa; padding: 10px; border-radius: 5px;"
                        )[str(result.get("result", "No detailed result available"))],
                    ],
                ]
            else:
                success_content = h.div(
                    f"Pipeline execution failed: {result.get('message', 'Unknown error')}",
                    class_="alert alert-danger",
                )

        elif execution_mode == "queue":
            # Add to queue
            result = queue_pipeline_execution(pipeline_id, runtime_args, run_at)

            if result["status"] == "success":
                success_content = h.div(
                    f"Pipeline queued successfully! Job ID: {result.get('job_id')}",
                    class_="alert alert-success",
                )
            else:
                success_content = h.div(
                    f"Failed to queue pipeline: {result.get('message', 'Unknown error')}",
                    class_="alert alert-danger",
                )

        elif execution_mode == "schedule":
            # Schedule for later (convert datetime-local to proper scheduling)
            if not run_at:
                await emit_to_all(
                    "execution-result",
                    {
                        "content": str(
                            h.div(
                                "Schedule time is required for scheduled execution",
                                class_="alert alert-danger",
                            )
                        )
                    },
                )
                return json({"status": "error", "message": "Schedule time required"})

            result = queue_pipeline_execution(pipeline_id, runtime_args, run_at)

            if result["status"] == "success":
                success_content = h.div(
                    f"Pipeline scheduled successfully! Job ID: {result.get('job_id')} will run at {run_at}",
                    class_="alert alert-success",
                )
            else:
                success_content = h.div(
                    f"Failed to schedule pipeline: {result.get('message', 'Unknown error')}",
                    class_="alert alert-danger",
                )

        await emit_to_all("execution-result", {"content": str(success_content)})

        return json({"status": "success", "message": "Pipeline execution initiated"})

    except Exception as e:
        error_content = h.div(
            f"Error executing pipeline: {str(e)}", class_="alert alert-danger"
        )
        await emit_to_all("execution-result", {"content": str(error_content)})
        return json({"status": "error", "message": str(e)})


@app.route("/pipelines/<pipeline_id:int>/schedule")
async def pipeline_schedule_form(request: Request, pipeline_id: int):
    """Pipeline scheduling form with cron expressions"""
    pipelines = load_pipelines()
    pipeline = next((p for p in pipelines if p["id"] == pipeline_id), None)

    if not pipeline:
        content = h.div[
            h.h1["Pipeline Not Found"],
            h.p["The requested pipeline could not be found."],
            h.a("Back to Pipelines", href="/pipelines", class_="btn btn-primary"),
        ]
        return html(base_layout("Pipeline Not Found", content))

    # Get project information
    projects = load_projects()
    project = next((p for p in projects if p["id"] == pipeline["project_id"]), None)
    project_name = project["name"] if project else "Unknown Project"

    # Get current schedule if any
    current_schedule = pipeline.get("config", {}).get("schedule", {})
    is_scheduled = current_schedule.get("enabled", False)
    current_cron = current_schedule.get("cron", "")

    content = h.div[
        h.div(class_="d-flex justify-content-between align-items-center mb-4")[
            h.div[
                h.h1[f"Schedule Pipeline: {pipeline['name']}"],
                h.p(class_="text-muted")[f"Project: {project_name}"],
            ],
            h.div[
                h.a(
                    "Back to Pipeline",
                    href=f"/pipelines/{pipeline_id}",
                    class_="btn btn-outline-secondary me-2",
                ),
                h.a(
                    "Run Now",
                    href=f"/pipelines/{pipeline_id}/run",
                    class_="btn btn-success",
                ),
            ],
        ],
        h.div(class_="row")[
            h.div(class_="col-md-8")[
                h.div(class_="card")[
                    h.div(class_="card-body")[
                        h.h5["Schedule Configuration"],
                        (
                            h.div(class_="alert alert-info")[
                                f"Current status: {'Scheduled' if is_scheduled else 'Not scheduled'}",
                                (h.br() if is_scheduled else ""),
                                (
                                    f"Cron expression: {current_cron}"
                                    if is_scheduled and current_cron
                                    else ""
                                ),
                            ]
                        ),
                        h.form(**{
                            "data-ds-post": f"/pipelines/{pipeline_id}/schedule",
                            "data-ds-target": "#schedule-result",
                        })[
                            h.div(class_="mb-3")[
                                h.label(for_="schedule_action", class_="form-label")[
                                    "Action"
                                ],
                                h.select(
                                    id="schedule_action",
                                    name="schedule_action",
                                    class_="form-select",
                                )[
                                    h.option(value="create")["Create/Update Schedule"],
                                    h.option(value="disable")["Disable Schedule"],
                                    h.option(value="delete")["Delete Schedule"],
                                ],
                            ],
                            h.div(class_="mb-3", id="cron_config")[
                                h.label(for_="cron_expression", class_="form-label")[
                                    "Cron Expression"
                                ],
                                h.input_(
                                    type="text",
                                    id="cron_expression",
                                    name="cron_expression",
                                    class_="form-control",
                                    value=current_cron,
                                    placeholder="0 */6 * * *",
                                ),
                                h.small(class_="form-text text-muted")[
                                    "Format: minute hour day month day-of-week"
                                ],
                            ],
                            h.div(class_="mb-3", id="preset_schedules")[
                                h.label(class_="form-label")["Common Schedules"],
                                h.div(class_="btn-group-vertical d-grid gap-2")[
                                    h.button(
                                        "Every minute",
                                        type="button",
                                        class_="btn btn-outline-secondary btn-sm",
                                        onclick="document.getElementById('cron_expression').value = '* * * * *'",
                                    ),
                                    h.button(
                                        "Every hour",
                                        type="button",
                                        class_="btn btn-outline-secondary btn-sm",
                                        onclick="document.getElementById('cron_expression').value = '0 * * * *'",
                                    ),
                                    h.button(
                                        "Every 6 hours",
                                        type="button",
                                        class_="btn btn-outline-secondary btn-sm",
                                        onclick="document.getElementById('cron_expression').value = '0 */6 * * *'",
                                    ),
                                    h.button(
                                        "Daily at midnight",
                                        type="button",
                                        class_="btn btn-outline-secondary btn-sm",
                                        onclick="document.getElementById('cron_expression').value = '0 0 * * *'",
                                    ),
                                    h.button(
                                        "Weekly (Sundays)",
                                        type="button",
                                        class_="btn btn-outline-secondary btn-sm",
                                        onclick="document.getElementById('cron_expression').value = '0 0 * * 0'",
                                    ),
                                ],
                            ],
                            h.div(class_="mb-3")[
                                h.label(for_="runtime_args", class_="form-label")[
                                    "Default Runtime Arguments (JSON)"
                                ],
                                h.textarea(
                                    id="runtime_args",
                                    name="runtime_args",
                                    class_="form-control",
                                    rows="4",
                                    placeholder='{\n  "batch_size": 1000\n}',
                                ),
                                h.small(class_="form-text text-muted")[
                                    "These arguments will be used for all scheduled executions."
                                ],
                            ],
                            h.div(class_="mb-3")[
                                h.button(
                                    "Update Schedule",
                                    type="submit",
                                    class_="btn btn-primary me-2",
                                ),
                                h.a(
                                    "Cancel",
                                    href=f"/pipelines/{pipeline_id}",
                                    class_="btn btn-secondary",
                                ),
                            ],
                        ],
                    ],
                ],
            ],
            h.div(class_="col-md-4")[
                h.div(class_="card")[
                    h.div(class_="card-body")[
                        h.h5["Cron Expression Guide"],
                        h.table(class_="table table-sm")[
                            h.thead[
                                h.tr[
                                    h.th["Field"],
                                    h.th["Values"],
                                ]
                            ],
                            h.tbody[
                                h.tr[h.td["Minute"], h.td["0-59"]],
                                h.tr[h.td["Hour"], h.td["0-23"]],
                                h.tr[h.td["Day"], h.td["1-31"]],
                                h.tr[h.td["Month"], h.td["1-12"]],
                                h.tr[h.td["Weekday"], h.td["0-7 (0=Sun)"]],
                            ],
                        ],
                        h.small[
                            h.strong["Examples:"],
                            h.br(),
                            "*/15 * * * * - Every 15 minutes",
                            h.br(),
                            "0 9-17 * * 1-5 - Business hours",
                            h.br(),
                            "0 2 * * 0 - Sundays at 2 AM",
                            h.br(),
                        ],
                    ],
                ],
            ],
        ],
        h.div(class_="mt-4")[
            h.div(id="schedule-result", **{"data-ds-id": "schedule-result"})
        ],
        h.script[
            """
            document.getElementById('schedule_action').addEventListener('change', function() {
                const cronConfig = document.getElementById('cron_config');
                const presetSchedules = document.getElementById('preset_schedules');
                if (this.value === 'create') {
                    cronConfig.style.display = 'block';
                    presetSchedules.style.display = 'block';
                } else {
                    cronConfig.style.display = 'none';
                    presetSchedules.style.display = 'none';
                }
            });
        """
        ],
    ]
    return html(base_layout(f"Schedule Pipeline: {pipeline['name']}", content))


@app.route("/pipelines/<pipeline_id:int>/schedule", methods=["POST"])
async def update_pipeline_schedule(request: Request, pipeline_id: int):
    """Update pipeline schedule configuration"""
    try:
        schedule_action = request.form.get("schedule_action", "create")
        cron_expression = request.form.get("cron_expression", "")
        runtime_args_str = request.form.get("runtime_args", "")

        # Parse runtime arguments if provided
        runtime_args = {}
        if runtime_args_str.strip():
            try:
                import json

                runtime_args = json.loads(runtime_args_str)
            except json.JSONDecodeError as e:
                await emit_to_all(
                    "schedule-result",
                    {
                        "content": str(
                            h.div(
                                f"Invalid JSON in runtime arguments: {str(e)}",
                                class_="alert alert-danger",
                            )
                        )
                    },
                )
                return json({
                    "status": "error",
                    "message": "Invalid JSON in runtime arguments",
                })

        pipelines = load_pipelines()
        pipeline_idx = None
        for i, p in enumerate(pipelines):
            if p["id"] == pipeline_id:
                pipeline_idx = i
                break

        if pipeline_idx is None:
            await emit_to_all(
                "schedule-result",
                {
                    "content": str(
                        h.div("Pipeline not found", class_="alert alert-danger")
                    )
                },
            )
            return json({"status": "error", "message": "Pipeline not found"})

        if schedule_action == "create":
            if not cron_expression.strip():
                await emit_to_all(
                    "schedule-result",
                    {
                        "content": str(
                            h.div(
                                "Cron expression is required",
                                class_="alert alert-danger",
                            )
                        )
                    },
                )
                return json({"status": "error", "message": "Cron expression required"})

            # Create/update schedule using FlowerPower
            result = schedule_pipeline_execution(
                pipeline_id, cron_expression, runtime_args
            )

            if result["status"] == "success":
                success_content = h.div[
                    h.div(
                        f"Pipeline scheduled successfully! Schedule ID: {result.get('schedule_id')}",
                        class_="alert alert-success",
                    ),
                    h.div(class_="mt-3")[
                        h.h6["Schedule Details:"],
                        h.ul[
                            h.li[f"Cron Expression: {cron_expression}"],
                            h.li[
                                f"Runtime Arguments: {runtime_args if runtime_args else 'None'}"
                            ],
                            h.li[f"Status: Active"],
                        ],
                    ],
                ]
            else:
                success_content = h.div(
                    f"Failed to create schedule: {result.get('message', 'Unknown error')}",
                    class_="alert alert-danger",
                )

        elif schedule_action == "disable":
            # Disable schedule
            pipelines[pipeline_idx]["config"]["schedule"]["enabled"] = False
            pipelines[pipeline_idx]["status"] = "Inactive"
            save_pipelines(pipelines)

            success_content = h.div(
                "Pipeline schedule disabled successfully", class_="alert alert-success"
            )

        elif schedule_action == "delete":
            # Delete schedule
            pipelines[pipeline_idx]["config"]["schedule"]["enabled"] = False
            pipelines[pipeline_idx]["config"]["schedule"]["cron"] = None
            pipelines[pipeline_idx]["status"] = "Inactive"
            save_pipelines(pipelines)

            success_content = h.div(
                "Pipeline schedule deleted successfully", class_="alert alert-success"
            )

        await emit_to_all("schedule-result", {"content": str(success_content)})

        return json({"status": "success", "message": "Schedule updated"})

    except Exception as e:
        error_content = h.div(
            f"Error updating schedule: {str(e)}", class_="alert alert-danger"
        )
        await emit_to_all("schedule-result", {"content": str(error_content)})
        return json({"status": "error", "message": str(e)})


# ================== JOB QUEUE MONITORING ROUTES ==================


@app.route("/jobs")
async def job_queue_monitor(request: Request):
    """
    Job queue monitoring and management interface.

    Displays job status cards, worker and queue management controls, and lists of recent jobs and active schedules.
    Includes auto-refresh logic for real-time updates.
    """
    content = h.div[
        h.h1["Job Queue Monitor"],
        h.p(class_="lead")["Monitor and manage pipeline execution jobs and schedules."],
        # Status Cards
        h.div(class_="row mb-4")[
            h.div(class_="col-md-3")[
                h.div(class_="card")[
                    h.div(class_="card-body text-center")[
                        h.h3(class_="card-title text-primary", id="active-jobs")["--"],
                        h.p(class_="card-text")["Active Jobs"],
                    ],
                ],
            ],
            h.div(class_="col-md-3")[
                h.div(class_="card")[
                    h.div(class_="card-body text-center")[
                        h.h3(class_="card-title text-info", id="scheduled-jobs")["--"],
                        h.p(class_="card-text")["Scheduled Jobs"],
                    ],
                ],
            ],
            h.div(class_="col-md-3")[
                h.div(class_="card")[
                    h.div(class_="card-body text-center")[
                        h.h3(class_="card-title text-success", id="completed-jobs")[
                            "--"
                        ],
                        h.p(class_="card-text")["Completed Jobs"],
                    ],
                ],
            ],
            h.div(class_="col-md-3")[
                h.div(class_="card")[
                    h.div(class_="card-body text-center")[
                        h.h3(class_="card-title text-danger", id="failed-jobs")["--"],
                        h.p(class_="card-text")["Failed Jobs"],
                    ],
                ],
            ],
        ],
        # Job Management Controls
        h.div(class_="row mb-4")[
            h.div(class_="col-md-6")[
                h.div(class_="card")[
                    h.div(class_="card-header")[h.h5["Worker Management"]],
                    h.div(class_="card-body")[
                        h.div(class_="mb-3")[
                            h.span(
                                class_="badge bg-secondary me-2", id="worker-status"
                            )["Unknown"],
                            h.span["Worker Status"],
                        ],
                        h.div(class_="d-grid gap-2")[
                            h.button(
                                "Start Workers",
                                class_="btn btn-success",
                                **{
                                    "data-ds-post": "/jobs/workers/start",
                                    "data-ds-target": "#worker-result",
                                },
                            ),
                            h.button(
                                "Stop Workers",
                                class_="btn btn-danger",
                                **{
                                    "data-ds-post": "/jobs/workers/stop",
                                    "data-ds-target": "#worker-result",
                                },
                            ),
                        ],
                        h.div(id="worker-result", class_="mt-3"),
                    ],
                ],
            ],
            h.div(class_="col-md-6")[
                h.div(class_="card")[
                    h.div(class_="card-header")[h.h5["Queue Management"]],
                    h.div(class_="card-body")[
                        h.div(class_="d-grid gap-2")[
                            h.button(
                                "Refresh Status",
                                class_="btn btn-outline-primary",
                                **{
                                    "data-ds-post": "/jobs/refresh",
                                    "data-ds-target": "#jobs-list",
                                },
                            ),
                            h.button(
                                "Clear Completed",
                                class_="btn btn-outline-warning",
                                **{
                                    "data-ds-post": "/jobs/clear-completed",
                                    "data-ds-target": "#queue-result",
                                },
                            ),
                            h.button(
                                "Pause All Schedules",
                                class_="btn btn-outline-secondary",
                                **{
                                    "data-ds-post": "/jobs/schedules/pause",
                                    "data-ds-target": "#queue-result",
                                },
                            ),
                        ],
                        h.div(id="queue-result", class_="mt-3"),
                    ],
                ],
            ],
        ],
        # Jobs and Schedules List
        h.div(class_="row")[
            h.div(class_="col-md-6")[
                h.div(class_="card")[
                    h.div(class_="card-header")[h.h5["Recent Jobs"]],
                    h.div(class_="card-body")[
                        h.div(id="jobs-list", **{"data-ds-id": "jobs-list"})[
                            h.div(class_="text-center text-muted p-3")[
                                "Loading job information..."
                            ]
                        ]
                    ],
                ],
            ],
            h.div(class_="col-md-6")[
                h.div(class_="card")[
                    h.div(class_="card-header")[h.h5["Active Schedules"]],
                    h.div(class_="card-body")[
                        h.div(id="schedules-list", **{"data-ds-id": "schedules-list"})[
                            h.div(class_="text-center text-muted p-3")[
                                "Loading schedule information..."
                            ]
                        ]
                    ],
                ],
            ],
        ],
        # Auto-refresh script
        h.script[
            """
            // Auto-refresh every 10 seconds
            setInterval(function() {
                fetch('/jobs/status')
                    .then(response => response.json())
                    .then(data => {
                        if (data.status === 'success') {
                            document.getElementById('active-jobs').textContent = data.active_jobs || 0;
                            document.getElementById('scheduled-jobs').textContent = data.scheduled_jobs || 0;
                            document.getElementById('completed-jobs').textContent = data.completed_jobs || 0;
                            document.getElementById('failed-jobs').textContent = data.failed_jobs || 0;
                            document.getElementById('worker-status').textContent = data.worker_status || 'Unknown';
                            document.getElementById('worker-status').className =
                                'badge me-2 ' + (data.worker_status === 'Running' ? 'bg-success' : 'bg-secondary');
                        }
                    })
                    .catch(error => console.error('Error fetching job status:', error));
            }, 10000);
            
            // Initial load
            window.addEventListener('load', function() {
                setTimeout(function() {
                    fetch('/jobs/status')
                        .then(response => response.json())
                        .then(data => {
                            if (data.status === 'success') {
                                document.getElementById('active-jobs').textContent = data.active_jobs || 0;
                                document.getElementById('scheduled-jobs').textContent = data.scheduled_jobs || 0;
                                document.getElementById('completed-jobs').textContent = data.completed_jobs || 0;
                                document.getElementById('failed-jobs').textContent = data.failed_jobs || 0;
                                document.getElementById('worker-status').textContent = data.worker_status || 'Unknown';
                                document.getElementById('worker-status').className =
                                    'badge me-2 ' + (data.worker_status === 'Running' ? 'bg-success' : 'bg-secondary');
                            }
                        });
                }, 1000);
            });
        """
        ],
    ]

    return html(base_layout("Job Queue Monitor", content))


@app.route("/jobs/status")
async def job_queue_status(request: Request):
    """Get current job queue status"""
    try:
        if not FLOWERPOWER_AVAILABLE:
            return json({
                "status": "success",
                "active_jobs": 0,
                "scheduled_jobs": 0,
                "completed_jobs": 0,
                "failed_jobs": 0,
                "worker_status": "Not Available",
            })

        # Mock data based on pipeline metadata for now
        pipelines = load_pipelines()
        active_jobs = len([p for p in pipelines if p.get("status") == "Running"])
        scheduled_jobs = len([
            p
            for p in pipelines
            if p.get("config", {}).get("schedule", {}).get("enabled")
        ])
        completed_jobs = sum(
            p.get("metadata", {}).get("success_count", 0) for p in pipelines
        )
        failed_jobs = sum(
            p.get("metadata", {}).get("error_count", 0) for p in pipelines
        )

        return json({
            "status": "success",
            "active_jobs": active_jobs,
            "scheduled_jobs": scheduled_jobs,
            "completed_jobs": completed_jobs,
            "failed_jobs": failed_jobs,
            "worker_status": "Unknown",  # Would check actual worker status
        })

    except Exception as e:
        return json({"status": "error", "message": str(e)})


@app.route("/jobs/workers/start", methods=["POST"])
async def start_workers(request: Request):
    """Start job queue workers"""
    try:
        if not FLOWERPOWER_AVAILABLE:
            await emit_to_all(
                "worker-result",
                {
                    "content": str(
                        h.div(
                            "FlowerPower not available - cannot start workers",
                            class_="alert alert-warning",
                        )
                    )
                },
            )
            return json({"status": "error", "message": "FlowerPower not available"})

        # In a real implementation, you would start the actual worker processes
        success_content = h.div(
            "Workers started successfully! (Mock implementation)",
            class_="alert alert-success",
        )

        await emit_to_all("worker-result", {"content": str(success_content)})

        return json({"status": "success", "message": "Workers started"})

    except Exception as e:
        error_content = h.div(
            f"Error starting workers: {str(e)}", class_="alert alert-danger"
        )
        await emit_to_all("worker-result", {"content": str(error_content)})
        return json({"status": "error", "message": str(e)})


@app.route("/jobs/workers/stop", methods=["POST"])
async def stop_workers(request: Request):
    """Stop job queue workers"""
    try:
        if not FLOWERPOWER_AVAILABLE:
            await emit_to_all(
                "worker-result",
                {
                    "content": str(
                        h.div(
                            "FlowerPower not available - cannot stop workers",
                            class_="alert alert-warning",
                        )
                    )
                },
            )
            return json({"status": "error", "message": "FlowerPower not available"})

        # In a real implementation, you would stop the actual worker processes
        success_content = h.div(
            "Workers stopped successfully! (Mock implementation)",
            class_="alert alert-info",
        )

        await emit_to_all("worker-result", {"content": str(success_content)})

        return json({"status": "success", "message": "Workers stopped"})

    except Exception as e:
        error_content = h.div(
            f"Error stopping workers: {str(e)}", class_="alert alert-danger"
        )
        await emit_to_all("worker-result", {"content": str(error_content)})
        return json({"status": "error", "message": str(e)})


# ================== PIPELINE VISUALIZATION ROUTES ==================


@app.route("/pipelines/<pipeline_id:int>/visualize")
async def pipeline_visualize(request: Request, pipeline_id: int):
    """Pipeline DAG visualization page"""
    pipelines = load_pipelines()
    pipeline = next((p for p in pipelines if p["id"] == pipeline_id), None)

    if not pipeline:
        content = h.div[
            h.h1["Pipeline Not Found"],
            h.p["The requested pipeline could not be found."],
            h.a("Back to Pipelines", href="/pipelines", class_="btn btn-primary"),
        ]
        return html(base_layout("Pipeline Not Found", content))

    # Get project information
    projects = load_projects()
    project = next((p for p in projects if p["id"] == pipeline["project_id"]), None)
    project_name = project["name"] if project else "Unknown Project"

    content = h.div[
        h.div(class_="d-flex justify-content-between align-items-center mb-4")[
            h.div[
                h.h1[f"Pipeline DAG: {pipeline['name']}"],
                h.p(class_="text-muted")[f"Project: {project_name}"],
            ],
            h.div[
                h.a(
                    "Back to Pipeline",
                    href=f"/pipelines/{pipeline_id}",
                    class_="btn btn-outline-secondary me-2",
                ),
                h.a(
                    "Run Pipeline",
                    href=f"/pipelines/{pipeline_id}/run",
                    class_="btn btn-success",
                ),
            ],
        ],
        h.div(class_="row")[
            h.div(class_="col-md-9")[
                h.div(class_="card")[
                    h.div(
                        class_="card-header d-flex justify-content-between align-items-center"
                    )[
                        h.h5(class_="mb-0")["Pipeline Directed Acyclic Graph (DAG)"],
                        h.div[
                            h.button(
                                "Refresh",
                                class_="btn btn-outline-primary btn-sm me-2",
                                **{
                                    "data-ds-post": f"/pipelines/{pipeline_id}/dag-data",
                                    "data-ds-target": "#dag-container",
                                },
                            ),
                            h.button(
                                "Fit to View",
                                class_="btn btn-outline-secondary btn-sm",
                                id="fit-view-btn",
                            ),
                        ],
                    ],
                    h.div(class_="card-body p-0")[
                        h.div(
                            id="dag-container",
                            style="height: 600px; width: 100%; border: 1px solid #dee2e6;",
                            **{"data-ds-id": "dag-container"},
                        )[
                            h.div(
                                class_="d-flex justify-content-center align-items-center h-100"
                            )[
                                h.div(class_="text-center")[
                                    h.div(
                                        class_="spinner-border text-primary",
                                        role="status",
                                    )[h.span(class_="visually-hidden")["Loading..."]],
                                    h.p(class_="mt-2 text-muted")[
                                        "Loading pipeline DAG..."
                                    ],
                                ]
                            ]
                        ]
                    ],
                ],
            ],
            h.div(class_="col-md-3")[
                h.div(class_="card")[
                    h.div(class_="card-header")[h.h5["Pipeline Info"]],
                    h.div(class_="card-body")[
                        h.dl(class_="row")[
                            h.dt(class_="col-sm-5")["Name"],
                            h.dd(class_="col-sm-7")[pipeline["name"]],
                            h.dt(class_="col-sm-5")["Type"],
                            h.dd(class_="col-sm-7")[pipeline.get("type", "batch")],
                            h.dt(class_="col-sm-5")["Status"],
                            h.dd(class_="col-sm-7")[pipeline.get("status", "Unknown")],
                        ],
                    ],
                ],
                h.div(class_="card mt-3")[
                    h.div(class_="card-header")[h.h5["Graph Controls"]],
                    h.div(class_="card-body")[
                        h.div(class_="mb-3")[
                            h.label(class_="form-label")["Layout"],
                            h.select(class_="form-select", id="layout-select")[
                                h.option(value="dagre", selected=True)[
                                    "Hierarchical (Dagre)"
                                ],
                                h.option(value="circle")["Circle"],
                                h.option(value="grid")["Grid"],
                                h.option(value="random")["Random"],
                            ],
                        ],
                        h.div(class_="mb-3")[
                            h.div(class_="form-check")[
                                h.input_(
                                    class_="form-check-input",
                                    type="checkbox",
                                    id="show-labels",
                                    checked=True,
                                ),
                                h.label(class_="form-check-label", for_="show-labels")[
                                    "Show Labels"
                                ],
                            ],
                        ],
                        h.div(class_="mb-3")[
                            h.div(class_="form-check")[
                                h.input_(
                                    class_="form-check-input",
                                    type="checkbox",
                                    id="animate-layout",
                                ),
                                h.label(
                                    class_="form-check-label", for_="animate-layout"
                                )["Animate Layout"],
                            ],
                        ],
                    ],
                ],
                h.div(class_="card mt-3")[
                    h.div(class_="card-header")[h.h5["Node Info"]],
                    h.div(class_="card-body")[
                        h.div(id="node-info")[
                            h.p(class_="text-muted")["Click on a node to see details"]
                        ]
                    ],
                ],
            ],
        ],
        # Include Cytoscape.js for graph visualization
        h.script(src="https://unpkg.com/cytoscape@3.28.1/dist/cytoscape.min.js"),
        h.script(src="https://unpkg.com/cytoscape-dagre@2.5.0/cytoscape-dagre.js"),
        h.script[
            f"""
            let cy;
            
            // Initialize Cytoscape when DAG data is loaded
            function initializeCytoscape(dagData) {{
                // Clear existing graph
                if (cy) {{
                    cy.destroy();
                }}
                
                const container = document.getElementById('dag-container');
                
                // Transform nodes and edges for Cytoscape format
                const elements = [];
                
                // Add nodes
                dagData.nodes.forEach(node => {{
                    elements.push({{
                        data: {{
                            id: node.id,
                            label: node.label || node.id,
                            type: node.type || 'function'
                        }}
                    }});
                }});
                
                // Add edges
                dagData.edges.forEach(edge => {{
                    elements.push({{
                        data: {{
                            id: edge.id,
                            source: edge.source,
                            target: edge.target
                        }}
                    }});
                }});
                
                // Create Cytoscape instance
                cy = cytoscape({{
                    container: container,
                    elements: elements,
                    style: [
                        {{
                            selector: 'node',
                            style: {{
                                'background-color': '#0d6efd',
                                'label': 'data(label)',
                                'text-valign': 'center',
                                'text-halign': 'center',
                                'color': 'white',
                                'text-outline-width': 2,
                                'text-outline-color': '#0d6efd',
                                'width': 80,
                                'height': 40,
                                'shape': 'roundrectangle',
                                'font-size': '12px'
                            }}
                        }},
                        {{
                            selector: 'node[type="input"]',
                            style: {{
                                'background-color': '#198754',
                                'text-outline-color': '#198754'
                            }}
                        }},
                        {{
                            selector: 'node[type="output"]',
                            style: {{
                                'background-color': '#dc3545',
                                'text-outline-color': '#dc3545'
                            }}
                        }},
                        {{
                            selector: 'edge',
                            style: {{
                                'width': 2,
                                'line-color': '#6c757d',
                                'target-arrow-color': '#6c757d',
                                'target-arrow-shape': 'triangle',
                                'curve-style': 'bezier'
                            }}
                        }},
                        {{
                            selector: 'node:selected',
                            style: {{
                                'border-width': 3,
                                'border-color': '#ffc107'
                            }}
                        }}
                    ],
                    layout: {{
                        name: 'dagre',
                        rankDir: 'TB',
                        spacingFactor: 1.5
                    }}
                }});
                
                // Handle node clicks
                cy.on('tap', 'node', function(evt) {{
                    const node = evt.target;
                    const nodeData = node.data();
                    
                    document.getElementById('node-info').innerHTML = `
                        <h6>${{nodeData.label}}</h6>
                        <p><strong>ID:</strong> ${{nodeData.id}}</p>
                        <p><strong>Type:</strong> ${{nodeData.type}}</p>
                        <p><strong>Degree:</strong> ${{node.degree()}}</p>
                    `;
                }});
                
                // Handle layout controls
                document.getElementById('layout-select').addEventListener('change', function() {{
                    const layout = cy.layout({{
                        name: this.value,
                        rankDir: 'TB',
                        spacingFactor: 1.5
                    }});
                    layout.run();
                }});
                
                document.getElementById('show-labels').addEventListener('change', function() {{
                    if (this.checked) {{
                        cy.style().selector('node').style('label', 'data(label)').update();
                    }} else {{
                        cy.style().selector('node').style('label', '').update();
                    }}
                }});
                
                document.getElementById('fit-view-btn').addEventListener('click', function() {{
                    cy.fit();
                }});
            }}
            
            // Load DAG data on page load
            window.addEventListener('load', function() {{
                setTimeout(function() {{
                    fetch('/pipelines/{pipeline_id}/dag-data')
                        .then(response => response.json())
                        .then(data => {{
                            if (data.status === 'success') {{
                                initializeCytoscape(data.dag);
                            }} else {{
                                document.getElementById('dag-container').innerHTML =
                                    '<div class="d-flex justify-content-center align-items-center h-100">' +
                                    '<div class="alert alert-danger">Error loading DAG: ' + data.message + '</div>' +
                                    '</div>';
                            }}
                        }})
                        .catch(error => {{
                            console.error('Error loading DAG:', error);
                            document.getElementById('dag-container').innerHTML =
                                '<div class="d-flex justify-content-center align-items-center h-100">' +
                                '<div class="alert alert-danger">Error loading DAG visualization</div>' +
                                '</div>';
                        }});
                }}, 1000);
            }});
        """
        ],
    ]

    return html(base_layout(f"Visualize: {pipeline['name']}", content))


@app.route("/pipelines/<pipeline_id:int>/dag-data")
async def pipeline_dag_data(request: Request, pipeline_id: int):
    """API endpoint to get pipeline DAG data"""
    try:
        dag_data = get_pipeline_dag_data(pipeline_id)

        if dag_data["status"] == "success":
            # Update the visualization container with success
            dag_json = json_module.dumps(dag_data["dag"])
            await emit_to_all(
                "dag-container",
                {
                    "content": f"""
                <div class="d-flex justify-content-center align-items-center h-100">
                    <div class="text-center text-success">
                        <i class="fas fa-check-circle fa-3x"></i>
                        <p class="mt-2">DAG loaded successfully</p>
                    </div>
                </div>
                <script>
                    if (typeof initializeCytoscape === 'function') {{
                        initializeCytoscape({dag_json});
                    }}
                </script>
                """
                },
            )
        else:
            # Update with error message
            await emit_to_all(
                "dag-container",
                {
                    "content": f"""
                <div class="d-flex justify-content-center align-items-center h-100">
                    <div class="alert alert-danger">
                        Error loading DAG: {dag_data.get("message", "Unknown error")}
                    </div>
                </div>
                """
                },
            )

        return json(dag_data)

    except Exception as e:
        error_response = {"status": "error", "message": str(e)}
        await emit_to_all(
            "dag-container",
            {
                "content": f"""
            <div class="d-flex justify-content-center align-items-center h-100">
                <div class="alert alert-danger">
                    Error: {str(e)}
                </div>
            </div>
            """
            },
        )
        return json(error_response)


@app.route("/datastar/stream")
async def datastar_stream(request: Request):
    """SSE endpoint for Datastar"""
    generator = ServerSentEventGenerator()
    sse_connections.add(generator)

    try:
        return await datastar_respond(generator, headers=SSE_HEADERS)
    finally:
        sse_connections.discard(generator)


if __name__ == "__main__":
    # Create data file if it doesn't exist
    if not os.path.exists(PROJECTS_DATA_FILE):
        # Initialize with empty data structure
        initial_data = {
            "projects": [],
            "pipelines": [],
            "last_updated": datetime.now().isoformat(),
        }
        save_data(initial_data)

    app.run(host="0.0.0.0", port=8000, debug=True)
