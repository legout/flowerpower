from pathlib import Path
import runpy


def test_pipeline_only_example_module_loads_named_pipeline_config() -> None:
    globals_dict = runpy.run_path(
        str(Path("examples/pipeline-only-example/pipelines/text_processor.py"))
    )

    params = globals_dict["PARAMS"]
    assert params["input_file"] == "data/sample_texts.txt"
    assert params["chunk_size"] == 1000


def test_web_scraping_example_module_loads_named_pipeline_config() -> None:
    globals_dict = runpy.run_path(
        str(Path("examples/web-scraping-pipeline/pipelines/news_scraper.py"))
    )

    params = globals_dict["PARAMS"]
    assert params["max_concurrent_requests"] == 5
    assert params["output_dir"] == "output"
