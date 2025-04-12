import os
import importlib.util
from pathlib import Path

from fastapi import APIRouter, Request, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse

from ...pipeline import PipelineManager
from .. import templates

router = APIRouter(prefix="/scheduler", tags=["scheduler"])

base_dir = os.environ.get("FLOWERPOWER_BASE_DIR", str(Path.cwd()))

# Check if scheduler is available
has_scheduler = importlib.util.find_spec("apscheduler") is not None
if not has_scheduler:
    # Create minimal router if scheduler not available
    @router.get("/", response_class=HTMLResponse)
    async def scheduler_not_available(request: Request):
        return templates.TemplateResponse(
            "scheduler/not_available.html",
            {"request": request}
        )
else:
    from ...scheduler import SchedulerManager

    # Worker process handler
    worker_process = None

    def start_worker_process(base_dir):
        global worker_process
        import subprocess
        import sys

        cmd = [
            sys.executable, 
            "-m", "flowerpower", 
            "scheduler", 
            "start-worker",
            "--base-dir", base_dir
        ]
        worker_process = subprocess.Popen(cmd)

    def stop_worker_process():
        global worker_process
        if worker_process:
            worker_process.terminate()
            worker_process = None

    @router.get("/", response_class=HTMLResponse)
    async def scheduler_dashboard(request: Request):
        """Scheduler dashboard with schedules and jobs"""
        pipeline_manager = PipelineManager(base_dir=base_dir)
        
        with SchedulerManager(fs=pipeline_manager._fs, role="scheduler") as sm:
            schedules = sm.get_schedules(as_dict=True)
            jobs = sm.get_jobs(as_dict=True)
            
        return templates.TemplateResponse(
            "scheduler/dashboard.html",
            {
                "request": request,
                "schedules": schedules,
                "jobs": jobs,
                "worker_running": worker_process is not None,
                "base_dir": base_dir
            }
        )

    @router.post("/start-worker")
    async def start_worker(background_tasks: BackgroundTasks):
        """Start scheduler worker"""
        global worker_process
        
        if worker_process is not None:
            return {"success": False, "message": "Worker is already running"}
            
        try:
            background_tasks.add_task(start_worker_process, base_dir)
            return {"success": True, "message": "Worker started successfully"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("/stop-worker")
    async def stop_worker():
        """Stop scheduler worker"""
        global worker_process
        
        if worker_process is None:
            return {"success": False, "message": "No worker is running"}
            
        try:
            stop_worker_process()
            return {"success": True, "message": "Worker stopped successfully"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("/pause-schedule/{schedule_id}")
    async def pause_schedule(schedule_id: str):
        """Pause a scheduled pipeline"""
        try:
            pipeline_manager = PipelineManager(base_dir=base_dir)
            
            with SchedulerManager(fs=pipeline_manager._fs, role="scheduler") as sm:
                sm.pause_schedule(schedule_id)
                
            return {"success": True, "message": f"Schedule {schedule_id} paused successfully"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("/resume-schedule/{schedule_id}")
    async def resume_schedule(schedule_id: str):
        """Resume a paused schedule"""
        try:
            pipeline_manager = PipelineManager(base_dir=base_dir)
            
            with SchedulerManager(fs=pipeline_manager._fs, role="scheduler") as sm:
                sm.resume_schedule(schedule_id)
                
            return {"success": True, "message": f"Schedule {schedule_id} resumed successfully"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.delete("/remove-schedule/{schedule_id}")
    async def remove_schedule(schedule_id: str):
        """Remove a schedule"""
        try:
            pipeline_manager = PipelineManager(base_dir=base_dir)
            
            with SchedulerManager(fs=pipeline_manager._fs, role="scheduler") as sm:
                sm.remove_schedule(schedule_id)
                
            return {"success": True, "message": f"Schedule {schedule_id} removed successfully"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
