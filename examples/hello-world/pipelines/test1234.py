# FlowerPower pipeline test1234.py
# Created on 2024-10-28 09:25:45


from hamilton.function_modifiers import parameterize
from flowerpower.cfg import Config
from pathlib import Path

PARAMS = Config.load(
    Path(__file__).parents[1], pipeline_name="test1234"
).pipeline.hamilton_func_params
