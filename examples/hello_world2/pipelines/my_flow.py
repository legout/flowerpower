# FlowerPower pipeline my_flow.py
# Created on 2024-07-03 17:09:30


from hamilton.function_modifiers import parameterize
from flowerpower.cfg import load_pipeline_cfg
from pathlib import Path

PARAMS = load_pipeline_cfg(
    path=str(Path(__file__).parent / "conf"), to_ht=True
).params.my_flow
