# FlowerPower pipeline test_123.py
# Created on 2024-11-08 17:28:16


from hamilton.function_modifiers import parameterize
from flowerpower.cfg import Config
from pathlib import Path

PARAMS = Config.load(
    Path(__file__).parents[1], pipeline_name="test_123"
).pipeline.hamilton_func_params
