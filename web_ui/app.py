"""
FlowerPower Web Application
Main Sanic application with htpy templates and Datastar integration
"""

from sanic import Sanic, Request
from sanic.response import html, json
from sanic_ext import Extend
from datastar_py.sanic import ServerSentEventGenerator, datastar_respond, SSE_HEADERS
import htpy as h
import asyncio
from typing import List, Dict, Any
import json as json_module
import os
from datetime import datetime
import uuid

# Initialize Sanic app
app = Sanic("FlowerPowerWeb")
app.config.CORS_ORIGINS = "*"
Extend(app)

# Global SSE connections storage
sse_connections = set()

# Data storage file path
PROJECTS_DATA_FILE = os.path.join(os.path.dirname(__file__), "projects_data.json")

def load_projects():
    """Load projects from JSON file"""
    if os.path.\1[PROJECTS_DATA_FILE):
        try:
            with open(PROJECTS_DATA_FILE, 'r') as f:
                data = json_module.load(f)
                return data.get('projects', [])
        except Exception as e:
            print(f"Error loading projects: {e}")
    return []

def save_projects(projects):
    """Save projects to JSON file"""
    try:
        data = {
            'projects': projects,
            'last_updated': datetime.now().isoformat()
        }
        with open(PROJECTS_DATA_FILE, 'w') as f:
            json_module.dump(data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving projects: {e}")
        return False

def get_next_project_id(projects):
    """Get the next available project ID"""
    if not projects:
        return 1
    return max(p.get('id', 0) for p in projects) + 1

async def emit_to_all(target_id: str, data: dict):
    """Emit data to all connected SSE clients"""
    if not sse_connections:
        return
    
    # Create the datastar event
    event_data = {
        "type": "patch",
        "data": {
            "selector": f"#{target_id}",
            "merge": "morph",
            "content": data.get("content", "")
        }
    }
    
    # Send to all connections
    disconnected = set()
    for connection in sse_connections:
        try:
            await connection.send(f"data: {json.dumps(event_data)}\n\n")
        except Exception:
            disconnected.add(connection)
    
    # Remove disconnected clients
    sse_connections.difference_update(disconnected)

# Initialize projects data from file or with default samples
PROJECTS = load_projects()

# Initialize with sample data if no projects exist
if not PROJECTS:
    PROJECTS = [
        {
            "id": 1,
            "name": "Sample Data Pipeline",
            "description": "A sample pipeline for processing CSV data",
            "status": "Active",
            "created_at": "2025-01-20T10:00:00Z",
            "updated_at": "2025-01-20T10:00:00Z",
            "config": {
                "environment": "development",
                "auto_run": True,
                "notifications": True,
                "retry_attempts": 3
            }
        },
        {
            "id": 2,
            "name": "MQTT Analytics",
            "description": "Real-time analytics pipeline for MQTT data streams",
            "status": "Active",
            "created_at": "2025-01-21T14:30:00Z",
            "updated_at": "2025-01-21T14:30:00Z",
            "config": {
                "environment": "production",
                "auto_run": False,
                "notifications": True,
                "retry_attempts": 5
            }
        }
    ]
    save_projects(PROJECTS)

def base_layout(title: str, content: Any) -> str:
    """Base HTML layout with navigation and Datastar setup"""
    return str(h.html[
        h.head[
            h.\1[charset="utf-8"),
            h.\1[name="viewport", content="width=device-width, initial-scale=1"),
            h.title[f"{title} - FlowerPower"],
            h.\1[
                href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css",
                rel="stylesheet"
            ),
            h.\1[src="https://unpkg.com/@starfederation/datastar@latest"),
        ],
        h.\1[**{"data-ds-stream": "/datastar/stream"})[
            h.\1[".navbar.navbar-expand-lg.navbar-dark.bg-primary")[
                h.\1[".container-fluid")[
                    h.\1[".navbar-brand", href="/")["FlowerPower"],
                    h.\1[".navbar-nav")[
                        h.\1[".navbar-nav.me-auto")[
                            h.\1[".nav-item")[h.\1[".nav-link", href="/dashboard")["Dashboard"]],
                            h.\1[".nav-item")[h.\1[".nav-link", href="/projects")["Projects"]],
                            h.\1[".nav-item")[h.\1[".nav-link", href="/projects/new")["New Project"]],
                        ],
                    ],
                ],
            ],
            h.\1[".main-content")[
                h.\1[".container.mt-4")[content],
            ],
        ]
    ])

def project_card(project: Dict[str, Any]) -> Any:
    """Generate a project card component"""
    status = project.get("status", "Unknown")
    status_class = {
        "Active": "success",
        "Inactive": "secondary",
        "Error": "danger",
        "Unknown": "warning"
    }.get(status, "secondary")
    
    return h.\1[".card.mb-3")[
        h.\1[".card-body")[
            h.\1[".d-flex.justify-content-between.align-items-center")[
                h.\1[".card-title.d-inline")[project["name"]],
                h.\1[f".badge.bg-{status_class}.ms-2")[status],
            ],
            h.\1[".card-text")[project["description"]],
            h.\1[".text-muted")[f"Created: {project['created_at'][:10]}"],
            h.\1[".mt-2")[
                h.\1[".btn.btn-primary.btn-sm.me-2", href=f"/projects/{project['id']}")["View"],
                h.\1[".btn.btn-outline-secondary.btn-sm.me-2", href=f"/projects/{project['id']}/edit")["Edit"],
                h.\1[".btn.btn-outline-info.btn-sm", href=f"/projects/{project['id']}/config")["Config"],
            ],
        ],
    ]

@app.route("/")
async def home(request: Request):
    """Home page"""
    content = h.div[
        h.\1[".jumbotron.bg-light.p-5.rounded")[
            h.\1[".display-4")["Welcome to FlowerPower"],
            h.\1[".lead")[
                "A simple workflow framework for building and managing data pipelines."
            ],
            h.\1[".mt-3")[
                h.\1[".btn.btn-primary.btn-lg.me-3", href="/dashboard")["Dashboard"],
                h.\1[".btn.btn-outline-primary.btn-lg", href="/projects")["View Projects"],
            ],
        ]
    ]
    return html(base_layout("Home", content))

@app.route("/projects")
async def projects_list(request: Request):
    """List all projects"""
    content = h.div[
        h.\1[".d-flex.justify-content-between.align-items-center.mb-4")[
            h.h2["Projects"],
            h.\1[".btn.btn-success.mb-3", href="/projects/new")["Create New Project"],
        ],
        h.\1["#projects-list", **{"data-ds-id": "projects-list"})[
            [project_card(project) for project in PROJECTS] if PROJECTS else
            h.\1[".text-center.p-4")[
                h.\1[".text-muted")["No projects found."],
                h.\1[".btn.btn-primary", href="/projects/new")["Create your first project"],
            ],
        ]
    ]
    return html(base_layout("Projects", content))

@app.route("/projects/new", methods=["GET"])
async def new_project_form(request: Request):
    """Display new project form"""
    content = h.\1[
        h.\1["Create New Project"),
        h.\1[
            h.\1[
                h.\1["Project Name", for_="name", class_="form-label"),
                h.\1[
                    type="text",
                    id="name",
                    name="name",
                    class_="form-control",
                    required=True
                ),
                class_="mb-3"
            ),
            h.\1[
                h.\1["Description", for_="description", class_="form-label"),
                h.\1[
                    id="description",
                    name="description",
                    class_="form-control",
                    rows="3"
                ),
                class_="mb-3"
            ),
            h.\1[
                h.\1[
                    "Create Project",
                    type="submit",
                    class_="btn btn-primary me-2"
                ),
                h.\1["Cancel", href="/projects", class_="btn btn-secondary"),
                class_="mb-3"
            ),
            action="/projects",
            method="post",
            **{
                "data-ds-on-submit": "create-project",
                "data-ds-target": "#form-result"
            }
        ),
        h.\1[
            id="form-result",
            **{"data-ds-id": "form-result"}
        )
    )
    return html(base_layout("New Project", content))

@app.route("/projects", methods=["POST"])
async def create_project(request: Request):
    """Handle project creation (form submission)"""
    try:
        form_data = request.form
        name = form_data.get("name", "").strip()
        description = form_data.get("description", "").strip()
        
        if not name:
            # Send error message via Datastar
            await emit_to_all("form-result", {
                "content": str(h.\1[
                    "Project name is required.",
                    class_="alert alert-danger"
                ))
            })
            return json({"status": "error", "message": "Project name is required"})
        
        # Create new project with enhanced structure
        current_time = datetime.now().isoformat()
        new_project = {
            "id": get_next_project_id(PROJECTS),
            "name": name,
            "description": description,
            "status": "Active",
            "created_at": current_time,
            "updated_at": current_time,
            "config": {
                "environment": "development",
                "auto_run": True,
                "notifications": True,
                "retry_attempts": 3
            }
        }
        
        # Add to projects list and save to file
        PROJECTS.append(new_project)
        save_success = save_projects(PROJECTS)
        
        if not save_success:
            # Remove from memory if save failed
            PROJECTS.pop()
            await emit_to_all("form-result", {
                "content": str(h.\1[
                    "Error saving project to storage.",
                    class_="alert alert-danger"
                ))
            })
            return json({"status": "error", "message": "Failed to save project"}, status=500)
        
        # Send success message and redirect
        success_content = h.\1[
            h.\1[
                f"Project '{name}' created successfully!",
                class_="alert alert-success"
            ),
            h.\1[
                "setTimeout(() => window.location.href = '/projects', 2000);"
            )
        )
        
        await emit_to_all("form-result", {
            "content": str(success_content)
        })
        
        return json({"status": "success", "project_id": new_project["id"]})
        
    except Exception as e:
        await emit_to_all("form-result", {
            "content": str(h.\1[
                f"Error creating project: {str(e)}",
                class_="alert alert-danger"
            ))
        })
        return json({"status": "error", "message": str(e)}, status=500)

@app.route("/projects/<project_id:int>")
async def project_detail(request: Request, project_id: int):
    """Show project details"""
    project = next((p for p in PROJECTS if p["id"] == project_id), None)
    if not project:
        content = h.\1[
            h.\1["Project Not Found"),
            h.\1["The requested project could not be found."),
            h.\1["Back to Projects", href="/projects", class_="btn btn-primary")
        )
        return html(base_layout("Project Not Found", content))
    
    status = project.get("status", "Unknown")
    status_class = {
        "Active": "success",
        "Inactive": "secondary",
        "Error": "danger",
        "Unknown": "warning"
    }.get(status, "secondary")
    
    config = project.get("config", {})
    
    content = h.\1[
        h.\1[
            h.\1[
                h.\1[project["name"], class_="d-inline me-3"),
                h.\1[status, class_=f"badge bg-{status_class}")
            ),
            h.\1[
                h.\1["Back to Projects", href="/projects", class_="btn btn-outline-secondary me-2"),
                h.\1["Edit Project", href=f"/projects/{project_id}/edit", class_="btn btn-primary me-2"),
                h.\1["Configuration", href=f"/projects/{project_id}/config", class_="btn btn-outline-info"),
            ),
            class_="d-flex justify-content-between align-items-center mb-4"
        ),
        h.\1[
            h.\1[
                h.\1["Description"),
                h.\1[project["description"] or "No description provided."),
                class_="card-body"
            ),
            class_="card mb-3"
        ),
        h.\1[
            h.\1[
                h.\1["Project Details"),
                h.\1[
                    h.\1["ID", class_="col-sm-3"),
                    h.\1[str(project["id"]), class_="col-sm-9"),
                    h.\1["Status", class_="col-sm-3"),
                    h.\1[status, class_="col-sm-9"),
                    h.\1["Created", class_="col-sm-3"),
                    h.\1[project["created_at"][:19].replace("T", " "), class_="col-sm-9"),
                    h.\1["Updated", class_="col-sm-3"),
                    h.\1[project.get("updated_at", "N/A")[:19].replace("T", " "), class_="col-sm-9"),
                    class_="row"
                ),
                class_="card-body"
            ),
            class_="card mb-3"
        ),
        h.\1[
            h.\1[
                h.\1["Configuration"),
                h.\1[
                    h.\1["Environment", class_="col-sm-3"),
                    h.\1[config.get("environment", "N/A"), class_="col-sm-9"),
                    h.\1["Auto Run", class_="col-sm-3"),
                    h.\1["Yes" if config.get("auto_run") else "No", class_="col-sm-9"),
                    h.\1["Notifications", class_="col-sm-3"),
                    h.\1["Enabled" if config.get("notifications") else "Disabled", class_="col-sm-9"),
                    h.\1["Retry Attempts", class_="col-sm-3"),
                    h.\1[str(config.get("retry_attempts", "N/A")), class_="col-sm-9"),
                    class_="row"
                ),
                class_="card-body"
            ),
            class_="card"
        )
    )
    return html(base_layout(f"Project: {project['name']}", content))

@app.route("/dashboard")
async def dashboard(request: Request):
    """Project overview dashboard"""
    total_projects = len(PROJECTS)
    active_projects = len([p for p in PROJECTS if p.get("status") == "Active"])
    inactive_projects = len([p for p in PROJECTS if p.get("status") == "Inactive"])
    error_projects = len([p for p in PROJECTS if p.get("status") == "Error"])
    
    # Recent projects (last 3)
    recent_projects = sorted(PROJECTS, key=lambda x: x.get("updated_at", ""), reverse=True)[:3]
    
    content = h.\1[
        h.\1["Project Dashboard"),
        
        # Statistics cards
        h.\1[
            h.\1[
                h.\1[
                    h.\1[
                        h.\1[str(total_projects), class_="card-title text-primary"),
                        h.\1["Total Projects", class_="card-text"),
                        class_="card-body text-center"
                    ),
                    class_="card"
                ),
                class_="col-md-3"
            ),
            h.\1[
                h.\1[
                    h.\1[
                        h.\1[str(active_projects), class_="card-title text-success"),
                        h.\1["Active Projects", class_="card-text"),
                        class_="card-body text-center"
                    ),
                    class_="card"
                ),
                class_="col-md-3"
            ),
            h.\1[
                h.\1[
                    h.\1[
                        h.\1[str(inactive_projects), class_="card-title text-secondary"),
                        h.\1["Inactive Projects", class_="card-text"),
                        class_="card-body text-center"
                    ),
                    class_="card"
                ),
                class_="col-md-3"
            ),
            h.\1[
                h.\1[
                    h.\1[
                        h.\1[str(error_projects), class_="card-title text-danger"),
                        h.\1["Error Projects", class_="card-text"),
                        class_="card-body text-center"
                    ),
                    class_="card"
                ),
                class_="col-md-3"
            ),
            class_="row mb-4"
        ),
        
        # Recent projects
        h.\1[
            h.\1["Recent Projects"),
            h.\1[
                [project_card(project) for project in recent_projects] if recent_projects else
                h.\1[
                    h.\1["No projects found.", class_="text-muted"),
                    h.\1["Create your first project", href="/projects/new", class_="btn btn-primary"),
                    class_="text-center p-4"
                )
            ),
            class_="mb-4"
        ),
        
        # Quick actions
        h.\1[
            h.\1["Quick Actions"),
            h.\1[
                h.\1["Create New Project", href="/projects/new", class_="btn btn-primary me-2"),
                h.\1["View All Projects", href="/projects", class_="btn btn-outline-primary"),
                class_="mb-3"
            )
        )
    )
    return html(base_layout("Dashboard", content))

@app.route("/projects/<project_id:int>/edit", methods=["GET"])
async def edit_project_form(request: Request, project_id: int):
    """Display edit project form"""
    project = next((p for p in PROJECTS if p["id"] == project_id), None)
    if not project:
        content = h.\1[
            h.\1["Project Not Found"),
            h.\1["The requested project could not be found."),
            h.\1["Back to Projects", href="/projects", class_="btn btn-primary")
        )
        return html(base_layout("Project Not Found", content))
    
    content = h.\1[
        h.\1[f"Edit Project: {project['name']}"),
        h.\1[
            h.\1[
                h.\1["Project Name", for_="name", class_="form-label"),
                h.\1[
                    type="text",
                    id="name",
                    name="name",
                    class_="form-control",
                    value=project["name"],
                    required=True
                ),
                class_="mb-3"
            ),
            h.\1[
                h.\1["Description", for_="description", class_="form-label"),
                h.\1[
                    project["description"],
                    id="description",
                    name="description",
                    class_="form-control",
                    rows="3"
                ),
                class_="mb-3"
            ),
            h.\1[
                h.\1["Status", for_="status", class_="form-label"),
                h.\1[
                    h.\1["Active", value="Active", selected=project.get("status") == "Active"),
                    h.\1["Inactive", value="Inactive", selected=project.get("status") == "Inactive"),
                    h.\1["Error", value="Error", selected=project.get("status") == "Error"),
                    id="status",
                    name="status",
                    class_="form-select"
                ),
                class_="mb-3"
            ),
            h.\1[
                h.\1[
                    "Update Project",
                    type="submit",
                    class_="btn btn-primary me-2"
                ),
                h.\1["Cancel", href=f"/projects/{project_id}", class_="btn btn-secondary me-2"),
                h.\1[
                    "Delete Project",
                    type="button",
                    class_="btn btn-danger",
                    onclick=f"if(confirm('Are you sure you want to delete this project?')) window.location.href='/projects/{project_id}/delete'"
                ),
                class_="mb-3"
            ),
            action=f"/projects/{project_id}/edit",
            method="post",
            **{
                "data-ds-on-submit": "edit-project",
                "data-ds-target": "#form-result"
            }
        ),
        h.\1[
            id="form-result",
            **{"data-ds-id": "form-result"}
        )
    )
    return html(base_layout(f"Edit Project: {project['name']}", content))

@app.route("/projects/<project_id:int>/edit", methods=["POST"])
async def update_project(request: Request, project_id: int):
    """Handle project update"""
    try:
        project = next((p for p in PROJECTS if p["id"] == project_id), None)
        if not project:
            return json({"status": "error", "message": "Project not found"}, status=404)
        
        form_data = request.form
        name = form_data.get("name", "").strip()
        description = form_data.get("description", "").strip()
        status = form_data.get("status", "Active")
        
        if not name:
            await emit_to_all("form-result", {
                "content": str(h.\1[
                    "Project name is required.",
                    class_="alert alert-danger"
                ))
            })
            return json({"status": "error", "message": "Project name is required"})
        
        # Update project
        project["name"] = name
        project["description"] = description
        project["status"] = status
        project["updated_at"] = datetime.now().isoformat()
        
        # Save to file
        save_success = save_projects(PROJECTS)
        if not save_success:
            await emit_to_all("form-result", {
                "content": str(h.\1[
                    "Error saving project updates.",
                    class_="alert alert-danger"
                ))
            })
            return json({"status": "error", "message": "Failed to save project"}, status=500)
        
        # Send success message and redirect
        success_content = h.\1[
            h.\1[
                f"Project '{name}' updated successfully!",
                class_="alert alert-success"
            ),
            h.\1[
                f"setTimeout(() => window.location.href = '/projects/{project_id}', 2000);"
            )
        )
        
        await emit_to_all("form-result", {
            "content": str(success_content)
        })
        
        return json({"status": "success", "project_id": project_id})
        
    except Exception as e:
        await emit_to_all("form-result", {
            "content": str(h.\1[
                f"Error updating project: {str(e)}",
                class_="alert alert-danger"
            ))
        })
        return json({"status": "error", "message": str(e)}, status=500)

@app.route("/projects/<project_id:int>/config", methods=["GET"])
async def project_config_form(request: Request, project_id: int):
    """Display project configuration form"""
    project = next((p for p in PROJECTS if p["id"] == project_id), None)
    if not project:
        content = h.\1[
            h.\1["Project Not Found"),
            h.\1["The requested project could not be found."),
            h.\1["Back to Projects", href="/projects", class_="btn btn-primary")
        )
        return html(base_layout("Project Not Found", content))
    
    config = project.get("config", {})
    
    content = h.\1[
        h.\1[f"Configuration: {project['name']}"),
        h.\1[
            h.\1[
                h.\1["Environment", for_="environment", class_="form-label"),
                h.\1[
                    h.\1["development", value="development", selected=config.get("environment") == "development"),
                    h.\1["staging", value="staging", selected=config.get("environment") == "staging"),
                    h.\1["production", value="production", selected=config.get("environment") == "production"),
                    id="environment",
                    name="environment",
                    class_="form-select"
                ),
                class_="mb-3"
            ),
            h.\1[
                h.\1[
                    h.\1[
                        type="checkbox",
                        id="auto_run",
                        name="auto_run",
                        class_="form-check-input",
                        checked=config.get("auto_run", False)
                    ),
                    h.\1["Auto Run", for_="auto_run", class_="form-check-label"),
                    class_="form-check"
                ),
                class_="mb-3"
            ),
            h.\1[
                h.\1[
                    h.\1[
                        type="checkbox",
                        id="notifications",
                        name="notifications",
                        class_="form-check-input",
                        checked=config.get("notifications", False)
                    ),
                    h.\1["Enable Notifications", for_="notifications", class_="form-check-label"),
                    class_="form-check"
                ),
                class_="mb-3"
            ),
            h.\1[
                h.\1["Retry Attempts", for_="retry_attempts", class_="form-label"),
                h.\1[
                    type="number",
                    id="retry_attempts",
                    name="retry_attempts",
                    class_="form-control",
                    value=str(config.get("retry_attempts", 3)),
                    min="0",
                    max="10"
                ),
                class_="mb-3"
            ),
            h.\1[
                h.\1[
                    "Update Configuration",
                    type="submit",
                    class_="btn btn-primary me-2"
                ),
                h.\1["Cancel", href=f"/projects/{project_id}", class_="btn btn-secondary"),
                class_="mb-3"
            ),
            action=f"/projects/{project_id}/config",
            method="post",
            **{
                "data-ds-on-submit": "update-config",
                "data-ds-target": "#form-result"
            }
        ),
        h.\1[
            id="form-result",
            **{"data-ds-id": "form-result"}
        )
    )
    return html(base_layout(f"Configuration: {project['name']}", content))

@app.route("/projects/<project_id:int>/config", methods=["POST"])
async def update_project_config(request: Request, project_id: int):
    """Handle project configuration update"""
    try:
        project = next((p for p in PROJECTS if p["id"] == project_id), None)
        if not project:
            return json({"status": "error", "message": "Project not found"}, status=404)
        
        form_data = request.form
        
        # Update configuration
        config = {
            "environment": form_data.get("environment", "development"),
            "auto_run": "auto_run" in form_data,
            "notifications": "notifications" in form_data,
            "retry_attempts": int(form_data.get("retry_attempts", 3))
        }
        
        project["config"] = config
        project["updated_at"] = datetime.now().isoformat()
        
        # Save to file
        save_success = save_projects(PROJECTS)
        if not save_success:
            await emit_to_all("form-result", {
                "content": str(h.\1[
                    "Error saving configuration.",
                    class_="alert alert-danger"
                ))
            })
            return json({"status": "error", "message": "Failed to save configuration"}, status=500)
        
        # Send success message and redirect
        success_content = h.\1[
            h.\1[
                "Configuration updated successfully!",
                class_="alert alert-success"
            ),
            h.\1[
                f"setTimeout(() => window.location.href = '/projects/{project_id}', 2000);"
            )
        )
        
        await emit_to_all("form-result", {
            "content": str(success_content)
        })
        
        return json({"status": "success", "project_id": project_id})
        
    except Exception as e:
        await emit_to_all("form-result", {
            "content": str(h.\1[
                f"Error updating configuration: {str(e)}",
                class_="alert alert-danger"
            ))
        })
        return json({"status": "error", "message": str(e)}, status=500)

@app.route("/projects/<project_id:int>/delete")
async def delete_project(request: Request, project_id: int):
    """Handle project deletion"""
    try:
        project_index = next((i for i, p in enumerate(PROJECTS) if p["id"] == project_id), None)
        if project_index is None:
            content = h.\1[
                h.\1["Project Not Found"),
                h.\1["The requested project could not be found."),
                h.\1["Back to Projects", href="/projects", class_="btn btn-primary")
            )
            return html(base_layout("Project Not Found", content))
        
        project_name = PROJECTS[project_index]["name"]
        PROJECTS.pop(project_index)
        
        # Save to file
        save_success = save_projects(PROJECTS)
        if not save_success:
            # This is tricky - we already removed it from memory, but save failed
            # For now, just show error - in production you'd want better error handling
            content = h.\1[
                h.\1["Error"),
                h.\1["Error saving after project deletion. Please check the system."),
                h.\1["Back to Projects", href="/projects", class_="btn btn-primary")
            )
            return html(base_layout("Error", content))
        
        # Success page
        content = h.\1[
            h.\1[
                h.\1["Project Deleted"),
                h.\1[f"Project '{project_name}' has been successfully deleted."),
                h.\1["Back to Projects", href="/projects", class_="btn btn-primary"),
                class_="alert alert-success p-4"
            )
        )
        return html(base_layout("Project Deleted", content))
        
    except Exception as e:
        content = h.\1[
            h.\1["Error"),
            h.\1[f"Error deleting project: {str(e)}"),
            h.\1["Back to Projects", href="/projects", class_="btn btn-primary")
        )
        return html(base_layout("Error", content))

@app.route("/datastar/stream")
async def datastar_stream(request: Request):
    """Datastar SSE stream endpoint"""
    async def stream_generator():
        # Add this connection to the global set
        sse_connections.add(stream_generator)
        
        try:
            # Send initial connection event
            yield f"data: {json.dumps({'type': 'connected'})}\n\n"
            
            # Keep connection alive
            while True:
                await asyncio.sleep(1)
                # Send heartbeat to keep connection alive
                yield f"data: {json.dumps({'type': 'heartbeat'})}\n\n"
                
        except Exception:
            # Remove from connections on error
            sse_connections.discard(stream_generator)
            raise
    
    return ServerSentEventGenerator(stream_generator(), headers=SSE_HEADERS)

@app.route("/api/projects")
async def api_projects(request: Request):
    """API endpoint for projects (for future AJAX calls)"""
    return json({"projects": PROJECTS})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)