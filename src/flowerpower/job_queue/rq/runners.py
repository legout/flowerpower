import logging
from typing import Any

from ...cfg import PipelineConfig, ProjectConfig
from ...fs import get_storage_options_and_fs
from ...pipeline import Pipeline

logger = logging.getLogger(__name__)


def run_pipeline_job(
    pipeline_name: str,
    base_dir: str,
    storage_options: dict,
    run_args: dict,
) -> Any:
    """
    Standalone pipeline runner function for execution by RQ workers.
    This function is designed to be picklable and executed in a separate process.
    """
    logger.info(f"Starting pipeline job: {pipeline_name}")

    try:
        # Reconstruct filesystem object from serializable config
        # fs, _ = get_storage_options_and_fs(
        #     base_dir=base_dir,
        #     storage_options=fs_config.get("storage_options"),
        #     fs=None,  # Let get_storage_options_and_fs create the fs object
        # )

        # # Reconstruct configuration objects
        # project_cfg = ProjectConfig.from_dict(project_cfg_dict)
        # pipeline_cfg = PipelineConfig.from_dict(pipeline_cfg_dict)

        # Initialize Pipeline instance within the worker process
        # Pass the reconstructed fs and cfg objects
        pipeline_instance = Pipeline(
            name=pipeline_name,
            base_dir=base_dir,
            storage_options=storage_options,
        )

        # Execute the pipeline's run method with the provided arguments
        result = pipeline_instance.run(**run_args)
        logger.info(f"Pipeline job '{pipeline_name}' completed successfully.")
        return result
    except Exception as e:
        logger.error(f"Pipeline job '{pipeline_name}' failed: {e}", exc_info=True)
        raise  # Re-raise the exception so RQ can mark the job as failed
