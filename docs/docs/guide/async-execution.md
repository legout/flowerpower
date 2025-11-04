# Asynchronous Execution

FlowerPower integrates with Hamilton’s asynchronous driver to let you await
pipeline runs inside event loops (e.g., FastAPI, notebooks, asyncio scripts).

This page explains how to use `PipelineManager.run_async`, what the
`RunConfig.async_driver` toggle does, and how async execution parallels the
behaviour of synchronous runs.

## Quick start

```python
import asyncio
from flowerpower.pipeline import PipelineManager

pm = PipelineManager(base_dir='.')

async def run_async_pipeline():
    result = await pm.run_async(
        'hello_world',
        final_vars=['full_greeting'],
    )
    print(result['full_greeting'])

asyncio.run(run_async_pipeline())
```

### With additional modules

You can compose multiple modules in async mode just like sync mode using
`additional_modules`:

```python
async def run_async_composed():
    composed = await pm.run_async(
        'hello_world',
        additional_modules=['pipeline_setup'],
        final_vars=['full_greeting'],
    )
    print(composed['full_greeting'])
```

## RunConfig.async_driver

- `RunConfig.async_driver` controls whether the async driver is used.
- Default behaviour when calling `run_async(...)` is to use the async driver.
- Setting `async_driver=False` raises a `ValueError` – use `pm.run(...)` for
  synchronous execution instead.

```python
from flowerpower.cfg.pipeline.run import RunConfig

# Explicitly opt in (usually not necessary for run_async)
cfg = RunConfig(async_driver=True)
await pm.run_async('hello_world', run_config=cfg)

# Opting out raises an error (use pm.run)
cfg = RunConfig(async_driver=False)
try:
    await pm.run_async('hello_world', run_config=cfg)
except ValueError:
    # Fall back to sync
    pm.run('hello_world')
```

## Parity with synchronous runs

Async runs honour the same flags and behaviours:

- `reload=True` reloads the main and additional modules before executing.
- `log_level` configures logging for the run.
- Adapters and adapter configs are applied the same as in sync mode.

## Requirements

Async execution relies on `hamilton.async_driver`. Ensure your Hamilton version
provides it, and upgrade if necessary:

```bash
pip install -U hamilton
```

## Troubleshooting

| Symptom | Cause | Fix |
| --- | --- | --- |
| `ImportError: hamilton.async_driver` | Hamilton version too old | `pip install -U hamilton` |
| `ValueError: async_driver=False` | Explicit opt-out for async runs | Use `pm.run(...)` for sync or set `async_driver=True` |
| Event loop errors | Running `asyncio.run` inside an active loop | Use a framework’s lifecycle (e.g., FastAPI startup) or `nest_asyncio` in notebooks |

## Related

- [Compose Pipelines With Additional Modules](./additional-modules.md)
- README: “Asynchronous Execution” section

