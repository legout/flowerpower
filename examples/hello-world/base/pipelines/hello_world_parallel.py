# FlowerPower pipeline hello_world_parallel.py
# Created on 2025-10-14 02:39:22

####################################################################################################
# Import necessary libraries
# NOTE: Remove or comment out imports that are not used in the pipeline

from hamilton.function_modifiers import parameterize, dataloader, datasaver
from hamilton.htypes import Parallelizable, Collect

from pathlib import Path

from flowerpower.cfg import Config

####################################################################################################
# Load pipeline parameters. Do not modify this section.

PARAMS = Config.load(
    Path(__file__).parents[1], pipeline_name="hello_world_parallel"
).pipeline.h_params


####################################################################################################
# Helper functions.
# This functions have to start with an underscore (_).


####################################################################################################
# Pipeline functions

