import os
from pathlib import Path
from typing import Dict, List, Optional, Any

from fastapi import APIRouter, Request, Form, HTTPException, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel

from ...pipeline import PipelineManager, Pipeline
from .. import templates

router = APIRouter(prefix="/pipelines", tags=["pipelines"])

base_dir = os.environ.get("FLOWERPOWER_BASE_DIR", str(Path.cwd()))

class PipelineRunRequest(BaseModel):
    name: str
    executor: Optional[str] = None
    inputs: Optional[Dict[str, Any]] = None
    final_vars: Optional[List[str]] = None
    config: Optional[Dict[str, Any]] = None
    with_tracker: bool = False
    with_opentelemetry: bool = False
    with_progressbar: bool = False

class PipelineScheduleRequest(BaseModel):
    name: str
    trigger_type: str = "cron"
    executor: Optional[str] = None
    inputs: Optional[Dict[str, Any]] = None
    final_vars: Optional[List[str]] = None
    config: Optional[Dict[str, Any]] = None
    with_tracker: bool = False
    with_opentelemetry: bool = False
    with_progressbar: bool = False
    paused: bool = False
    crontab: Optional[str] = None
    overwrite: bool = False

@router.get("/", response_class=HTMLResponse)
async def list_pipelines(request: Request):
    """List all available pipelines"""
    pipeline_manager = PipelineManager(base_dir=base_dir)
    pipelines = pipeline_manager.list_pipelines() or []  # Ensure we have a list
    
    return templates.TemplateResponse(
        "pipelines/list.html",
        {
            "request": request,
            "pipelines": pipelines,
            "base_dir": base_dir
        }
    )

@router.get("/{name}", response_class=HTMLResponse)
async def get_pipeline(request: Request, name: str):
    """Get detailed pipeline view"""
    pipeline = Pipeline(name=name, base_dir=base_dir)
    summary = pipeline.get_summary()
    
    # Get pipeline code
    code = None
    pipeline_path = Path(base_dir) / "pipelines" / f"{name}.py"
    if pipeline_path.exists():
        with open(pipeline_path, "r") as f:
            code = f.read()
    
    return templates.TemplateResponse(
        "pipelines/detail.html",
        {
            "request": request,
            "pipeline": name,
            "summary": summary,
            "code": code,
            "base_dir": base_dir
        }
    )

@router.post("/{name}/run")
async def run_pipeline(request: Request, name: str, run_data: PipelineRunRequest):
    """Run a pipeline"""
    try:
        pipeline = Pipeline(name=name, base_dir=base_dir)
        result = pipeline.run(
            inputs=run_data.inputs,
            final_vars=run_data.final_vars,
            config=run_data.config,
            executor=run_data.executor,
            with_tracker=run_data.with_tracker,
            with_opentelemetry=run_data.with_opentelemetry,
            with_progressbar=run_data.with_progressbar
        )
        
        return {"success": True, "message": f"Pipeline {name} executed successfully", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{name}/schedule")
async def schedule_pipeline(request: Request, name: str, schedule_data: PipelineScheduleRequest):
    """Schedule a pipeline"""
    try:
        pipeline = Pipeline(name=name, base_dir=base_dir)
        kwargs = {}
        if schedule_data.crontab:
            kwargs["crontab"] = schedule_data.crontab
            
        schedule_id = pipeline.schedule(
            trigger_type=schedule_data.trigger_type,
            inputs=schedule_data.inputs,
            final_vars=schedule_data.final_vars,
            config=schedule_data.config,
            executor=schedule_data.executor,
            with_tracker=schedule_data.with_tracker,
            with_opentelemetry=schedule_data.with_opentelemetry,
            with_progressbar=schedule_data.with_progressbar,
            paused=schedule_data.paused,
            overwrite=schedule_data.overwrite,
            **kwargs
        )
        
        return {"success": True, "message": f"Pipeline {name} scheduled successfully", "schedule_id": schedule_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{name}/update-code")
async def update_pipeline_code(
    request: Request, 
    name: str, 
    code: str = Form(...),
):
    """Update pipeline code"""
    try:
        pipeline_path = Path(base_dir) / "pipelines" / f"{name}.py"
        with open(pipeline_path, "w") as f:
            f.write(code)
        
        return {"success": True, "message": f"Pipeline code updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{name}/edit", response_class=HTMLResponse)
async def edit_pipeline(request: Request, name: str):
    """Edit pipeline code and configuration"""
    pipeline = Pipeline(name=name, base_dir=base_dir)
    summary = pipeline.get_summary()
    
    # Get pipeline code
    code = None
    pipeline_path = Path(base_dir) / "pipelines" / f"{name}.py"
    if pipeline_path.exists():
        with open(pipeline_path, "r") as f:
            code = f.read()
    
    return templates.TemplateResponse(
        "pipelines/edit.html",
        {
            "request": request,
            "pipeline": name,
            "summary": summary,
            "code": code,
            "base_dir": base_dir
        }
    )

@router.post("/new")
async def create_pipeline(name: str = Form(...)):
    """Create a new pipeline"""
    try:
        pipeline_manager = PipelineManager(base_dir=base_dir)
        pipeline_manager.new(name=name)
        return RedirectResponse(url=f"/pipelines/{name}/edit", status_code=303)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
