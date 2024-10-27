# FlowerPower pipeline test1234.py
# Created on 2024-08-17 16:02:09


from hamilton.function_modifiers import parameterize
from flowerpower.cfg import Config
from pathlib import Path

PARAMS = Config(Path(__file__).parents[1]).pipeline_params.test1234
