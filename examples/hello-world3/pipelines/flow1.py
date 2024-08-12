# FlowerPower pipeline flow1.py
# Created on 2024-08-11 18:31:39


from hamilton.function_modifiers import parameterize
from flowerpower.cfg import Config
from pathlib import Path

PARAMS = Config(Path(__file__).parents[1] / "conf").pipeline_params.flow1
