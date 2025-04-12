import os
import yaml
from pathlib import Path

from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse

from ...cfg import Config
from ...pipeline import PipelineManager
from .. import templates

router = APIRouter(prefix="/config", tags=["config"])

base_dir = os.environ.get("FLOWERPOWER_BASE_DIR", str(Path.cwd()))

@router.get("/project", response_class=HTMLResponse)
async def get_project_config(request: Request):
    """Get project configuration"""
    config = Config.load(base_dir=base_dir)
    
    # Get raw YAML content
    config_path = Path(base_dir) / "conf" / "project.yml"
    config_content = ""
    if config_path.exists():
        with open(config_path, "r") as f:
            config_content = f.read()
    
    return templates.TemplateResponse(
        "config/project.html",
        {
            "request": request,
            "config": config.project,
            "config_content": config_content,
            "base_dir": base_dir
        }
    )

@router.post("/project/update")
async def update_project_config(
    request: Request,
    config_content: str = Form(...)
):
    """Update project configuration"""
    try:
        # Validate YAML
        config_data = yaml.safe_load(config_content)
        
        # Write to file
        config_path = Path(base_dir) / "conf" / "project.yml"
        with open(config_path, "w") as f:
            f.write(config_content)
        
        return {"success": True, "message": "Project configuration updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/pipeline/{name}", response_class=HTMLResponse)
async def get_pipeline_config(request: Request, name: str):
    """Get pipeline configuration"""
    pipeline_manager = PipelineManager(base_dir=base_dir)
    pipeline_manager.load_config(name=name)
    
    # Get raw YAML content
    config_path = Path(base_dir) / "conf" / "pipelines" / f"{name}.yml"
    config_content = ""
    if config_path.exists():
        with open(config_path, "r") as f:
            config_content = f.read()
    
    return templates.TemplateResponse(
        "config/pipeline.html",
        {
            "request": request,
            "pipeline": name,
            "config": pipeline_manager.cfg.pipeline,
            "config_content": config_content,
            "base_dir": base_dir
        }
    )

@router.post("/pipeline/{name}/update")
async def update_pipeline_config(
    request: Request,
    name: str,
    config_content: str = Form(...)
):
    """Update pipeline configuration"""
    try:
        # Validate YAML
        config_data = yaml.safe_load(config_content)
        
        # Write to file
        config_path = Path(base_dir) / "conf" / "pipelines" / f"{name}.yml"
        
        # Ensure directory exists
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, "w") as f:
            f.write(config_content)
        
        return {"success": True, "message": f"Pipeline {name} configuration updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
