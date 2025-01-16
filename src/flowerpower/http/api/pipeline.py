import dill
from sanic import Blueprint, SanicException
from sanic_ext import openapi


from sanic.response import json, raw, html

from ...pipeline import Pipeline, PipelineManager
from ..models.pipeline import (
    PipelineRun,
    PipelineAddJob,
    PipelineSchedule,
    PipelineManagerNew,
    PipelineManagerImportExport,
    PipelineDelete,
    PipelineManagerSummary,
)
from ..utils import deserialize_and_validate

bp = Blueprint("api_flowerpower_pipeline", url_prefix="api/pipeline")


@bp.post("run/<name>")
@openapi.body({"application/json": PipelineRun}, required=False)
@openapi.summary("Run a pipeline")
@openapi.description("Run a pipeline with the given parameters")
# @openapi.response(
#     200,
# )
async def run(
    request,
    name: str,
):

    body = await deserialize_and_validate(PipelineRun, body=request.json)
    # body = request.json

    try:
        with Pipeline(
            name=name,
            base_dir=request.app.config.BASE_DIR,
            storage_options=request.app.config.STORAGE_OPTIONS,
            # cfg_dir=request.app.config.CFG_DIR,
            # pipelines_dir=request.app.config.PIPELINES_DIR,
        ) as pipeline:
            final_vars = pipeline.run(**body.model_dump())

        final_vars = {k: dill.dumps(v) for k, v in final_vars.items()}
        return bytes(final_vars)
        return json({"status": "success", "message": "Pipeline ran successfully"})
    except Exception as e:
        raise SanicException(str(e))


@bp.post("run-job/<name>")
@openapi.body({"application/json": PipelineRun}, required=False)
@openapi.summary("Run a pipeline as a job")
@openapi.description("Run a pipeline as a job with the given parameters")
# @openapi.response(200, {"application/json": dict[str, Any]})
async def run_job(
    request,
    name: str,
):
    body = await deserialize_and_validate(PipelineRun, body=request.json)
    try:
        with Pipeline(
            name=name,
            base_dir=request.app.config.BASE_DIR,
            storage_options=request.app.config.STORAGE_OPTIONS,
            cfg_dir=request.app.config.CFG_DIR,
            pipelines_dir=request.app.config.PIPELINES_DIR,
        ) as pipeline:
            final_vars = pipeline.run_job(**body.model_dump())
            final_vars = {k: dill.dumps(v) for k, v in final_vars.items()}
        return json(final_vars)
    except Exception as e:
        raise SanicException(str(e))


@bp.post("/add-job/<name>")
@openapi.body({"application/json": PipelineAddJob}, required=False)
@openapi.summary("Add a pipeline as a job")
@openapi.description("Add a pipeline as a job with the given parameters")
# @openapi.response(200, {"application/json": dict[str, str]})
async def add_job(
    request,
    name: str,
):
    body = await deserialize_and_validate(PipelineAddJob, body=request.json)
    try:
        with Pipeline(
            name=name,
            base_dir=request.app.config.BASE_DIR,
            storage_options=request.app.config.STORAGE_OPTIONS,
            cfg_dir=request.app.config.CFG_DIR,
            pipelines_dir=request.app.config.PIPELINES_DIR,
        ) as pipeline:
            id_ = pipeline.add_job(**body.model_dump())
        return json({"job_id": str(id_)})
    except Exception as e:
        raise SanicException(str(e))


@bp.post("/schedule/<name>")
@openapi.body({"application/json": PipelineSchedule}, required=False)
@openapi.summary("Schedule a pipeline")
@openapi.description("Schedule a pipeline with the given parameters")
# @openapi.response(200, {"application/json": dict[str, str]})
async def schedule(
    request,
    name: str,
):

    body = await deserialize_and_validate(PipelineSchedule, body=request.json)

    try:
        with Pipeline(
            base_dir=request.app.config.BASE_DIR,
            storage_options=request.app.config.STORAGE_OPTIONS,
            cfg_dir=request.app.config.CFG_DIR,
            pipelines_dir=request.app.config.PIPELINES_DIR,
        ) as manager:
            id_ = manager.schedule(name, **body.model_dump())
        return json({"schedule_id": str(id_)})
    except Exception as e:
        raise SanicException(str(e))


@bp.patch("/schedule/<name>")
@openapi.body({"application/json": PipelineSchedule}, required=False)
@openapi.summary("Update a pipeline schedule")
@openapi.description("Update a pipeline schedule with the given parameters")
# @openapi.response(200, {"application/json": dict[str, str]})
async def update_schedule(
    request,
    name: str,
):
    overwrite = request.json.pop("overwrite", True)
    body = await deserialize_and_validate(PipelineSchedule, body=request.json)

    try:
        with Pipeline(
            base_dir=request.app.config.BASE_DIR,
            storage_options=request.app.config.STORAGE_OPTIONS,
            cfg_dir=request.app.config.CFG_DIR,
            pipelines_dir=request.app.config.PIPELINES_DIR,
        ) as manager:
            id_ = manager.schedule(name, overwrite=overwrite, **body.model_dump())
        return json({"schedule_id": str(id_)})
    except Exception as e:
        raise SanicException(str(e))


@bp.post("new/<name>")
@openapi.body({"application/json": PipelineManagerNew}, required=False)
@openapi.summary("Create a new pipeline")
@openapi.description("Create a new pipeline with the given parameters")
# @openapi.response(200, {"application/json": dict[str, str]})
async def new(
    request,
    name: str,
):

    body = await deserialize_and_validate(PipelineManagerNew, body=request.json)

    try:
        with PipelineManager(
            base_dir=request.app.config.BASE_DIR,
            storage_options=request.app.config.STORAGE_OPTIONS,
            cfg_dir=request.app.config.CFG_DIR,
            pipelines_dir=request.app.config.PIPELINES_DIR,
        ) as manager:
            manager.new(name, **body.model_dump())
        return json({"status": f"Pipeline {name} created"})
    except Exception as e:
        raise SanicException(str(e))


@bp.post("/import")
@openapi.body({"application/json": PipelineManagerImportExport}, required=True)
@openapi.summary("Import a pipeline")
@openapi.description("Import a pipeline with the given parameters")
# @openapi.response(200, {"application/json": dict[str, str]})
async def import_pipeline(
    request,
):
    name = request.json.pop("name", None)
    names = request.json.pop("names", None)
    path = request.json.pop("path", None)
    body = await deserialize_and_validate(
        PipelineManagerImportExport, body=request.json
    )

    if isinstance(names, str):
        names = names.split(",")
    try:

        with PipelineManager(
            base_dir=request.app.config.BASE_DIR,
            storage_options=request.app.config.STORAGE_OPTIONS,
            cfg_dir=request.app.config.CFG_DIR,
            pipelines_dir=request.app.config.PIPELINES_DIR,
        ) as manager:
            if name:
                manager.import_pipeline(name=name, path=path, **body.model_dump())
                return json({"status": f"Pipeline {name} imported from {path}"})
            elif names:
                manager.import_many(names, path=path, **body.model_dump())
                return json(
                    {"status": f"Pipelines {', '.join(names)} imported from {path}"}
                )
            else:
                manager.import_all(path=path, **body.model_dump())
                return json({"status": f"All pipelines imported from {path}"})

    except Exception as e:
        raise SanicException(str(e))


@bp.post("/export")
@openapi.body({"application/json": PipelineManagerImportExport}, required=True)
@openapi.summary("Export a pipeline")
@openapi.description("Export a pipeline with the given parameters")
# @openapi.response(200, {"application/json": dict[str, str]})
async def export_pipeline(
    request,
):

    path = request.json.pop("path", None)
    name = request.json.pop("name", None)
    names = request.json.pop("names", None)

    body = await deserialize_and_validate(
        PipelineManagerImportExport, body=request.json
    )

    if isinstance(names, str):
        names = names.split(",")
    try:
        with PipelineManager(
            base_dir=request.app.config.BASE_DIR,
            storage_options=request.app.config.STORAGE_OPTIONS,
            cfg_dir=request.app.config.CFG_DIR,
            pipelines_dir=request.app.config.PIPELINES_DIR,
        ) as manager:
            if name:
                manager.export_pipeline(name, path=path, **body.model_dump())
                return json({"status": f"Pipeline {name} exported to {path}"})
            elif names:

                manager.export_many(names, path=path, **body.model_dump())
                return json(
                    {"status": f"Pipelines {', '.join(names)} exported to {path}"}
                )
            else:
                manager.export_all(path=path, **body.model_dump())
                return json({"status": f"All pipelines exported to {path}"})
    except Exception as e:
        raise SanicException(str(e))


@bp.delete("/delete/<name>")
@openapi.body({"application/json": PipelineDelete}, required=False)
@openapi.summary("Delete a pipeline")
@openapi.description("Delete a pipeline with the given parameters")
# @openapi.response(200, {"application/json": dict[str, str]})
async def delete(
    request,
    name: str,
):
    body = await deserialize_and_validate(PipelineDelete, body=request.json)
    try:
        with Pipeline(
            name=name,
            base_dir=request.app.config.BASE_DIR,
            storage_options=request.app.config.STORAGE_OPTIONS,
            cfg_dir=request.app.config.CFG_DIR,
            pipelines_dir=request.app.config.PIPELINES_DIR,
        ) as pipeline:
            pipeline.delete(**body.model_dump())
        return json({"status": f"Pipeline {name} deleted"})
    except Exception as e:
        raise SanicException(str(e))


@bp.get("/summary/<name>")
@openapi.body({"application/json": PipelineManagerSummary}, required=False)
@openapi.summary("Show a pipeline summary")
@openapi.description("Show a pipeline summary with the given parameters")
# @openapi.response(200, {"application/json": dict[str, Any]})
# @openapi.response(200, {"text/html": str})
# @openapi.response(200, {"image/svg": bytes})
async def summary(
    request,
    name: str | None = None,
):

    as_ = request.args.get("as", None)
    if as_ == "html":
        to_html = True
        to_svg = False
    if as_ == "svg":
        to_svg = True
        to_html = False
    else:
        to_html = False
        to_svg = False

    body = await deserialize_and_validate(PipelineManagerSummary, body=request.json)

    try:
        if name == "all":
            with PipelineManager(
                base_dir=request.app.config.BASE_DIR,
                storage_options=request.app.config.STORAGE_OPTIONS,
                cfg_dir=request.app.config.CFG_DIR,
                pipelines_dir=request.app.config.PIPELINES_DIR,
            ) as manager:
                if to_html or to_svg:
                    summary = manager.show_summary(
                        to_html=to_html, to_svg=to_svg, **body.model_dump()
                    )
                summary = manager.get_summary(**body.model_dump())

        else:
            with Pipeline(
                name=name,
                base_dir=request.app.config.BASE_DIR,
                storage_options=request.app.config.STORAGE_OPTIONS,
                cfg_dir=request.app.config.CFG_DIR,
                pipelines_dir=request.app.config.PIPELINES_DIR,
            ) as pipeline:

                summary = pipeline.get_summary(
                    to_html=to_html, to_svg=to_svg, **body.model_dump()
                )
        if to_html:
            return html(summary)
        elif to_svg:
            return raw(summary)
        return json(summary)
    except Exception as e:
        raise SanicException(str(e))


@bp.get("/show/<name>")
# @openapi.parameter({"name": str})
@openapi.summary("Show a pipeline graph")
@openapi.description("Show a pipeline grap with the given parameters")
# @openapi.response(200, {"image/png": bytes})
# @openapi.response(200, {"image/svg": bytes})
async def show(
    request,
    name: str,
):

    format = request.args.get("format", "png")

    try:
        with Pipeline(
            name=name,
            base_dir=request.app.config.BASE_DIR,
            storage_options=request.app.config.STORAGE_OPTIONS,
            cfg_dir=request.app.config.CFG_DIR,
            pipelines_dir=request.app.config.PIPELINES_DIR,
        ) as pipeline:
            pipeline_dag = pipeline.show_dag(raw=True)
        return raw(pipeline_dag.pipe(format))
    except Exception as e:
        raise SanicException(str(e))


@bp.get("/pipelines")
# @openapi.parameter({"show": bool})
# @openapi.parameter({"format": str})
@openapi.summary("List pipelines")
@openapi.description("List pipelines with the given parameters")
# @openapi.response(200, {"application/json": dict[str, Any]})
# @openapi.response(200, {"text/html": str})
# @openapi.response(200, {"image/svg": bytes})
async def pipelines(
    request,
):
    show = request.args.get("show", False)
    format_ = request.args.get("format", "html")
    to_html = format_.lower() == "html"
    to_svg = format_.lower() == "svg"
    try:
        with PipelineManager(
            base_dir=request.app.config.BASE_DIR,
            storage_options=request.app.config.STORAGE_OPTIONS,
            cfg_dir=request.app.config.CFG_DIR,
            pipelines_dir=request.app.config.PIPELINES_DIR,
        ) as manager:
            if show:
                pipelines = manager._all_pipelines(
                    show=True, to_html=to_html, to_svg=to_svg
                )
            else:
                pipelines = manager.list_pipelines()
        if to_html:
            return html(pipelines)
        elif to_svg:
            return raw(pipelines)
        return json(pipelines)
    except Exception as e:
        raise SanicException(str(e))
