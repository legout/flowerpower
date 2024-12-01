import dill
from sanic import Blueprint, SanicException
from sanic.response import json, raw, html

from ...pipeline import Pipeline, PipelineManager

bp = Blueprint("api_flowerpower_pipeline", url_prefix="api/pipeline")


@bp.post("run/<name>")
async def run(
    request,
    name: str,
) -> json:
    kwargs = request.json or {}
    try:
        with Pipeline(
            name=name,
            base_dir=app.conf.BASE_DIR,
            storage_options=app.conf.STORAGE_OPTIONS,
            cfg_dir=app.conf.CFG_DIR,
            pipelines_dir=app.conf.PIPELINES_DIR,
        ) as pipeline:
            final_vars = pipeline.run(**kwargs)

        final_vars = {k: dill.dumps(v) for k, v in final_vars.items()}
        return json(final_vars)
    except Exception as e:
        raise SanicException(str(e))


@bp.post("run-job/<name>")
async def run_job(
    request,
    name: str,
) -> json:
    kwargs = request.json or {}
    try:
        with Pipeline(
            name=name,
            base_dir=app.conf.BASE_DIR,
            storage_options=app.conf.STORAGE_OPTIONS,
            cfg_dir=app.conf.CFG_DIR,
            pipelines_dir=app.conf.PIPELINES_DIR,
        ) as pipeline:
            final_vars = pipeline.run_job(**kwargs)
            final_vars = {k: dill.dumps(v) for k, v in final_vars.items()}
        return json(final_vars)
    except Exception as e:
        raise SanicException(str(e))


@bp.post("/add-job/<name>")
async def add_job(
    request,
    name: str,
) -> json:
    kwargs = request.json or {}
    try:
        with Pipeline(
            name=name,
            base_dir=app.conf.BASE_DIR,
            storage_options=app.conf.STORAGE_OPTIONS,
            cfg_dir=app.conf.CFG_DIR,
            pipelines_dir=app.conf.PIPELINES_DIR,
        ) as pipeline:
            id_ = pipeline.add_job(**kwargs)
        return json({"job_id": str(id_)})
    except Exception as e:
        raise SanicException(str(e))


@bp.post("/schedule/<name>")
async def schedule(
    request,
    name: str,
) -> json:
    kwargs = request.json or {}
    try:
        with Pipeline(
            base_dir=app.conf.BASE_DIR,
            storage_options=app.conf.STORAGE_OPTIONS,
            cfg_dir=app.conf.CFG_DIR,
            pipelines_dir=app.conf.PIPELINES_DIR,
        ) as manager:
            id_ = manager.schedule(name, **kwargs)
        return json({"schedule_id": str(id_)})
    except Exception as e:
        raise SanicException(str(e))


@bp.patch("/schedule/<name>")
async def schedule(
    request,
    name: str,
) -> json:
    kwargs = request.json or {}
    overwrite = kwargs.pop("overwrite", True) or request.args.get("overwrite", True)
    try:
        with Pipeline(
            base_dir=app.conf.BASE_DIR,
            storage_options=app.conf.STORAGE_OPTIONS,
            cfg_dir=app.conf.CFG_DIR,
            pipelines_dir=app.conf.PIPELINES_DIR,
        ) as manager:
            id_ = manager.schedule(name, overwrite=overwrite, **kwargs)
        return json({"schedule_id": str(id_)})
    except Exception as e:
        raise SanicException(str(e))


@bp.post("new/<name>")
async def new(
    request,
    name: str,
) -> json:
    kwargs = request.json or {}
    try:
        with PipelineManager(
            base_dir=app.conf.BASE_DIR,
            storage_options=app.conf.STORAGE_OPTIONS,
            cfg_dir=app.conf.CFG_DIR,
            pipelines_dir=app.conf.PIPELINES_DIR,
        ) as manager:
            manager.new(name, **kwargs)
        return json({"status": f"Pipeline {name} created"})
    except Exception as e:
        raise SanicException(str(e))


@bp.post("/import")
async def import_pipeline(
    request,
) -> json:
    kwargs = request.json or {}
    storage_options = kwargs.pop("storage_options", None)
    path = kwargs.pop("path", None) or request.args.get("path")
    name = kwargs.pop("name", None) or request.args.get("name")
    names = kwargs.pop("names", None) or request.args.get("names") or request.args.getlist("name")
    if isinstance(names, str):
        names = names.split(",")
    try:
        if name:
            with PipelineManager(
                base_dir=app.conf.BASE_DIR,
                storage_options=app.conf.STORAGE_OPTIONS,
                cfg_dir=app.conf.CFG_DIR,
                pipelines_dir=app.conf.PIPELINES_DIR,
            ) as manager:
                manager.import_pipeline(
                    name, path=path, storage_options=storage_options, **kwargs
                )
            return json({"status": f"Pipeline {name} imported from {path}"})
        elif names:
            with PipelineManager(
                base_dir=app.conf.BASE_DIR,
                storage_options=app.conf.STORAGE_OPTIONS,
                cfg_dir=app.conf.CFG_DIR,
                pipelines_dir=app.conf.PIPELINES_DIR,
            ) as manager:
                manager.import_many(
                    names, path=path, storage_options=storage_options, **kwargs
                )
            return json(
                {"status": f"Pipelines {', '.join(names)} imported from {path}"}
            )
        else:
            with PipelineManager(
                base_dir=app.conf.BASE_DIR,
                storage_options=app.conf.STORAGE_OPTIONS,
                cfg_dir=app.conf.CFG_DIR,
                pipelines_dir=app.conf.PIPELINES_DIR,
            ) as manager:
                manager.import_all(path=path, storage_options=storage_options, **kwargs)
            return json({"status": f"All pipelines imported from {path}"})

    except Exception as e:
        raise SanicException(str(e))


@bp.post("/export")
async def export_pipeline(
    request,
) -> json:
    kwargs = request.json or {}
    storage_options = kwargs.pop("storage_options", None)
    path = kwargs.pop("path", None) or request.args.get("path")
    name = kwargs.pop("name", None) or request.args.get("name")
    names = kwargs.pop("names", None) or request.args.get("names") or request.args.getlist("name")
    if isinstance(names, str):
        names = names.split(",")
    try:
        if name:
            with PipelineManager(
                base_dir=app.conf.BASE_DIR,
                storage_options=app.conf.STORAGE_OPTIONS,
                cfg_dir=app.conf.CFG_DIR,
                pipelines_dir=app.conf.PIPELINES_DIR,
            ) as manager:
                manager.export_pipeline(
                    name, path=path, storage_options=storage_options, **kwargs
                )
            return json({"status": f"Pipeline {name} exported to {path}"})
        elif names:
            with PipelineManager(
                base_dir=app.conf.BASE_DIR,
                storage_options=app.conf.STORAGE_OPTIONS,
                cfg_dir=app.conf.CFG_DIR,
                pipelines_dir=app.conf.PIPELINES_DIR,
            ) as manager:
                manager.export_many(
                    names, path=path, storage_options=storage_options, **kwargs
                )
            return json({"status": f"Pipelines {', '.join(names)} exported to {path}"})
        else:
            with PipelineManager(
                base_dir=app.conf.BASE_DIR,
                storage_options=app.conf.STORAGE_OPTIONS,
                cfg_dir=app.conf.CFG_DIR,
                pipelines_dir=app.conf.PIPELINES_DIR,
            ) as manager:
                manager.export_all(path=path, storage_options=storage_options, **kwargs)
            return json({"status": f"All pipelines exported to {path}"})
    except Exception as e:
        raise SanicException(str(e))


@bp.delete("/delete/<name>")
async def delete(
    request,
    name: str,
) -> json:
    cfg = request.json.get("cfg", True) or request.args.get("cfg", True)
    module = request.json.get("module", True) or request.args.get("module", True)
    try:
        with Pipeline(
            name=name,
            base_dir=app.conf.BASE_DIR,
            storage_options=app.conf.STORAGE_OPTIONS,
            cfg_dir=app.conf.CFG_DIR,
            pipelines_dir=app.conf.PIPELINES_DIR,
        ) as pipeline:
            pipeline.delete(cfg=cfg, module=module)
        return json({"status": f"Pipeline {name} deleted"})
    except Exception as e:
        raise SanicException(str(e))


@bp.get("/summary")
async def summary(
    request,
) -> json:
    kwargs = request.json or {}
    name = request.args.get("name")
    to_html = request.args.get("html", False)
    to_svg = request.args.get("svg", False)
    try:
        with PipelineManager(
            base_dir=app.conf.BASE_DIR,
            storage_options=app.conf.STORAGE_OPTIONS,
            cfg_dir=app.conf.CFG_DIR,
            pipelines_dir=app.conf.PIPELINES_DIR,
        ) as manager:
            if to_html:
                summary = manager.show_summary(name=name, to_html=True, **kwargs)
                return html(summary)
            if to_svg:
                summary = manager.show_summary(name=name, to_svg=True, **kwargs)
                return raw(summary)

            summary = manager.get_summary(name=name,**kwargs)

        return json(summary)
    except Exception as e:
        raise SanicException(str(e))


@bp.get("/summary/<name>")
async def summary(
    request,
    name: str | None = None,
) -> json:
    kwargs = request.json or {}
    to_html = request.args.get("html", False)
    to_svg = request.args.get("svg", False)
    try:
        with Pipeline(
            name=name,
            base_dir=app.conf.BASE_DIR,
            storage_options=app.conf.STORAGE_OPTIONS,
            cfg_dir=app.conf.CFG_DIR,
            pipelines_dir=app.conf.PIPELINES_DIR,
        ) as pipeline:
            if to_html:
                summary = pipeline.show_summary(to_html=True, **kwargs)
                return html(summary)
            if to_svg:
                summary = pipeline.show_summary(to_svg=True, **kwargs)
                return raw(summary)
            summary = pipeline.get_summary(**kwargs)

        return json(summary)
    except Exception as e:
        raise SanicException(str(e))

@bp.get("/show/<name>")
async def show(
    request,
    name: str,
) -> json:
    try:
        with Pipeline(
            name=name,
            base_dir=app.conf.BASE_DIR,
            storage_options=app.conf.STORAGE_OPTIONS,
            cfg_dir=app.conf.CFG_DIR,
            pipelines_dir=app.conf.PIPELINES_DIR,
        ) as pipeline:
            pipeline_dag = pipeline.show_dag()
        return raw(pipeline_dag.pipe("svg"))
    except Exception as e:
        raise SanicException(str(e))

@bp.get("/show/<name>")
async def show(
    request,
    name: str,
) -> json:
    try:
        with Pipeline(
            name=name,
            base_dir=app.conf.BASE_DIR,
            storage_options=app.conf.STORAGE_OPTIONS,
            cfg_dir=app.conf.CFG_DIR,
            pipelines_dir=app.conf.PIPELINES_DIR,
        ) as pipeline:
            pipeline_dag = pipeline.show_dag()
        return raw(pipeline_dag.pipe("svg"))
    except Exception as e:
        raise SanicException(str(e))


@bp.get("/pipelines")
async def all_pipelines(
    request,
) -> json:
    try:
        with PipelineManager(
            base_dir=app.conf.BASE_DIR,
            storage_options=app.conf.STORAGE_OPTIONS,
            cfg_dir=app.conf.CFG_DIR,
            pipelines_dir=app.conf.PIPELINES_DIR,
        ) as manager:
            pipelines = manager.list()
        return json(pipelines)
    except Exception as e:
        raise SanicException(str(e))



# @bp.get("/summary")
# async def summary_all(
#     request,
# ) -> json:
#     try:
#         with PipelineManager(
#             base_dir=app.conf.BASE_DIR,
#             storage_options=app.conf.STORAGE_OPTIONS,
#             cfg_dir=app.conf.CFG_DIR,
#             pipelines_dir=app.conf.PIPELINES_DIR,
#         ) as manager:
#             pipelines = manager.get_summary()
#         return json(pipelines)
#     except Exception as e:
#         SanicException(str(e))


# # @bp.get("/summary/<name>")
# # async def summary(
# #     request,
# #     name: str | None = None,
# # ) -> json:
# #     try:
# #     return json({"pipeline": pipeline})


# @bp.post("/run/<name>")
# async def run_(
#     request,
#     name: str,
# ) -> json:
#     kwargs = request.json or {}
#     _ = request.app.ctx.pipeline_manager.run(name, **kwargs)
#     return json({"status": "success"})


# @bp.post("/run-job/<name>")
# async def run_job(
#     request,
#     name: str,
# ) -> json:
#     kwargs = request.json or {}
#     _ = request.app.ctx.pipeline_manager.run_job(name, **kwargs)
#     return json({"status": "success"})


# @bp.post("/schedule/<name>")
# async def schedule_pipeline(request, name):
#     kwargs = request.json or {}
#     id_ = request.app.ctx.pipeline_manager.schedule(name, **kwargs)
#     return json({"schedule_id": str(id_)})


# @bp.post("/start-mqtt-listener/<name>")
# async def start_mqtt_listener(request, name):
#     kwargs = request.json or {}
#     _ = request.app.ctx.pipeline_manager.start_mqtt_listener(name, **kwargs)
#     return json({"status": "success"})


# @bp.post("/stop-mqtt-listener/<name>")
# async def stop_mqtt_listener(request, name):
#     kwargs = request.json or {}
#     _ = request.app.ctx.pipeline_manager.stop_mqtt_listener(name, **kwargs)
#     return json({"status": "success"})


# @bp.get("/show/<name>")
# async def show(
#     request,
#     name: str,
# ) -> json:
#     pipeline_dag = request.app.ctx.pipeline_manager.show_dag(name=name)
#     return raw(pipeline_dag.pipe("svg"))


# @bp.post("/set-abc/<value>")
# async def set_abc(request, value):
#     request.app.ctx.abc = value
#     return json({"status": "success"})
