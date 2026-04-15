PIPELINE_PY_TEMPLATE = """# FlowerPower pipeline {name}.py
# Created on {date}

####################################################################################################
# Import necessary libraries
# NOTE: Remove or comment out imports that are not used in the pipeline

from hamilton.function_modifiers import parameterize, dataloader, datasaver
from hamilton.htypes import Parallelizable, Collect

from pathlib import Path

from flowerpower.cfg import Config

def _resolve_base_dir() -> Path:
    cfg_root = Path("{cfg_dir}") if "{cfg_dir}" else Path(".")
    current = Path(__file__).resolve().parent

    while True:
        if (
            (current / cfg_root / "project.yml").exists()
            or (current / cfg_root / "project.yaml").exists()
        ):
            return current
        if current.parent == current:
            raise RuntimeError("Could not locate project root for pipeline configuration.")
        current = current.parent

####################################################################################################
# Load pipeline parameters. Do not modify this section.

PARAMS = Config.load(
    _resolve_base_dir(),
    pipeline_name="{name}",
    cfg_dir="{cfg_dir}",
    pipelines_dir="{pipelines_dir}",
).pipeline.h_params


####################################################################################################
# Helper functions.
# This functions have to start with an underscore (_).


####################################################################################################
# Pipeline functions

"""

HOOK_TEMPLATE__MQTT_BUILD_CONFIG = '''
def {function_name}(payload: bytes, topic: str) -> dict:
    """
    MQTT hook function to build the configuration for the pipeline.
    This function is called in the on_message callback of the MQTT client.
    The result of this function will be passed to the hamilton builder as the config for the pipeline.
    Args:
        payload (bytes): The payload of the MQTT message.
        topic (str): The topic of the MQTT message.
    Returns:
        dict: The configuration for the pipeline.
    """

    pass
'''
