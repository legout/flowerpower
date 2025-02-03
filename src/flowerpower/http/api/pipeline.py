import dill
from sanic import Blueprint, SanicException
from sanic_ext import validate


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

bp = Blueprint("api_flowerpower_pipeline", url_prefix="api/pipeline")


@bp.post("run/<name>")
@validate(json=PipelineRun)
async def run(
    request,
    name: str,
    body: PipelineRun,
):
    try:
        with Pipeline(
            name=name,
            base_dir=request.app.config.BASE_DIR,
            storage_options=request.app.config.STORAGE_OPTIONS,
        ) as pipeline:
            final_vars = pipeline.run(**body.model_dump())

        final_vars = dill.dumps(final_vars)
        # {k: dill.dumps(v) for k, v in final_vars.items()}
        return raw(final_vars)
        # return json({"status": "success", "message": "Pipeline ran successfully"})
    except Exception as e:
        raise SanicException(str(e))


@bp.post("run-job/<name>")
@validate(json=PipelineRun)
async def run_job(
    request,
    name: str,
    body: PipelineRun,
):
    try:
        with Pipeline(
            name=name,
            base_dir=request.app.config.BASE_DIR,
            storage_options=request.app.config.STORAGE_OPTIONS,
        ) as pipeline:
            final_vars = pipeline.run_job(**body.model_dump())
        final_vars = dill.dumps(final_vars)
        return raw(final_vars)
    except Exception as e:
        raise SanicException(str(e))


@bp.post("/add-job/<name>")
@validate(json=PipelineAddJob)
async def add_job(
    request,
    name: str,
    body: PipelineAddJob,
):
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
@validate(json=PipelineSchedule)
async def schedule(
    request,
    name: str,
    body: PipelineSchedule,
):

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
@validate(json=PipelineSchedule)
async def update_schedule(
    request,
    name: str,
    body: PipelineSchedule,
):
    params = body.model_dump()
    params.update({"overwrite": True})

    try:
        with Pipeline(
            base_dir=request.app.config.BASE_DIR,
            storage_options=request.app.config.STORAGE_OPTIONS,
            cfg_dir=request.app.config.CFG_DIR,
            pipelines_dir=request.app.config.PIPELINES_DIR,
        ) as manager:
            id_ = manager.schedule(name, **params)
        return json({"schedule_id": str(id_)})
    except Exception as e:
        raise SanicException(str(e))


@bp.post("new/<name>")
@validate(json=PipelineManagerNew)
async def new(
    request,
    name: str,
    body: PipelineManagerNew,
):

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
@validate(json=PipelineManagerImportExport)
async def import_pipeline(
    request,
    body: PipelineManagerImportExport,
):
    params = body.model_dump()
    name = params.pop("name", None)
    names = params.pop("names", None)
    path = params.pop("path", None)

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
                manager.import_pipeline(name=name, path=path, **params)
                return json({"status": f"Pipeline {name} imported from {path}"})
            elif names:
                manager.import_many(names, path=path, **params)
                return json(
                    {"status": f"Pipelines {', '.join(names)} imported from {path}"}
                )
            else:
                manager.import_all(path=path, **params)
                return json({"status": f"All pipelines imported from {path}"})

    except Exception as e:
        raise SanicException(str(e))


@bp.post("/export")
@validate(json=PipelineManagerImportExport)
async def export_pipeline(
    request,
    body: PipelineManagerImportExport,
):
    params = body.model_dump()
    path = params.pop("path", None)
    name = params.pop("name", None)
    names = params.pop("names", None)

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
                manager.export_pipeline(name, path=path, **params)
                return json({"status": f"Pipeline {name} exported to {path}"})
            elif names:
                manager.export_many(names, path=path, **params)
                return json(
                    {"status": f"Pipelines {', '.join(names)} exported to {path}"}
                )
            else:
                manager.export_all(path=path, **params)
                return json({"status": f"All pipelines exported to {path}"})
    except Exception as e:
        raise SanicException(str(e))


@bp.delete("/delete/<name>")
@validate(json=PipelineDelete)
async def delete(
    request,
    name: str,
    body: PipelineDelete,
):
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
@validate(query=PipelineManagerSummary)
async def summary(
    request,
    query: PipelineManagerSummary,
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
                        to_html=to_html, to_svg=to_svg, **query.model_dump()
                    )
                summary = manager.get_summary(**query.model_dump())

        else:
            with Pipeline(
                name=name,
                base_dir=request.app.config.BASE_DIR,
                storage_options=request.app.config.STORAGE_OPTIONS,
                cfg_dir=request.app.config.CFG_DIR,
                pipelines_dir=request.app.config.PIPELINES_DIR,
            ) as pipeline:

                summary = pipeline.get_summary(
                    to_html=to_html, to_svg=to_svg, **query.model_dump()
                )
        if to_html:
            return html(summary)
        elif to_svg:
            return raw(summary)
        return json(summary)
    except Exception as e:
        raise SanicException(str(e))


@bp.get("/show/<name>")
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
