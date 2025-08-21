# Pipeline-Only Example

This example demonstrates lightweight FlowerPower usage focusing exclusively on pipeline functionality without job queue dependencies. It's perfect for simple data processing tasks and scenarios where immediate synchronous execution is preferred.

## Prerequisites

- Python 3.11+
- No Redis required
- No job queue setup required

## Quick Start

All commands should be run from the `examples/pipeline-only-example` directory.

### 1. Run Synchronously

Execute the pipeline directly. Ideal for development and testing.

**Using the script:**
```bash
uv run scripts/run_example.py direct
```

**Using the `flowerpower` CLI:**
```bash
uv run flowerpower pipeline run text_processor
```

**Using a Python REPL:**
```python
from flowerpower.flowerpower import FlowerPowerProject
project = FlowerPowerProject.load()
project.run("text_processor")
```

### 2. Run with Different Modes

```bash
# Run with minimal processing operations
uv run scripts/run_example.py simple

# Run with custom processing parameters
uv run scripts/run_example.py custom

# Demonstrate multiple pipeline configurations
uv run scripts/run_example.py demo
```

## Project Structure

```
pipeline-only-example/
├── conf/
│   ├── project.yml             # Project configuration
│   └── pipelines/
│       └── text_processor.yml  # Pipeline configuration
├── data/
│   └── sample_texts.txt        # Sample input data
├── pipelines/
│   └── text_processor.py       # Pipeline implementation
└── scripts/
    └── run_example.py          # Example runner script
```

## Key Components

- **Pipeline Configuration (`conf/pipelines/text_processor.yml`):** Defines parameters for text processing, including input file, chunk size, analysis operations, and filters.
- **Pipeline Implementation (`pipelines/text_processor.py`):** Contains the core text processing logic, including functions for loading text, analyzing content, and generating results.

## Configuration Options

You can customize the pipeline's behavior by editing `conf/pipelines/text_processor.yml`:

- **`input_config`**: Specify input file path and processing chunk size.
- **`processing_config`**: Set analysis operations to perform (word count, sentence count, keyword extraction, sentiment analysis).
- **`filters`**: Configure text filtering options like minimum word count and stopword removal.

## Expected Output

Running the pipeline generates a comprehensive text analysis report including word statistics, sentence analysis, keyword extraction, and sentiment scoring. Results are returned immediately as a structured dictionary.

## Pipeline-Only vs Full FlowerPower

- **Pipeline-Only**: Ideal for simple tasks, development workflows, and scenarios requiring immediate results. No Redis or job queue setup needed.
- **Full FlowerPower**: Better for long-running computations, background processing, and production workloads requiring scaling and scheduling.

## Customizing the Example

- **Add New Operations**: Extend the pipeline with new analysis functions in `pipelines/text_processor.py`.
- **Modify Processing**: Update configuration in `text_processor.yml` to change operations or parameters.
- **Process Different Files**: Modify the input configuration to work with different text files.

## Troubleshooting

- **`FileNotFoundError`**: Ensure you are in the correct directory and the `data/sample_texts.txt` file exists.
- **Import Errors**: Verify FlowerPower is properly installed with core dependencies.
- **Memory Issues**: Reduce `chunk_size` in configuration for large text files.

## Related Examples

- [`data-etl-pipeline`](../data-etl-pipeline/): More complex data processing patterns
- [`job-queue-only-example`](../job-queue-only-example/): Job queue without pipelines
- [`scheduled-reports`](../scheduled-reports/): Combining pipelines with scheduling