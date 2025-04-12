import importlib.util
import os
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from ..pipeline import PipelineManager
from ..cfg import Config

# Initialize FastAPI app
app = FastAPI(
    title="FlowerPower UI",
    description="Web UI for the FlowerPower framework",
    version="1.0.0",
)

# Set base directory
base_dir = os.environ.get("FLOWERPOWER_BASE_DIR", str(Path.cwd()))

# Set up template and static file directories
package_root = Path(__file__).parent
templates = Jinja2Templates(directory=str(package_root / "templates"))
app.mount("/static", StaticFiles(directory=str(package_root / "static")), name="static")

# Import and include routers
from .routes import pipelines, scheduler, config

app.include_router(pipelines.router)
app.include_router(scheduler.router)
app.include_router(config.router)

# Check for scheduler availability
has_scheduler = importlib.util.find_spec("apscheduler") is not None

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page with dashboard overview"""
    # Create pipeline manager to get pipelines
    pipeline_manager = PipelineManager(base_dir=base_dir)
    pipelines_list = pipeline_manager.list_pipelines() or []  # Ensure we have a list, even if empty
    
    # Get schedules if scheduler is available
    schedules = []
    if has_scheduler:
        from ..scheduler import SchedulerManager
        with SchedulerManager(fs=pipeline_manager._fs, role="scheduler") as sm:
            schedules = sm.get_schedules(as_dict=True) or []  # Ensure we have a list
    
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "pipelines": pipelines_list,
            "schedules": schedules,
            "has_scheduler": has_scheduler,
            "base_dir": base_dir,
        }
    )
