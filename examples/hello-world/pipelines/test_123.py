# FlowerPower pipeline test_123.py
# Created on 2024-11-08 17:28:16


from pathlib import Path

from hamilton.function_modifiers import parameterize

from flowerpower.cfg import Config

PARAMS = Config.load(
    Path(__file__).parents[1], pipeline_name="test_123"
).pipeline.h_params
