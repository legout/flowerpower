# Examples

The FlowerPower repository includes ready-to-run example projects that demonstrate common pipeline patterns. You can find them in the [`examples/`](https://github.com/legout/flowerpower/tree/main/examples) directory on GitHub.

## `hello-world/`

The canonical starter project. It defines a minimal `hello_world` pipeline in `pipelines/hello_world.py` and pairs it with a `setup.py` companion module. The companion module is loaded as an `additional_module`, so it shows how to split a pipeline into a main DAG and shared helper code.

## `data-etl-pipeline/`

Demonstrates a configuration-driven ETL workflow: loading a raw CSV, validating the data, cleaning it, and producing a summary report. Use it to see how `params` and `run.config` can change pipeline behavior without editing code.

## `ml-training-pipeline/`

Shows an end-to-end machine-learning workflow covering data preprocessing, feature engineering, model training, and evaluation. It illustrates how a Hamilton DAG maps cleanly onto ML stages and how model artifacts can be saved from a pipeline run.

## `pipeline-only-example/`

A lightweight project that uses FlowerPower's core pipeline features with no optional extras. It is useful when you want a small, self-contained DAG that runs synchronously without additional infrastructure.

## `web-scraping-pipeline/`

Demonstrates concurrent web scraping and content processing as a FlowerPower pipeline. It covers parallel HTTP requests, rate-limiting configuration, and structured content extraction.
