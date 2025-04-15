import time
import logging
import sys
import typer
from enum import Enum
from typing import Optional
from typing_extensions import Annotated # Use typing_extensions for compatibility
from pathlib import Path

# add examples to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
#print(sys.path)

# Assume flowerpower is installed in the environment
try:
    from flowerpower.worker import Worker, BaseBackend
    from flowerpower.worker.rq import RQBackend
    #from flowerpower.worker.huey import 
    from flowerpower.worker.apscheduler import APSBackend
    # Import trigger types if scheduling examples are needed and implemented
    # from flowerpower.worker.apscheduler.trigger import IntervalTrigger as APSIntervalTrigger
    # from flowerpower.worker.huey.trigger import HueyIntervalTrigger
    # from flowerpower.worker.rq.trigger import ... # If RQ triggers exist
except ImportError as e:
    print(f"Error importing flowerpower: {e}")
    print("Ensure flowerpower is installed in your Python environment (e.g., pip install .)")
    sys.exit(1)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define a simple task function
def simple_task(message: str):
    """A simple task that logs a message."""
    logging.info(f"Executing task: {message}")
    time.sleep(2) # Simulate work
    result = f"Task completed: {message}"
    logging.info(result)
    return result

# Define worker choices using Enum for Typer
class WorkerChoice(str, Enum):
    apscheduler = "apscheduler"
    rq = "rq"
    huey = "huey"

# Create a Typer app
app = typer.Typer(help="Run FlowerPower worker examples with configurable backends.")
from worker_example import simple_task

@app.command()
def main(
    worker_type: Annotated[
        WorkerChoice,
        typer.Argument(..., help="Specify the worker backend type.")
    ],
    backend_host: Annotated[Optional[str], typer.Option(help="Backend host (e.g., localhost, IP address).")] = None,
    backend_port: Annotated[Optional[int], typer.Option(help="Backend port number.")] = None,
    backend_db: Annotated[Optional[str], typer.Option(help="Backend database name or number (e.g., 0 for Redis, dbname for SQL).")] = None,
    backend_user: Annotated[Optional[str], typer.Option(help="Backend username.")] = None,
    backend_password: Annotated[Optional[str], typer.Option("--password", help="Backend password. Can also use BACKEND_PASSWORD env var.", envvar="BACKEND_PASSWORD", show_default=False)] = None,
    backend_ssl: Annotated[bool, typer.Option(help="Enable SSL/TLS for backend connection.")] = False,
    backend_uri: Annotated[Optional[str], typer.Option(help="Full backend URI (e.g., redis://user:pass@host:port/db). Overrides other backend options if provided.")] = None,
):
    """
    Run a FlowerPower worker example using the specified backend and connection details.

    Examples:

    - Run RQ worker with default Redis (localhost:6379/0):
      python examples/workers/worker_example.py rq

    - Run Huey worker connecting to a specific Redis instance:
      python examples/workers/worker_example.py huey --backend-host my-redis.server --backend-port 6380 --backend-db 1

    - Run APScheduler with PostgreSQL backend using URI:
      python examples/workers/worker_example.py apscheduler --backend-uri postgresql+asyncpg://user:pass@host:port/db?ssl=verify-full

    - Run RQ worker with Redis password from environment variable:
      export BACKEND_PASSWORD='your_redis_password'
      python examples/workers/worker_example.py rq --backend-host localhost
    """
    logging.info(f"Selected worker type: {worker_type.value}")

    # --- Worker Instantiation ---
    worker_instance = None
    backend = None
    try:
        # Construct backend configuration if options are provided
        backend_kwargs = {
            "host": backend_host,
            "port": backend_port,
            "database": backend_db,
            "username": backend_user,
            "password": backend_password,
            "ssl": backend_ssl,
            "uri": backend_uri, # Add URI here
        }
        # Filter out None values so BaseBackend uses defaults where appropriate
        filtered_backend_kwargs = {k: v for k, v in backend_kwargs.items() if v is not None}

        if filtered_backend_kwargs:
            logging.info(f"Configuring backend with provided options: { {k:v for k,v in filtered_backend_kwargs.items() if k != 'password'} }") # Log options except password
            # If URI is provided, it takes precedence
            if backend_uri:
                if worker_type.value == WorkerChoice.rq:
                    backend = RQBackend(type="redis", uri=backend_uri)
                    logging.warning("RQ backend does not support URI format. Using provided host/port/db instead.")
                elif worker_type.value == WorkerChoice.huey:
                    backend = HueyBackend(type="redis", uri=backend_uri)
                    logging.warning("RQ backend does not support URI format. Using provided host/port/db instead.")
                else:
                    backend = APSBackend(type="postgresql", uri=backend_uri)
                    logging.warning("RQ backend does not support URI format. Using provided host/port/db instead.")
                    
            else:
                if worker_type.value == WorkerChoice.rq:
                    backend = RQBackend(type="redis", **filtered_backend_kwargs)
                elif worker_type.value == WorkerChoice.huey:
                    backend = HueyBackend(type="redis", **filtered_backend_kwargs)

        else:
            logging.info("Using default backend configuration for the worker type (likely memory or default Redis).")

        logging.info("Instantiating worker...")
        # Pass backend_type always, and backend object if configured
        worker_instance = Worker(
            name=f"{worker_type.value}_example_worker",
            backend_type=worker_type.value,
            backend=backend # Pass the configured BaseBackend object if created
        )
        logging.info(f"Worker instance created: {type(worker_instance)}")
        if backend and backend.uri:
             # Be careful logging URIs if they contain sensitive info not handled by filtering above
             logging.info(f"Worker configured with backend URI: {backend.uri.split('@')[-1] if '@' in backend.uri else backend.uri}") # Avoid logging credentials in URI

        # --- Example 1: Add a one-off job ---
        logging.info("Adding one-off job...")
        job_id = worker_instance.add_job(simple_task, args=("Hello from one-off job!",), id="one_off_hello")
        logging.info(f"Added one-off job with ID: {job_id}")

        # --- Example 2: Add a scheduled job (Optional - Requires Triggers) ---
        # (Scheduling example code remains commented out as before)
        # ...

        # --- Start the worker ---
        logging.info("Starting worker in foreground... Press Ctrl+C to stop.")
        worker_instance.start_worker(background=False)

    except ValueError as e:
        logging.error(f"Configuration or Value Error: {e}", exc_info=True)
    except ImportError as e:
        logging.error(f"Import Error: {e}. Make sure backend dependencies are installed (e.g., pip install flowerpower[rq,huey,apscheduler])", exc_info=True)
    except ConnectionError as e:
         logging.error(f"Connection Error: {e}. Is the backend running and accessible with provided config?", exc_info=True)
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}", exc_info=True)
    finally:
        # --- Cleanup ---
        if worker_instance and hasattr(worker_instance, 'stop_worker'):
            logging.info("Stopping worker...")
            try:
                worker_instance.stop_worker()
                logging.info("Worker stopped.")
            except Exception as e:
                logging.error(f"Error stopping worker: {e}", exc_info=True)

if __name__ == "__main__":
    app()