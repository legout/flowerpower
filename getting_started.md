# Getting Started with FlowerPower

FlowerPower is a Python library for building and managing data pipelines with support for various job queue backends.

## Installation

Install FlowerPower using pip:

```bash
pip install flowerpower
```

## Basic Configuration

Create a basic configuration file `config.yml`:

```yaml
# config.yml
flowerpower:
  job_queue:
    type: rq  # or 'apscheduler'
    backend:
      type: redis
      host: localhost
      port: 6379
```

## Running Your First Pipeline

```python
from flowerpower import Pipeline

# Create a simple pipeline
pipeline = Pipeline("my_first_pipeline")

# Add tasks
@pipeline.task
def load_data():
    return {"data": [1, 2, 3]}

@pipeline.task
def process_data(data):
    return [x * 2 for x in data]

# Run the pipeline
result = pipeline.run()
print(result)
```

## Next Steps

- Explore the [API Documentation]()
- Learn about [Advanced Configuration]()
- Check out [Example Pipelines]()