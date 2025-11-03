# Compose Pipelines With Additional Modules

FlowerPower extends Hamilton’s ability to compose DAGs across multiple Python
modules. This guide walks through when and how to use the
`additional_modules` argument, how module resolution works, and what to watch
out for when you split a pipeline into reusable building blocks.

## Why split pipelines?

- **Shared setup** – initialise databases, secrets, or clients once and reuse
  them in multiple pipelines.
- **Team ownership** – keep domain-specific logic in separate modules while
  still orchestrating a single DAG.
- **Iterative development** – experiment with new nodes alongside the existing
  pipeline without touching the production module.

The official `examples/hello-world/pipelines/` folder includes both
`hello_world.py` and a companion `setup.py`; the snippets below mirror that
structure.

## Quick start

```python
from flowerpower import FlowerPowerProject

project = FlowerPowerProject.load('.')

result = project.run(
    'hello_world',
    additional_modules=['pipeline_setup'],
    final_vars=['full_greeting'],
)
print(result['full_greeting'])
```

The same pattern works with `PipelineManager`:

```python
from flowerpower.pipeline import PipelineManager

pm = PipelineManager(base_dir='.')
composed = pm.run(
    name='hello_world',
    additional_modules=['pipeline_setup'],
    final_vars=['full_greeting'],
)
```

## Module resolution rules

When strings are provided, FlowerPower tries to match them in this order:

1. Import the string exactly as given (`importlib.import_module(value)`).
2. Import the value with hyphens replaced by underscores (e.g. `data-setup`
   → `data_setup`).
3. Import from the `pipelines` package (e.g. `pipelines.data_setup`).

Already-imported module objects can be mixed with strings in the
`additional_modules` list.

> **Tip:** Keep the list ordered. Hamilton resolves conflicting node names by
> using the last module passed to `.with_modules(...)`. FlowerPower appends the
> main pipeline module after everything in `additional_modules`, so it wins
> ties by default.

## Reload behaviour

Setting `reload=True` on the `RunConfig` (or passing `reload=True` to
`pm.run(...)`) reloads every module in the composed list before execution. This
mirrors Hamilton’s behaviour and is especially helpful during local
development.

```python
pm.run(
    'hello_world',
    additional_modules=['pipeline_setup'],
    reload=True,
)
```

## Visualising composed DAGs

The visualiser accepts the same flag, letting you inspect the combined graph:

```python
pm.visualizer.save_dag(
    name='hello_world',
    base_dir='.',
    additional_modules=['pipeline_setup'],
)

pm.visualizer.show_dag(
    name='hello_world',
    additional_modules=['pipeline_setup'],
    raw=False,
)
```

## Troubleshooting

| Symptom | Cause | Fix |
| --- | --- | --- |
| `ImportError: Could not import additional module` | Module string cannot be resolved | Ensure the module is on `PYTHONPATH` or lives in the `pipelines/` folder. Use dotted paths for nested modules. |
| Unexpected node value | Same node defined in multiple modules | Reorder `additional_modules` so the desired version is last, or rename the node. |
| Changes not reflected | Modules cached by Python | Use `reload=True` during iterative development. |

## Related reading

- Repository README – section “Compose Pipelines With Additional Modules” for a
  concise quick-start.
- Example modules: `examples/hello-world/pipelines/hello_world.py` and
  `examples/hello-world/pipelines/setup.py`
