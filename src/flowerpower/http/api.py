from sanic import Sanic,
from orjson import dumps, loads
from sanic.response import json as json_response
import argparse
from flowerpower.pipeline import Pipeline
from flowerpower.scheduler import SchedulerManager

# import asyncio

app = Sanic("pipeline_server", dumps=dumps, loads=loads)
scheduler = None

parser = argparse.ArgumentParser()
parser.add_argument("--base-dir", required=True, help="Base directory for pipelines")
args = parser.parse_args()


@app.listener("before_server_start")
def init_scheduler(app, loop):
    app.ctx.scheduler = SchedulerManager(base_dir=args.base_dir)
    app.ctx.scheduler.start_worker(background=True)


@app.listener("before_server_stop")
def cleanup_scheduler(app, loop):
    if hasattr(app.ctx, "scheduler"):
        app.ctx.scheduler.stop_worker()


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
