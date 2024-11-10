from sanic import Blueprint
from orjson import dumps, loads
from sanic.response import json
from ..pipeline import run, run_job, add_job, schedule
from flowerpower.scheduler import SchedulerManager

# import asyncio

bp = Blueprint("flowerpower_api", url_prefix="api")


@bp.post("/run/<name>")
async def run_pipeline(request, name: str,)->json:
    
    try:
        base_dir = request.json.pop("base_dir", None) or request.app.config.BASE_DIR
        
        result = run(name, base_dir=base_dir, **request.json)
        return json({"status": "success", "result": result})
    except Exception as e:
        return json({"status": "error", "message": str(e)})


@bp.post("/run-job/<pipeline_name>")
async def run_job(request, pipeline_name):
    try:
        job_data = request.json
        pipeline = Pipeline(pipeline_name, base_dir=request.app.config.BASE_DIR)
        result = pipeline.run_job(job_data)
        return json({"status": "success", "result": result})
    except Exception as e:
        return json({"status": "error", "message": str(e)})


@bp.post("/add-job/<pipeline_name>")
async def add_job(request, pipeline_name):
    try:
        job_config = request.json
        pipeline = Pipeline(pipeline_name, base_dir=request.app.config.BASE_DIR)
        result = pipeline.add_job(job_config)
        return json({"status": "success", "job_id": result})
    except Exception as e:
        return json({"status": "error", "message": str(e)})


@bp.post("/schedule/<pipeline_name>")
async def schedule_pipeline(request, pipeline_name):
    try:
        schedule_config = request.json
        pipeline = Pipeline(pipeline_name, base_dir=request.app.config.BASE_DIR)
        result = pipeline.schedule(schedule_config)
        return json({"status": "success", "schedule_id": result})
    except Exception as e:
        return json({"status": "error", "message": str(e)})


# @app.post("/run-pipeline/<pipeline_name>")
# async def run_pipeline(request, pipeline_name):
#     try:
#         payload = request.json
#         pipeline = Pipeline(pipeline_name, base_dir=args.base_dir)
#         result = pipeline.run(inputs={"payload": payload}, with_tracker=False)
#         return json_response({"status": "success", "result": result})
#     except Exception as e:
#         return json_response({"status": "error", "message": str(e)})


# @app.post("/run-job/<pipeline_name>")
# async def run_job(request, pipeline_name):
#     try:
#         job_data = request.json
#         pipeline = Pipeline(pipeline_name, base_dir=args.base_dir)
#         result = pipeline.run_job(job_data)
#         return json_response({"status": "success", "result": result})
#     except Exception as e:
#         return json_response({"status": "error", "message": str(e)})


# @app.post("/add-job/<pipeline_name>")
# async def add_job(request, pipeline_name):
#     try:
#         job_config = request.json
#         pipeline = Pipeline(pipeline_name, base_dir=args.base_dir)
#         result = pipeline.add_job(job_config)
#         return json_response({"status": "success", "job_id": result})
#     except Exception as e:
#         return json_response({"status": "error", "message": str(e)})


# @app.post("/schedule/<pipeline_name>")
# async def schedule_pipeline(request, pipeline_name):
#     try:
#         schedule_config = request.json
#         pipeline = Pipeline(pipeline_name, base_dir=args.base_dir)
#         result = pipeline.schedule(schedule_config)
#         return json_response({"status": "success", "schedule_id": result})
#     except Exception as e:
#         return json_response({"status": "error", "message": str(e)})


# @app.get("/scheduler/jobs")
# async def get_jobs(request):
#     try:
#         jobs = scheduler.get_jobs()
#         return json_response({"status": "success", "jobs": jobs})
#     except Exception as e:
#         return json_response({"status": "error", "message": str(e)})


# @app.get("/scheduler/schedules")
# async def get_schedules(request):
#     try:
#         schedules = scheduler.get_schedules()
#         return json_response({"status": "success", "schedules": schedules})
#     except Exception as e:
#         return json_response({"status": "error", "message": str(e)})


# @app.post("/mqtt/start/<pipeline_name>")
# async def start_mqtt_handler(request, pipeline_name):
#     try:
#         pipeline = Pipeline(pipeline_name, base_dir=args.base_dir)
#         pipeline.on_mqtt_message()
#         return json_response(
#             {
#                 "status": "success",
#                 "message": f"MQTT handler started for {pipeline_name}",
#             }
#         )
#     except Exception as e:
#         return json_response({"status": "error", "message": str(e)})


# if __name__ == "__main__":
#    app.run(host="0.0.0.0", port=8000)
