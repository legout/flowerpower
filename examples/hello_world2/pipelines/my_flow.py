# FlowerPower pipeline my_flow.py
# Created on 2024-07-03 17:09:30


from hamilton.function_modifiers import parameterize
from flowerpower.cfg import Config
from pathlib import Path

PARAMS = Config(Path(__file__).parents[1]).pipeline_params.my_flow
