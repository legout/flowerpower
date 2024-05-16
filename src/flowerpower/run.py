# import typer
from hamilton import driver
from hamilton_sdk import adapters
from loguru import logger

# from hamilton.execution import executors
from .config import load_params

# from .pipelines import *
import importlib


def run(
    pipeline: str, with_tracker: bool = False, project_id: int | None = None
) -> None:
    PARAMS = load_params()

    final_vars = PARAMS.run[pipeline].final_vars
    inputs = PARAMS.run[pipeline].inputs

    if with_tracker:
        if project_id is None:
            raise ValueError(
                "Please provide a project_id if you want to use the tracker"
            )
        tracker = adapters.HamiltonTracker(
            project_id=project_id,
            username="volker.lorrmann@siemens.com",
            dag_name="my_version_of_the_dag",
            tags={"environment": "DEV", "team": "MY_TEAM", "version": "X"},
        )
        module = importlib.import_module(pipeline)

        dr = (
            driver.Builder()
            .with_modules(module)
            .enable_dynamic_execution(allow_experimental_mode=True)
            .with_adapters(tracker)
            .build()
        )
    else:
        dr = (
            driver.Builder()
            .with_modules(eval(pipeline))
            .enable_dynamic_execution(allow_experimental_mode=True)
            .build()
        )

    logger.info(f"Starting pipeline {pipeline}")

    _ = dr.execute(final_vars=final_vars, inputs=inputs)

    logger.success(f"Finished pipeline {pipeline}")


if __name__ == "__main__":
    pass
    # app()
    # run("raw_to_stage1", filesystem="local")
