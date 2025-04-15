class PipelineManager:
    def __init__(
        self,
        base_dir: str | None = None,
        storage_options: dict | Munch | BaseStorageOptions = {},
        fs: AbstractFileSystem | None = None,
        cfg_dir: str = "conf",
        pipelines_dir: str = "pipelines",
        telemetry: bool = True,
        worker_type: str = "apscheduler",  # New parameter for worker backend
    ):
        """
        Initializes the Pipeline object.

        Args:
            base_dir (str | None): The flowerpower base path. Defaults to None.
            storage_options (dict | Munch | BaseStorageOptions, optional): The storage options. Defaults to {}.
            fs (AbstractFileSystem | None, optional): The fsspec filesystem to use. Defaults to None.

        Returns:
            None
        """
        self._telemetry = telemetry
        self._base_dir = base_dir or str(Path.cwd())
        self._storage_options = storage_options or {}
        if fs is None:
            fs = get_filesystem(self._base_dir, **self._storage_options)
        self._fs = fs

        self._cfg_dir = cfg_dir
        self._pipelines_dir = pipelines_dir
        self._worker_type = worker_type  # Store worker_type

        try:
            self._fs.makedirs(f"{self._cfg_dir}/pipelines", exist_ok=True)
            self._fs.makedirs(self._pipelines_dir, exist_ok=True)
        except Exception as e:
            logger.error(f"Error creating directories: {e}")

        self._sync_fs()
        # Load default config only if it exists, avoid error on fresh init
        try:
             self.load_config()
        except FileNotFoundError:
             logger.warning("Default project.yml not found. Skipping initial config load.")
             self.cfg = Munch() # Initialize cfg as empty Munch

    def __enter__(self) -> "PipelineManager":
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        # Add any cleanup code here if needed
        pass

    def _get_schedules(self):
        # TODO: Make worker_type configurable, potentially via self.cfg.project.worker
        with Worker(
            type=self._worker_type,  # Use configured worker_type
            fs=self._fs,
            base_dir=self._base_dir,
            storage_options=self._storage_options,
            # name="schedule_reader" # Optional name
        ) as worker:
            return worker.get_schedules()
    def _sync_fs(self):
        """
        Sync the filesystem.

        Returns:
            None
        """
        if hasattr(self._fs, 'is_cache_fs') and self._fs.is_cache_fs:
            logger.debug(f"Syncing internal filesystem cache: {self._fs}")
            self._fs.sync()

        # Ensure the base pipelines directory is in sys.path relative to the internal fs root
        # This assumes self._fs.path points to the root correctly.
        # If self._fs is abstract, self._fs.path might not be meaningful.
        # A more robust approach might be needed if self._fs isn't a local/simple FS.
        try:
            # Construct path relative to internal fs root
            modules_path_rel = self._pipelines_dir
            # Check if the *absolute* path is in sys.path if fs is local-like
            if hasattr(self._fs, 'path') and not self._fs.path.startswith(self._fs.protocol):
                 modules_path_abs = posixpath.join(self._fs.path, modules_path_rel)
                 if modules_path_abs not in sys.path:
                      logger.debug(f"Adding absolute path to sys.path: {modules_path_abs}")
                      sys.path.append(modules_path_abs)
            # For abstract FS, adding relative path might be necessary if imports rely on it
            # This part is potentially fragile depending on how imports work with abstract FS
            elif modules_path_rel not in sys.path:
                 logger.debug(f"Adding relative path to sys.path: {modules_path_rel}")
                 sys.path.append(modules_path_rel)

        except Exception as e:
             logger.warning(f"Could not reliably add pipelines directory to sys.path: {e}")


    def load_module(self, name: str, reload: bool = False):
        """
        Load a module dynamically.

        Args:
            name (str): The name of the module to load.

        Returns:
            None
        """
        # Ensure pipelines dir is in path before import
        self._sync_fs() # sync_fs now handles adding to sys.path

        module_name = name # Assuming name directly maps to module name

        if not hasattr(self, "_module") or self._module.__name__ != module_name:
             logger.debug(f"Importing module: {module_name}")
             self._module = importlib.import_module(module_name)
        elif reload:
             logger.debug(f"Reloading module: {module_name}")
             self._module = importlib.reload(self._module)
        else:
             logger.debug(f"Module {module_name} already loaded.")


    def load_config(self, name: str | None = None, reload: bool = False):
        """
        Load the configuration file.

        This method loads the configuration file specified by the `_cfg_dir` attribute and
        assigns it to the `cfg` attribute.

        Args:
            name (str | None, optional): The name of the pipeline. Defaults to None (loads project.yml).

        Returns:
            None
        """
        if reload and hasattr(self, 'cfg'):
            del self.cfg
        logger.debug(f"Loading config for pipeline: {name} (reload={reload})")
        self.cfg = Config.load(base_dir=self._base_dir, pipeline_name=name, fs=self._fs)
        logger.debug(f"Config loaded. Project: {self.cfg.project.name}, Pipeline: {getattr(self.cfg.pipeline, 'name', 'N/A')}")


    def _get_driver(
        self,
        name: str,
        executor: str | None = None,
        with_tracker: bool = False,
        with_opentelemetry: bool = False,
        with_progressbar: bool = False,
        config: dict = {},
        reload: bool = False,
        **kwargs,
    ) -> tuple[driver.Driver, Callable | None]:
        """
        Get the driver and shutdown function for a given pipeline.

        Args:
            name (str): The name of the pipeline.
            executor (str | None, optional): The executor to use. Defaults to None.
            with_tracker (bool, optional): Whether to use the tracker. Defaults to False.
            with_opentelemetry (bool, optional): Whether to use OpenTelemetry. Defaults to False.
            with_progressbar (bool, optional): Whether to use a progress bar. Defaults to False.
            config (dict | None, optional): The config for the hamilton driver that executes the pipeline.
                Defaults to None.
            with_opentelemetry (bool, optional): Whether to use OpenTelemetry. Defaults to False.
            reload (bool, optional): Whether to reload the module. Defaults to False.
            **kwargs: Additional keyword arguments.

        Keyword Args:
            max_tasks (int, optional): The maximum number of tasks. Defaults to 20.
            num_cpus (int, optional): The number of CPUs. Defaults to 4.
            project_id (str, optional): The project ID for the tracker. Defaults to None.
            username (str, optional): The username for the tracker. Defaults to None.
            dag_name (str, optional): The DAG name for the tracker. Defaults to None.
            tags (str, optional): The tags for the tracker. Defaults to None.
            api_url (str, optional): The API URL for the tracker. Defaults to None.
            ui_url (str, optional): The UI URL for the tracker. Defaults to None.

        Returns:
            tuple[driver.Driver, Callable | None]: A tuple containing the driver and shutdown function.
        """
        # Ensure config is loaded for the correct pipeline
        if not hasattr(self, 'cfg') or self.cfg.pipeline.name != name or reload:
             logger.debug(f"Loading config for driver build (pipeline: {name}, reload: {reload})")
             self.load_config(name=name, reload=reload)
        # Ensure module is loaded for the correct pipeline
        if not hasattr(self, "_module") or self._module.__name__ != name or reload:
             logger.debug(f"Loading module for driver build (pipeline: {name}, reload: {reload})")
             self.load_module(name=name, reload=reload)

        if self._telemetry:
            disable_telemetry()

        max_tasks = kwargs.pop("max_tasks", 20)
        num_cpus = kwargs.pop("num_cpus", 4)
        executor_, shutdown = get_executor(
            executor or "local", max_tasks=max_tasks, num_cpus=num_cpus
        )
        adapters = []
        if with_tracker:
            # Ensure tracker configs are present
            pipeline_tracker_cfg = getattr(self.cfg.pipeline, 'tracker', Munch())
            project_tracker_cfg = getattr(self.cfg.project, 'tracker', Munch())

            tracker_cfg = {
                **pipeline_tracker_cfg.to_dict(),
                **project_tracker_cfg.to_dict(),
            }
            tracker_kwargs = {
                key: kwargs.pop(key, None) or tracker_cfg.get(key, None)
                for key in tracker_cfg if tracker_cfg.get(key) is not None # Only include non-None values
            }
            # Rename keys for HamiltonTracker
            if "api_url" in tracker_kwargs:
                 tracker_kwargs["hamilton_api_url"] = tracker_kwargs.pop("api_url")
            if "ui_url" in tracker_kwargs:
                 tracker_kwargs["hamilton_ui_url"] = tracker_kwargs.pop("ui_url")

            if tracker_kwargs.get("project_id", None) is None:
                raise ValueError(
                    "Please provide a project_id in project.yml or pipeline config if you want to use the tracker"
                )

            logger.debug(f"Initializing HamiltonTracker with args: {tracker_kwargs}")
            tracker = HamiltonTracker(**tracker_kwargs)
            adapters.append(tracker)

        if with_opentelemetry and h_opentelemetry is not None:
             # Ensure opentelemetry configs are present
             otel_cfg = getattr(self.cfg.project, 'open_telemetry', Munch())
             trace = init_tracer(
                 host=kwargs.pop("host", otel_cfg.get("host", "localhost")),
                 port=kwargs.pop("port", otel_cfg.get("port", 6831)),
                 name=f"{self.cfg.project.name}.{name}",
             )
             if trace:
                  tracer = trace.get_tracer(__name__)
                  adapters.append(h_opentelemetry.OpenTelemetryTracer(tracer=tracer))
             else:
                  logger.warning("OpenTelemetry tracer initialization failed.")


        if with_progressbar:
            adapters.append(h_tqdm.ProgressBar(desc=f"{self.cfg.project.name}.{name}"))

        if executor == "future_adapter":
            adapters.append(FutureAdapter())

        dr = (
            driver.Builder()
            .enable_dynamic_execution(allow_experimental_mode=True)
            .with_modules(self._module)
            .with_config(config or {}) # Ensure config is a dict
            .with_local_executor(executors.SynchronousLocalTaskExecutor())
        )

        if executor_ is not None:
            dr = dr.with_remote_executor(executor_)

        if len(adapters):
            logger.debug(f"Adding adapters to driver: {[type(a).__name__ for a in adapters]}")
            dr = dr.with_adapters(*adapters)

        dr = dr.build()
        return dr, shutdown

    def _prepare_run_params(self, name, inputs, final_vars, config, executor, with_tracker, with_opentelemetry, with_progressbar):
        """Prepares run-related parameters using the run configuration."""
        # Assumes self.cfg is loaded for the correct pipeline 'name' before calling
        if not hasattr(self, 'cfg') or self.cfg.pipeline.name != name:
             self.load_config(name=name) # Load if not loaded or wrong pipeline

        run_config = getattr(self.cfg.pipeline, 'run', Munch()) # Use getattr for safety

        # Merge parameters: method args override config if not None/False
        merged_inputs = inputs if inputs is not None else run_config.get('inputs')
        merged_final_vars = final_vars if final_vars is not None else run_config.get('final_vars')
        merged_config = config if config is not None else run_config.get('config')
        merged_executor = executor if executor is not None else run_config.get('executor')
        # For booleans, method arg takes precedence if True or False, otherwise use config's value (defaulting to False)
        merged_with_tracker = with_tracker if with_tracker is not None else run_config.get('with_tracker', False)
        merged_with_opentelemetry = with_opentelemetry if with_opentelemetry is not None else run_config.get('with_opentelemetry', False)
        merged_with_progressbar = with_progressbar if with_progressbar is not None else run_config.get('with_progressbar', False)


        return {
            'inputs': merged_inputs or {}, # Default to empty dict
            'final_vars': merged_final_vars or [], # Default to empty list
            'config': merged_config or {}, # Default to empty dict
            'executor': merged_executor,
            'with_tracker': merged_with_tracker,
            'with_opentelemetry': merged_with_opentelemetry,
            'with_progressbar': merged_with_progressbar,
        }

    def _prepare_schedule_params(self, name, inputs, final_vars, config, executor, with_tracker, with_opentelemetry, with_progressbar):
        """Prepares run-related parameters specifically for the schedule context."""
        # Assumes self.cfg is loaded for the correct pipeline 'name' before calling
        if not hasattr(self, 'cfg') or self.cfg.pipeline.name != name:
             self.load_config(name=name) # Load if not loaded or wrong pipeline

        schedule_config = getattr(self.cfg.pipeline, 'schedule', Munch())
        schedule_run_config = getattr(schedule_config, 'run', Munch()) # Use getattr for safety

        # Merge parameters: method args override config if not None/False
        merged_inputs = inputs if inputs is not None else schedule_run_config.get('inputs')
        merged_final_vars = final_vars if final_vars is not None else schedule_run_config.get('final_vars')
        merged_config = config if config is not None else schedule_run_config.get('config')
        merged_executor = executor if executor is not None else schedule_run_config.get('executor')
        # For booleans, method arg takes precedence if True or False, otherwise use config's value (defaulting to False)
        merged_with_tracker = with_tracker if with_tracker is not None else schedule_run_config.get('with_tracker', False)
        merged_with_opentelemetry = with_opentelemetry if with_opentelemetry is not None else schedule_run_config.get('with_opentelemetry', False)
        merged_with_progressbar = with_progressbar if with_progressbar is not None else schedule_run_config.get('with_progressbar', False)

        return {
            'inputs': merged_inputs or {}, # Default to empty dict
            'final_vars': merged_final_vars or [], # Default to empty list
            'config': merged_config or {}, # Default to empty dict
            'executor': merged_executor,
            'with_tracker': merged_with_tracker,
            'with_opentelemetry': merged_with_opentelemetry,
            'with_progressbar': merged_with_progressbar,
        }

    # --- Start: New Helper Methods for Import/Export ---
    def _get_pipeline_paths(self, name: str) -> tuple[str, str]:
        """Constructs the relative paths for a pipeline's .py and .yml files."""
        # These paths are relative to the base_dir managed by the fs object
        # Use posixpath for consistent path separators
        py_path = posixpath.join(self._pipelines_dir, f"{name}.py")
        yml_path = posixpath.join(self._cfg_dir, "pipelines", f"{name}.yml")
        return py_path, yml_path

    def _check_pipeline_exists(
        self, fs: AbstractFileSystem, py_path: str, yml_path: str
    ) -> tuple[bool, bool]:
        """Checks if pipeline files exist on the given filesystem using relative paths."""
        # fs.exists() typically works with paths relative to the fs root
        py_exists = fs.exists(py_path)
        yml_exists = fs.exists(yml_path)
        logger.debug(f"Checking existence: py='{py_path}' ({py_exists}), yml='{yml_path}' ({yml_exists}) on fs: {fs}")
        return py_exists, yml_exists

    def _handle_overwrite(
        self, fs: AbstractFileSystem, py_path: str, yml_path: str, overwrite: bool
    ) -> None:
        """
        Handles the overwrite logic for pipeline files on the target filesystem.

        Checks if files exist using relative paths. If they do:
        - Raises ValueError if overwrite is False.
        - Deletes the files if overwrite is True.
        """
        py_exists, yml_exists = self._check_pipeline_exists(fs, py_path, yml_path)

        if py_exists or yml_exists:
            if not overwrite:
                existing = []
                if py_exists:
                    existing.append(py_path)
                if yml_exists:
                    existing.append(yml_path)
                raise ValueError(
                    f"Target pipeline files already exist and overwrite is False: {', '.join(existing)}"
                )
            else:
                logger.warning(f"Overwrite is True. Deleting existing target files:")
                if py_exists:
                    logger.debug(f"Deleting {py_path} on {fs}")
                    fs.rm(py_path)
                if yml_exists:
                    logger.debug(f"Deleting {yml_path} on {fs}")
                    fs.rm(yml_path)
    # --- End: New Helper Methods for Import/Export ---


    def run(
        self,
        name: str,
        inputs: dict | None = None,
        final_vars: list | None = None,
        config: dict | None = None,
        executor: str | None = None,
        with_tracker: bool | None = None,
        with_opentelemetry: bool | None = None,
        with_progressbar: bool | None = None,
        reload: bool = False,
        **kwargs,
    ) -> dict[str, Any]:
        """
        Run the pipeline with the given parameters.

        Args:
            name (str): The name of the pipeline.
            executor (str | None, optional): The executor to use. Defaults to None.
            inputs (dict | None, optional): The inputs for the pipeline. Defaults to None.
            final_vars (list | None, optional): The final variables for the pipeline. Defaults to None.
            config (dict | None, optional): The config for the hamilton driver that executes the pipeline.
                Defaults to None.
            with_tracker (bool | None, optional): Whether to use a tracker. Defaults to None.
            with_opentelemetry (bool | None, optional): Whether to use OpenTelemetry. Defaults to None.
            with_progressbar (bool | None, optional): Whether to use a progress bar. Defaults to None.
            reload (bool, optional): Whether to reload the pipeline. Defaults to False.
            **kwargs: Additional keyword arguments.

        Returns:
            dict[str,Any]: The result of executing the pipeline.

        Examples:
            ```python
            pm = PipelineManager()
            final_vars = pm.run("my_pipeline")
            ```
        """
        if not hasattr(self, 'cfg') or self.cfg.pipeline.name != name or reload:
            self.load_config(name=name, reload=reload)

        if reload or not hasattr(self, "_module") or self._module.__name__ != name:
            self.load_module(name=name, reload=reload)

        logger.info(
            f"Starting pipeline {self.cfg.project.name}.{name}"
        )  # in environment {environment}")

        # Prepare run parameters using the helper
        params = self._prepare_run_params(
            name, inputs, final_vars, config, executor,
            with_tracker, with_opentelemetry, with_progressbar
        )
        # Extract merged parameters
        inputs = params['inputs']
        final_vars = params['final_vars']
        config = params['config']
        executor = params['executor']
        with_tracker = params['with_tracker']
        with_opentelemetry = params['with_opentelemetry']
        with_progressbar = params['with_progressbar']

        # Prepare kwargs for _get_driver, ensuring helper results are used
        driver_kwargs = {
            "executor": executor,
            "with_tracker": with_tracker,
            "with_opentelemetry": with_opentelemetry,
            "with_progressbar": with_progressbar,
            "config": config,
            "reload": reload, # Pass reload status to driver build
            **kwargs # Pass through any other kwargs
        }

        dr, shutdown = self._get_driver(
            name=name,
            **driver_kwargs,
        )

        res = dr.execute(final_vars=final_vars, inputs=inputs)

        logger.success(f"Finished pipeline {self.cfg.project.name}.{name}")

        if shutdown is not None:
            shutdown()

        return res

    def run_job(
        self,
        name: str,
        inputs: dict | None = None,
        final_vars: list | None = None,
        config: dict | None = None,
        executor: str | None = None,
        with_tracker: bool | None = None,
        with_opentelemetry: bool | None = None,
        with_progressbar: bool | None = None,
        reload: bool = False,
        worker_type: str | None = None,  # Allow override
        **kwargs,
    ) -> str:
        """
        Add a job to run the pipeline with the given parameters to the worker queue.
        Returns the job ID. Note: This previously executed immediately and returned results.

        Args:
            name (str): The name of the job (pipeline).
            inputs (dict | None, optional): The inputs for the job. Defaults to None.
            final_vars (list | None, optional): The final variables for the job. Defaults to None.
            config (dict | None, optional): The configuration for the job. Defaults to None.
            executor (str | None, optional): Executor hint (behavior might depend on worker backend). Defaults to None.
            with_tracker (bool | None, optional): Whether to use a tracker for the job. Defaults to None.
            with_opentelemetry (bool | None, optional): Whether to use OpenTelemetry for the job. Defaults to None.
            with_progressbar (bool | None, optional): Whether to use a progress bar for the job. Defaults to None.
            reload (bool, optional): Whether to reload the job module. Defaults to False.
            **kwargs: Additional keyword arguments passed to the pipeline's run method.

        Returns:
            str: The ID of the enqueued job.

        Examples:
            ```python
            pm = PipelineManager()
            final_vars = pm.run_job("my_job")
            ```
        """
        # Removed SchedulerManager check, Worker factory handles backend availability.
        if not hasattr(self, 'cfg') or self.cfg.pipeline.name != name:
             self.load_config(name=name) # Load config for the specific pipeline

        # TODO: Make worker_type configurable
        with Worker(
            type=worker_type or self._worker_type,
            name=f"{self.cfg.project.name}.{name}",
            fs=self._fs,
            base_dir=self._base_dir,
            storage_options=self._storage_options,
        ) as worker:
            # Prepare run parameters using the helper
            params = self._prepare_run_params(
                name, inputs, final_vars, config, executor,
                with_tracker, with_opentelemetry, with_progressbar
            )
            # Update kwargs with merged params and other necessary args for self.run
            run_kwargs = {
                "name": name,
                "inputs": params['inputs'],
                "final_vars": params['final_vars'],
                "config": params['config'],
                "executor": params['executor'],
                "with_tracker": params['with_tracker'],
                "with_opentelemetry": params['with_opentelemetry'],
                "with_progressbar": params['with_progressbar'],
                "reload": reload,
                **kwargs # Include any extra kwargs passed to run_job
            }

            # Note: The execution context is determined by the Worker.
            # We pass the prepared pipeline run parameters via run_kwargs.
            job_id = worker.add_job(
                func=self.run, # Pass the bound method self.run
                kwargs=run_kwargs, # Pass the prepared kwargs
            )
            logger.info(f"Added job '{name}' with ID: {job_id} to worker: {worker_type or self._worker_type}")
            return job_id

    def add_job(
        self,
        name: str,
        inputs: dict | None = None,
        final_vars: list | None = None,
        config: dict | None = None,
        executor: str | None = None,
        with_tracker: bool | None = None,
        with_opentelemetry: bool | None = None,
        with_progressbar: bool | None = None,
        reload: bool = False,
        worker_type: str | None = None,  # Allow override
        **kwargs,
    ) -> str:
        """
        Alias for run_job. Adds a job to the worker queue.

        Args:
            name (str): The name of the job (pipeline).
            inputs (dict | None, optional): The inputs for the job. Defaults to None.
            final_vars (list | None, optional): The final variables for the job. Defaults to None.
            config (dict | None, optional): The configuration for the job. Defaults to None.
            executor (str | None, optional): Executor hint. Defaults to None.
            with_tracker (bool | None, optional): Whether to use a tracker. Defaults to None.
            with_opentelemetry (bool | None, optional): Whether to use OpenTelemetry. Defaults to None.
            with_progressbar (bool | None, optional): Whether to use a progress bar. Defaults to None.
            reload (bool, optional): Whether to reload the job module. Defaults to False.
            **kwargs: Additional keyword arguments passed to the pipeline's run method.

        Returns:
            str: The ID of the enqueued job.
        """
        return self.run_job(
            name=name,
            inputs=inputs,
            final_vars=final_vars,
            config=config,
            executor=executor,
            with_tracker=with_tracker,
            with_opentelemetry=with_opentelemetry,
            with_progressbar=with_progressbar,
            reload=reload,
            worker_type=worker_type,
            **kwargs,
        )


    def schedule(
        self,
        name: str,
        trigger: str | dict,
        inputs: dict | None = None,
        final_vars: list | None = None,
        config: dict | None = None,
        executor: str | None = None,
        with_tracker: bool | None = None,
        with_opentelemetry: bool | None = None,
        with_progressbar: bool | None = None,
        reload: bool = False,
        worker_type: str | None = None,  # Allow override
        **kwargs,
    ) -> str:
        """
        Schedule a pipeline run with the given parameters using the worker.

        Args:
            name (str): The name of the pipeline (job).
            trigger (str | dict): Trigger configuration (e.g., 'cron', 'interval', or dict for specific backend).
            inputs (dict | None, optional): Inputs for the scheduled run. Defaults to None.
            final_vars (list | None, optional): Final variables for the scheduled run. Defaults to None.
            config (dict | None, optional): Configuration for the scheduled run. Defaults to None.
            executor (str | None, optional): Executor hint. Defaults to None.
            with_tracker (bool | None, optional): Whether to use a tracker. Defaults to None.
            with_opentelemetry (bool | None, optional): Whether to use OpenTelemetry. Defaults to None.
            with_progressbar (bool | None, optional): Whether to use a progress bar. Defaults to None.
            reload (bool, optional): Whether to reload the module for each run. Defaults to False.
            worker_type (str | None, optional): Override the default worker type. Defaults to None.
            **kwargs: Additional keyword arguments for the trigger or job.

        Returns:
            str: The ID of the scheduled job.

        Examples:
            ```python
            pm = PipelineManager()
            # Schedule to run every hour
            job_id = pm.schedule("my_pipeline", trigger={'type': 'interval', 'hours': 1})
            # Schedule using cron syntax
            job_id_cron = pm.schedule("my_other_pipeline", trigger={'type': 'cron', 'minute': '0', 'hour': '*/2'})
            ```
        """
        if not hasattr(self, 'cfg') or self.cfg.pipeline.name != name:
             self.load_config(name=name) # Load config for the specific pipeline

        effective_worker_type = worker_type or self._worker_type
        logger.info(f"Scheduling pipeline '{name}' using worker: {effective_worker_type}")

        with Worker(
            type=effective_worker_type,
            name=f"{self.cfg.project.name}.{name}.schedule", # Add suffix for clarity
            fs=self._fs,
            base_dir=self._base_dir,
            storage_options=self._storage_options,
        ) as worker:
            # Prepare run parameters using the schedule-specific helper
            params = self._prepare_schedule_params(
                name, inputs, final_vars, config, executor,
                with_tracker, with_opentelemetry, with_progressbar
            )

            # Prepare kwargs for the self.run function that will be scheduled
            run_kwargs = {
                "name": name,
                "inputs": params['inputs'],
                "final_vars": params['final_vars'],
                "config": params['config'],
                "executor": params['executor'],
                "with_tracker": params['with_tracker'],
                "with_opentelemetry": params['with_opentelemetry'],
                "with_progressbar": params['with_progressbar'],
                "reload": reload,
                # Pass only pipeline run kwargs, not schedule/trigger kwargs
                **{k: v for k, v in kwargs.items() if k not in ['trigger', 'id', 'jobstore', 'replace_existing']}
            }

            # Prepare trigger arguments
            trigger_type = None
            trigger_kwargs = {}
            if isinstance(trigger, str):
                # Basic trigger types like 'date', 'interval', 'cron' might be passed as string
                # But usually, parameters are needed, so dict is preferred.
                # This branch might need refinement based on worker capabilities.
                trigger_type = trigger
                logger.warning(f"Using string trigger '{trigger}'. Dict format is recommended for parameters.")
            elif isinstance(trigger, dict):
                trigger_kwargs = trigger.copy()
                trigger_type = trigger_kwargs.pop('type', None)
                if not trigger_type:
                    raise ValueError("Trigger dictionary must include a 'type' key.")
            else:
                raise TypeError("Trigger must be a string or dictionary.")

            # Generate a unique ID for the schedule if not provided
            # This logic might need adjustment based on how workers handle IDs
            schedule_id = kwargs.pop('id', None)
            if schedule_id is None:
                 # Simple unique ID generation, might need enhancement
                 timestamp = dt.datetime.now().strftime("%Y%m%d%H%M%S%f")
                 schedule_id = f"{name}_schedule_{timestamp}"
                 logger.debug(f"Generated schedule ID: {schedule_id}")


            # Prepare schedule arguments for the worker's add_schedule method
            schedule_kwargs = {
                'id': schedule_id,
                'func': self.run, # Pass the bound method self.run
                'kwargs': run_kwargs,
                'trigger': trigger, # Pass the original trigger dict/str
                'replace_existing': kwargs.get('replace_existing', True), # Default to replace
                # Add other relevant schedule options from kwargs if needed by the worker
                **{k: v for k, v in kwargs.items() if k in ['jobstore', 'misfire_grace_time', 'coalesce', 'max_instances']}
            }


            # Add the schedule using the worker
            id_ = worker.add_schedule(**schedule_kwargs)

            logger.success(
                f"Scheduled job '{name}' with ID: {id_} using trigger: {trigger}"
            )
            return id_


    def schedule_all(
        self,
        worker_type: str | None = None,  # Allow override
        **kwargs,
    ):
        """
        Schedule all pipelines based on their configuration in `conf/pipelines/*.yml`.

        Args:
            worker_type (str | None, optional): Override the default worker type. Defaults to None.
            **kwargs: Additional arguments passed to the `schedule` method for each pipeline
                      (e.g., overwrite behavior for existing schedules).
        """
        scheduled_pipelines = []
        skipped_pipelines = []
        errored_pipelines = []

        pipeline_names = self.list_pipelines()
        logger.info(f"Found {len(pipeline_names)} pipelines to potentially schedule.")

        for name in pipeline_names:
            try:
                # Load config specifically for this pipeline to check schedule settings
                self.load_config(name=name, reload=True)

                if hasattr(self.cfg.pipeline, "schedule") and self.cfg.pipeline.schedule.enabled:
                    trigger_cfg = self.cfg.pipeline.schedule.trigger.to_dict()
                    if not trigger_cfg:
                         logger.warning(f"Pipeline '{name}' schedule enabled but no trigger configured. Skipping.")
                         skipped_pipelines.append(name)
                         continue

                    logger.info(f"Scheduling pipeline '{name}' based on its configuration.")
                    # Use schedule parameters from config, allowing overrides from kwargs
                    # Note: _prepare_schedule_params is used internally by schedule()
                    job_id = self.schedule(
                        name=name,
                        trigger=trigger_cfg, # Pass trigger config directly
                        worker_type=worker_type,
                        # Pass other relevant kwargs like replace_existing
                        **kwargs
                    )
                    scheduled_pipelines.append(f"{name} (ID: {job_id})")
                else:
                    logger.debug(f"Pipeline '{name}' has no schedule configured or is disabled. Skipping.")
                    skipped_pipelines.append(name)

            except Exception as e:
                logger.error(f"Error scheduling pipeline '{name}': {e}")
                errored_pipelines.append(f"{name}: {e}")

        # Report summary
        logger.info("--- Schedule All Summary ---")
        logger.info(f"Successfully scheduled: {len(scheduled_pipelines)}")
        # for p in scheduled_pipelines: logger.info(f"  - {p}")
        logger.info(f"Skipped (no config/disabled): {len(skipped_pipelines)}")
        # for p in skipped_pipelines: logger.info(f"  - {p}")
        logger.error(f"Errors encountered: {len(errored_pipelines)}")
        for p in errored_pipelines: logger.error(f"  - {p}")
        logger.info("--------------------------")


    def new(
        self,
        name: str,
        description: str = "A new pipeline",
        template: str = "default",
        overwrite: bool = False,
        **kwargs,
    ):
        """
        Create a new pipeline from a template.

        Args:
            name (str): The name of the new pipeline.
            description (str, optional): Description for the pipeline config. Defaults to "A new pipeline".
            template (str, optional): The template to use (currently only 'default'). Defaults to "default".
            overwrite (bool, optional): Whether to overwrite existing files. Defaults to False.
            **kwargs: Additional arguments for the pipeline configuration (e.g., schedule, run params).

        Returns:
            None
        """
        logger.info(f"Creating new pipeline '{name}' using template '{template}'")

        py_rel_path, yml_rel_path = self._get_pipeline_paths(name)

        # Handle potential overwrite using the helper method
        # Check relative paths on the internal filesystem
        logger.debug(f"Checking for existing files on internal fs: {self._fs}")
        self._handle_overwrite(self._fs, py_rel_path, yml_rel_path, overwrite)

        # Create directories if they don't exist
        try:
            py_dir = posixpath.dirname(py_rel_path)
            if py_dir and py_dir != '.':
                 logger.debug(f"Ensuring internal directory exists: {py_dir}")
                 self._fs.makedirs(py_dir, exist_ok=True)
            yml_dir = posixpath.dirname(yml_rel_path)
            if yml_dir and yml_dir != '.':
                 logger.debug(f"Ensuring internal directory exists: {yml_dir}")
                 self._fs.makedirs(yml_dir, exist_ok=True)
        except Exception as e:
            logger.error(f"Error creating directories for new pipeline '{name}': {e}")
            raise

        # Create the .py file from template
        if template == "default":
            py_content = PIPELINE_PY_TEMPLATE.format(name=name)
        else:
            # TODO: Add support for more templates if needed
            raise ValueError(f"Unknown template: {template}")

        try:
            logger.info(f"Writing pipeline code to: {py_rel_path}")
            with self._fs.open(py_rel_path, "wb") as f: # Open in binary mode for bytes
                 f.write(py_content.encode('utf-8')) # Encode string to bytes
            logger.debug(f"Successfully wrote {len(py_content)} bytes to {py_rel_path}")
        except Exception as e:
            logger.error(f"Error writing pipeline code file {py_rel_path}: {e}")
            raise

        # Create the .yml configuration file
        # Start with basic structure and update with kwargs
        pipeline_cfg_dict = {
            "name": name,
            "description": description,
            "schedule": {"enabled": False, "trigger": {}}, # Default schedule disabled
            "run": {"final_vars": ["result"]}, # Default run config
            "tracker": {},
            **kwargs # Merge any additional config provided
        }
        # Use PipelineConfig to structure and validate before saving
        try:
             # Create a temporary full config structure for validation
             full_cfg_for_validation = Munch({
                  "project": getattr(self.cfg, 'project', Munch()), # Use existing project cfg or empty
                  "pipeline": pipeline_cfg_dict
             })
             # Validate and structure the pipeline part
             pipeline_config = PipelineConfig(**full_cfg_for_validation)
             # Get the validated pipeline dictionary
             validated_pipeline_dict = pipeline_config.pipeline.toDict() # Use toDict for plain dict

             # Save the validated pipeline config part
             Config.save_pipeline_config(
                 config=validated_pipeline_dict, # Pass the validated pipeline dict
                 pipeline_name=name,
                 fs=self._fs,
                 cfg_dir=self._cfg_dir
             )
             logger.info(f"Writing pipeline configuration to: {yml_rel_path}")
             logger.debug(f"Successfully wrote config for {name}")

        except Exception as e:
            logger.error(f"Error writing pipeline config file {yml_rel_path}: {e}")
            # Clean up the .py file if config writing fails?
            try:
                 if self._fs.exists(py_rel_path):
                      self._fs.rm(py_rel_path)
                      logger.warning(f"Cleaned up partially created file: {py_rel_path}")
            except Exception as cleanup_e:
                 logger.error(f"Error during cleanup of {py_rel_path}: {cleanup_e}")
            raise

        logger.success(f"Successfully created pipeline '{name}'.")
        logger.info(f"  Code: {py_rel_path}")
        logger.info(f"  Config: {yml_rel_path}")


    # --- Refactored Import/Export Methods ---

    def import_pipeline(
        self,
        name: str,
        path: str | None = None, # Changed path to optional
        storage_options: dict | Munch | BaseStorageOptions = {}, # Made storage_options default {}
        fs: AbstractFileSystem | None = None,
        overwrite: bool = False,
        reload: bool = True, # Added reload parameter
        # Removed cfg_dir and pipelines_dir as they come from self
    ):
        """
        Import a pipeline from a given external path/filesystem.

        Args:
            name (str): The name of the pipeline.
            path (str | None, optional): The base path on the external filesystem. Defaults to None.
            storage_options (dict | Munch | BaseStorageOptions, optional): Storage options for the external filesystem. Defaults to {}.
            fs (AbstractFileSystem | None, optional): The external fsspec filesystem to use. If None, created from path/storage_options. Defaults to None.
            overwrite (bool, optional): Whether to overwrite existing files in the internal filesystem. Defaults to False.
            reload (bool, optional): Whether to reload the pipeline config and module after import. Defaults to True.

        Returns:
            None
        """
        # Determine external filesystem
        if fs is None:
            if path is None:
                raise ValueError("Either 'path' or 'fs' must be provided for import.")
            # Use provided storage_options or default from self if empty
            effective_storage_options = storage_options or self._storage_options
            logger.debug(f"Creating external filesystem for path: {path} with options: {effective_storage_options}")
            fs = get_filesystem(path, **effective_storage_options)
        elif path is None:
             # If fs is provided, use its path as the base path if available
             path = getattr(fs, 'path', '') # Use getattr for safety
             logger.debug(f"Using provided external filesystem: {fs}, inferred path: {path}")

        logger.info(f"Starting import of pipeline '{name}' from {path or type(fs).__name__}")

        # Get relative paths based on internal structure (self._pipelines_dir, self._cfg_dir)
        py_rel_path, yml_rel_path = self._get_pipeline_paths(name)
        logger.debug(f"Generated relative paths: py='{py_rel_path}', yml='{yml_rel_path}'")

        # Construct full source paths (on external filesystem)
        # Use posixpath.join which handles potential empty path
        py_path_src = posixpath.join(path or '', py_rel_path)
        yml_path_src = posixpath.join(path or '', yml_rel_path)
        logger.debug(f"Constructed source paths: py='{py_path_src}', yml='{yml_path_src}' on fs={fs}")

        # Destination paths are relative to the internal filesystem's root (self._fs)
        py_path_dst = py_rel_path
        yml_path_dst = yml_rel_path
        logger.debug(f"Destination paths (relative to internal fs): py='{py_path_dst}', yml='{yml_path_dst}' on fs={self._fs}")

        # 1. Check if source files exist on external fs
        logger.debug(f"Checking source files on external fs: {fs}")
        py_exists_src, yml_exists_src = self._check_pipeline_exists(fs, py_path_src, yml_path_src)
        if not py_exists_src:
             raise FileNotFoundError(f"Source pipeline file not found: {py_path_src} on {path or type(fs).__name__}")
        if not yml_exists_src:
             raise FileNotFoundError(f"Source config file not found: {yml_path_src} on {path or type(fs).__name__}")
        logger.debug("Source files exist.")

        # 2. Handle overwrite logic for destination (internal fs)
        logger.debug(f"Handling overwrite check on internal fs: {self._fs}")
        # Pass relative paths to _handle_overwrite as they are relative to self._fs
        self._handle_overwrite(self._fs, py_path_dst, yml_path_dst, overwrite)
        logger.debug("Overwrite check passed.")

        # 3. Ensure destination directories exist on internal fs
        try:
            target_py_dir = posixpath.dirname(py_path_dst)
            if target_py_dir and target_py_dir != '.': # Avoid creating '.' or empty string
                 logger.debug(f"Ensuring internal directory exists: {target_py_dir}")
                 self._fs.makedirs(target_py_dir, exist_ok=True)
            target_yml_dir = posixpath.dirname(yml_path_dst)
            if target_yml_dir and target_yml_dir != '.': # Avoid creating '.' or empty string
                 logger.debug(f"Ensuring internal directory exists: {target_yml_dir}")
                 self._fs.makedirs(target_yml_dir, exist_ok=True)
            logger.debug("Internal target directories ensured.")
        except Exception as e:
            logger.error(f"Error creating target directories on internal fs: {e}")
            raise

        # 4. Copy files from source (external fs) to destination (internal self._fs)
        # Use self._fs.put(external_path, internal_relative_path)
        try:
            logger.info(f"Importing {py_path_src} (from {fs}) to {py_path_dst} (on {self._fs})")
            self._fs.put(py_path_src, py_path_dst)
            logger.debug(f"Successfully copied {py_path_src} to {py_path_dst}")

            logger.info(f"Importing {yml_path_src} (from {fs}) to {yml_path_dst} (on {self._fs})")
            self._fs.put(yml_path_src, yml_path_dst)
            logger.debug(f"Successfully copied {yml_path_src} to {yml_path_dst}")

        except Exception as e:
            # Log the specific paths involved for better debugging
            logger.error(f"Error during file copy for pipeline '{name}': "
                         f"put('{py_path_src}', '{py_path_dst}') or "
                         f"put('{yml_path_src}', '{yml_path_dst}') failed. Error: {e}")
            # Consider adding cleanup logic here if needed.
            raise
        logger.debug("File copy successful.")

        # 5. Sync internal cache filesystem if applicable
        self._sync_fs()

        # 6. Reload config/module if requested
        if reload:
            try:
                logger.info(f"Reloading config and module for pipeline '{name}'")
                self.load_config(name=name, reload=True)
                self.load_module(name=name, reload=True)
                logger.success(f"Pipeline '{name}' imported and reloaded successfully.")
            except Exception as e:
                logger.error(f"Error reloading pipeline '{name}' after import: {e}")
                # Consider implications if reload fails after successful copy.
                raise
        else:
            logger.success(f"Pipeline '{name}' imported successfully (reload skipped).")

        # Use logger instead of rich.print for consistency
        logger.success(f"Import complete for pipeline '{name}' from {path or type(fs).__name__}")


    def import_many(
        self,
        names: list[str],
        path: str | None = None,
        storage_options: dict | Munch | BaseStorageOptions = {},
        fs: AbstractFileSystem | None = None,
        overwrite: bool = False,
        reload: bool = False, # Default to False for many, reload individually if needed
    ):
        """Import multiple pipelines from a given path."""
        logger.info(f"Importing {len(names)} pipelines from {path or type(fs).__name__}")
        success_count = 0
        error_count = 0
        # Create external fs once if path is provided
        if fs is None and path is not None:
             effective_storage_options = storage_options or self._storage_options
             fs = get_filesystem(path, **effective_storage_options)
        elif fs is None and path is None:
             raise ValueError("Either 'path' or 'fs' must be provided for import_many.")

        for name in names:
            try:
                self.import_pipeline(
                    name=name,
                    path=path, # Pass path even if fs is provided for logging clarity
                    storage_options=storage_options, # Pass original options
                    fs=fs, # Pass the potentially pre-created fs
                    overwrite=overwrite,
                    reload=reload, # Use the batch reload flag
                )
                success_count += 1
            except Exception as e:
                logger.error(f"Failed to import pipeline '{name}': {e}")
                error_count += 1

        logger.info(f"Import many summary: {success_count} succeeded, {error_count} failed.")
        if error_count > 0:
             # Optionally raise an error or return status
             pass


    def import_all(
        self,
        path: str | None = None,
        storage_options: dict | Munch | BaseStorageOptions = {},
        fs: AbstractFileSystem | None = None,
        overwrite: bool = False,
        reload: bool = False, # Default to False for all
    ):
        """Import all pipelines found at a given path."""
        # Determine external filesystem
        if fs is None:
            if path is None:
                raise ValueError("Either 'path' or 'fs' must be provided for import_all.")
            effective_storage_options = storage_options or self._storage_options
            fs = get_filesystem(path, **effective_storage_options)
        elif path is None:
             path = getattr(fs, 'path', '')

        logger.info(f"Importing all pipelines from {path or type(fs).__name__}")

        # Discover pipeline .py files on the external filesystem
        # Use the structure defined by self._pipelines_dir relative to the external path
        search_path = posixpath.join(path or '', self._pipelines_dir, "**/*.py")
        try:
             # Use fs.glob which should work relative to the fs root
             # Need to adjust the glob pattern to be relative to fs root
             glob_pattern = posixpath.join(self._pipelines_dir, "**/*.py")
             logger.debug(f"Globbing external fs {fs} with pattern: {glob_pattern}")
             pipeline_files = fs.glob(glob_pattern)
             logger.debug(f"Found potential pipeline files: {pipeline_files}")
        except Exception as e:
             logger.error(f"Error globbing for pipeline files on {fs} with pattern '{glob_pattern}': {e}")
             return

        # Extract names from relative paths
        names = []
        for fn in pipeline_files:
             # fn should be relative to the fs root, e.g., 'pipelines/subdir/my_pipe.py'
             if fn.startswith(self._pipelines_dir + posixpath.sep):
                  name = fn[len(self._pipelines_dir) + 1 : -3] # Remove dir prefix and .py suffix
                  # Replace path separators with dots for module name
                  name = name.replace(posixpath.sep, ".")
                  names.append(name)

        if not names:
             logger.warning(f"No pipeline .py files found in '{posixpath.join(path or '', self._pipelines_dir)}' on {fs}")
             return

        logger.info(f"Found {len(names)} pipelines to import: {names}")

        # Call import_many with discovered names
        self.import_many(
            names=names,
            path=path,
            storage_options=storage_options,
            fs=fs,
            overwrite=overwrite,
            reload=reload,
        )


    def export(
        self,
        name: str,
        path: str | None = None, # Changed path to optional
        storage_options: dict | Munch | BaseStorageOptions = {}, # Made storage_options default {}
        fs: AbstractFileSystem | None = None,
        overwrite: bool = False,
        # Removed cfg_dir and pipelines_dir as they come from self
    ):
        """
        Export a pipeline to a given external path/filesystem.

        Args:
            name (str): The name of the pipeline.
            path (str | None, optional): The base path on the external filesystem. Defaults to None.
            storage_options (dict | Munch | BaseStorageOptions, optional): Storage options for the external filesystem. Defaults to {}.
            fs (AbstractFileSystem | None, optional): The external fsspec filesystem to use. If None, created from path/storage_options. Defaults to None.
            overwrite (bool, optional): Whether to overwrite existing files on the external filesystem. Defaults to False.

        Returns:
            None
        """
        # Determine external filesystem
        if fs is None:
            if path is None:
                raise ValueError("Either 'path' or 'fs' must be provided for export.")
            # Use provided storage_options or default from self if empty
            effective_storage_options = storage_options or self._storage_options
            logger.debug(f"Creating external filesystem for export path: {path} with options: {effective_storage_options}")
            fs = get_filesystem(path, **effective_storage_options)
        elif path is None:
             # If fs is provided, use its path as the base path if available
             path = getattr(fs, 'path', '') # Use getattr for safety
             logger.debug(f"Using provided external filesystem for export: {fs}, inferred path: {path}")


        logger.info(f"Starting export of pipeline '{name}' to {path or type(fs).__name__}")

        # Get relative paths based on internal structure (self._pipelines_dir, self._cfg_dir)
        py_rel_path, yml_rel_path = self._get_pipeline_paths(name)
        logger.debug(f"Generated relative paths: py='{py_rel_path}', yml='{yml_rel_path}'")

        # Source paths are relative to the internal filesystem's root (self._fs)
        py_path_src = py_rel_path
        yml_path_src = yml_rel_path
        logger.debug(f"Source paths (relative to internal fs): py='{py_path_src}', yml='{yml_path_src}' on fs={self._fs}")

        # Construct full destination paths (on external filesystem)
        # Use posixpath.join which handles potential empty path
        py_path_dst = posixpath.join(path or '', py_rel_path)
        yml_path_dst = posixpath.join(path or '', yml_rel_path)
        logger.debug(f"Constructed destination paths: py='{py_path_dst}', yml='{yml_path_dst}' on fs={fs}")

        # 1. Check if source files exist on internal fs
        logger.debug(f"Checking source files on internal fs: {self._fs}")
        # Pass relative paths to _check_pipeline_exists as they are relative to self._fs
        py_exists_src, yml_exists_src = self._check_pipeline_exists(self._fs, py_path_src, yml_path_src)
        if not py_exists_src:
             raise FileNotFoundError(f"Source pipeline file not found: {py_path_src} on internal fs {self._fs}")
        if not yml_exists_src:
             raise FileNotFoundError(f"Source config file not found: {yml_path_src} on internal fs {self._fs}")
        logger.debug("Source files exist.")

        # 2. Handle overwrite logic for destination (external fs)
        logger.debug(f"Handling overwrite check on external fs: {fs}")
        # Pass potentially full destination paths to _handle_overwrite
        self._handle_overwrite(fs, py_path_dst, yml_path_dst, overwrite)
        logger.debug("Overwrite check passed.")

        # 3. Ensure destination directories exist on external fs
        try:
            target_py_dir = posixpath.dirname(py_path_dst)
            if target_py_dir and target_py_dir != '.': # Avoid creating '.' or empty string
                 logger.debug(f"Ensuring external directory exists: {target_py_dir}")
                 fs.makedirs(target_py_dir, exist_ok=True)
            target_yml_dir = posixpath.dirname(yml_path_dst)
            if target_yml_dir and target_yml_dir != '.': # Avoid creating '.' or empty string
                 logger.debug(f"Ensuring external directory exists: {target_yml_dir}")
                 fs.makedirs(target_yml_dir, exist_ok=True)
            logger.debug("External target directories ensured.")
        except Exception as e:
            logger.error(f"Error creating target directories on external fs {fs}: {e}")
            raise

        # 4. Copy files from source (internal self._fs) to destination (external fs)
        # Use fs.put(internal_relative_path, external_path)
        try:
            logger.info(f"Exporting {py_path_src} (from {self._fs}) to {py_path_dst} (on {fs})")
            # Provide the source path relative to self._fs
            fs.put(py_path_src, py_path_dst)
            logger.debug(f"Successfully put {py_path_src} to {py_path_dst}")

            logger.info(f"Exporting {yml_path_src} (from {self._fs}) to {yml_path_dst} (on {fs})")
            # Provide the source path relative to self._fs
            fs.put(yml_path_src, yml_path_dst)
            logger.debug(f"Successfully put {yml_path_src} to {yml_path_dst}")

        except Exception as e:
            # Log the specific paths involved for better debugging
            logger.error(f"Error during file export for pipeline '{name}': "
                         f"put('{py_path_src}', '{py_path_dst}') or "
                         f"put('{yml_path_src}', '{yml_path_dst}') failed. Error: {e}")
            # Consider adding cleanup logic here if needed.
            raise
        logger.debug("File copy successful.")

        # 5. Sync external cache filesystem if applicable
        if hasattr(fs, "sync") and callable(fs.sync) and getattr(fs, 'is_cache_fs', False):
            try:
                logger.debug(f"Syncing external filesystem: {fs}")
                fs.sync()
            except Exception as e:
                logger.warning(f"Could not sync external filesystem {fs}: {e}")

        # Use logger instead of rich.print for consistency
        logger.success(f"Pipeline '{name}' exported successfully to {path or type(fs).__name__}.")


    def export_many(
        self,
        names: list[str],
        path: str | None = None,
        storage_options: dict | Munch | BaseStorageOptions = {},
        fs: AbstractFileSystem | None = None,
        overwrite: bool = False,
    ):
        """Export multiple pipelines to a given path."""
        logger.info(f"Exporting {len(names)} pipelines to {path or type(fs).__name__}")
        success_count = 0
        error_count = 0
        # Create external fs once if path is provided
        if fs is None and path is not None:
             effective_storage_options = storage_options or self._storage_options
             fs = get_filesystem(path, **effective_storage_options)
        elif fs is None and path is None:
             raise ValueError("Either 'path' or 'fs' must be provided for export_many.")

        for name in names:
            try:
                self.export(
                    name=name,
                    path=path,
                    storage_options=storage_options,
                    fs=fs, # Pass the potentially pre-created fs
                    overwrite=overwrite,
                )
                success_count += 1
            except Exception as e:
                logger.error(f"Failed to export pipeline '{name}': {e}")
                error_count += 1

        logger.info(f"Export many summary: {success_count} succeeded, {error_count} failed.")
        if error_count > 0:
             # Optionally raise an error or return status
             pass


    def export_all(
        self,
        path: str | None = None,
        storage_options: dict | Munch | BaseStorageOptions = {},
        fs: AbstractFileSystem | None = None,
        overwrite: bool = False,
    ):
        """Export all pipelines managed by this instance."""
         # Determine external filesystem
        if fs is None:
            if path is None:
                raise ValueError("Either 'path' or 'fs' must be provided for export_all.")
            effective_storage_options = storage_options or self._storage_options
            fs = get_filesystem(path, **effective_storage_options)
        elif path is None:
             path = getattr(fs, 'path', '')

        logger.info(f"Exporting all pipelines to {path or type(fs).__name__}")

        # Get list of pipelines from the internal filesystem
        names = self.list_pipelines()

        if not names:
             logger.warning("No pipelines found in the internal manager to export.")
             return

        logger.info(f"Found {len(names)} pipelines to export: {names}")

        # Call export_many with discovered names
        self.export_many(
            names=names,
            path=path,
            storage_options=storage_options,
            fs=fs,
            overwrite=overwrite,
        )


    def delete(self, name: str, cfg: bool = True, module: bool = False):
        """
        Delete a pipeline's files.

        Args:
            name (str): The name of the pipeline.
            cfg (bool, optional): Whether to delete the configuration file. Defaults to True.
            module (bool, optional): Whether to delete the module file. Defaults to True.

        Returns:
            None
        """
        py_rel_path, yml_rel_path = self._get_pipeline_paths(name)
        deleted_files = []
        skipped_files = []

        if module:
            try:
                if self._fs.exists(py_rel_path):
                    logger.warning(f"Deleting pipeline module file: {py_rel_path}")
                    self._fs.rm(py_rel_path)
                    deleted_files.append(py_rel_path)
                else:
                    logger.debug(f"Pipeline module file not found, skipping delete: {py_rel_path}")
                    skipped_files.append(py_rel_path)
            except Exception as e:
                logger.error(f"Error deleting pipeline module {py_rel_path}: {e}")
        else:
             skipped_files.append(f"{py_rel_path} (module deletion skipped)")


        if cfg:
            try:
                if self._fs.exists(yml_rel_path):
                    logger.warning(f"Deleting pipeline config file: {yml_rel_path}")
                    self._fs.rm(yml_rel_path)
                    deleted_files.append(yml_rel_path)
                else:
                    logger.debug(f"Pipeline config file not found, skipping delete: {yml_rel_path}")
                    skipped_files.append(yml_rel_path)
            except Exception as e:
                logger.error(f"Error deleting pipeline config {yml_rel_path}: {e}")
        else:
            skipped_files.append(f"{yml_rel_path} (config deletion skipped)")


        # Unload module and config if they were loaded for this pipeline
        if hasattr(self, "_module") and self._module.__name__ == name:
             logger.debug(f"Unloading module '{name}' from memory.")
             del self._module
        if hasattr(self, 'cfg') and getattr(self.cfg.pipeline, 'name', None) == name:
             logger.debug(f"Unloading config for '{name}' from memory.")
             # Load default project config back if possible, or clear it
             try:
                  self.load_config(reload=True) # Load project.yml
             except FileNotFoundError:
                  self.cfg = Munch() # Clear config if project.yml doesn't exist


        if deleted_files:
             logger.success(f"Successfully deleted files for pipeline '{name}': {', '.join(deleted_files)}")
        if skipped_files:
             logger.info(f"Skipped deletion for pipeline '{name}': {', '.join(skipped_files)}")


    def _display_all_function(self, name: str, reload: bool = True):
        """Helper to display all functions in a pipeline module."""
        if not hasattr(self, "_module") or self._module.__name__ != name or reload:
            self.load_module(name, reload=reload)
        dr, _ = self._get_driver(name, reload=False) # Use existing loaded module
        dr.display_all_functions()


    def save_dag(
        self,
        name: str,
        path: str | None = None,
        inputs: dict | None = None,
        final_vars: list | None = None,
        config: dict | None = None,
        executor: str | None = None,
        reload: bool = False,
        fmt: str = "png",
        view: bool = False,
        **kwargs,
    ):
        """
        Save the DAG of a pipeline to a file.

        Args:
            name (str): The name of the pipeline.
            path (str | None, optional): The path to save the DAG to. Defaults to None (saves in cwd).
            inputs (dict | None, optional): Inputs for DAG visualization. Defaults to None.
            final_vars (list | None, optional): Final variables for DAG visualization. Defaults to None.
            config (dict | None, optional): Config for DAG visualization. Defaults to None.
            executor (str | None, optional): Executor (not typically used for DAG viz). Defaults to None.
            reload (bool, optional): Whether to reload the pipeline module. Defaults to False.
            fmt (str, optional): The format to save the DAG in (e.g., 'png', 'svg', 'dot'). Defaults to "png".
            view (bool, optional): Whether to view the DAG after saving. Defaults to False.
            **kwargs: Additional arguments for the Hamilton driver's visualize_execution.
        """
        if not hasattr(self, 'cfg') or self.cfg.pipeline.name != name or reload:
             self.load_config(name=name, reload=reload)
        if not hasattr(self, "_module") or self._module.__name__ != name or reload:
             self.load_module(name=name, reload=reload)

        # Prepare run parameters (subset relevant for visualization)
        params = self._prepare_run_params(name, inputs, final_vars, config, executor, False, False, False)
        inputs = params['inputs']
        final_vars = params['final_vars']
        config = params['config']

        dr, shutdown = self._get_driver(
            name=name,
            executor=None, # Executor not needed for viz
            config=config,
            reload=False, # Already loaded
            **kwargs
        )

        output_path = path or f"{name}_dag.{fmt}"

        logger.info(f"Generating DAG for pipeline '{name}' to {output_path} (format: {fmt})")
        dr.visualize_execution(
            final_vars=final_vars,
            inputs=inputs,
            output_file_path=output_path,
            render_kwargs=kwargs.get("render_kwargs", {}),
            graphviz_kwargs=kwargs.get("graphviz_kwargs", {"format": fmt}), # Pass format here
            show_legend=kwargs.get("show_legend", True),
            orient=kwargs.get("orient", "LR"),
            show_inputs=kwargs.get("show_inputs", True),
            show_schema=kwargs.get("show_schema", True),
        )

        if shutdown:
            shutdown()

        logger.success(f"DAG saved to {output_path}")

        if view:
            if fmt == "png":
                 try:
                      view_img(output_path)
                 except Exception as e:
                      logger.error(f"Could not view image {output_path}: {e}")
            else:
                 logger.warning(f"Viewing is only supported for PNG format. Saved as {fmt}.")


    def show_dag(
        self,
        name: str,
        inputs: dict | None = None,
        final_vars: list | None = None,
        config: dict | None = None,
        executor: str | None = None,
        reload: bool = False,
        fmt: str = "png",
        **kwargs,
    ):
        """
        Display the DAG of a pipeline. Currently saves as PNG and attempts to view.

        Args:
            name (str): The name of the pipeline.
            inputs (dict | None, optional): Inputs for DAG visualization. Defaults to None.
            final_vars (list | None, optional): Final variables for DAG visualization. Defaults to None.
            config (dict | None, optional): Config for DAG visualization. Defaults to None.
            executor (str | None, optional): Executor (not typically used for DAG viz). Defaults to None.
            reload (bool, optional): Whether to reload the pipeline module. Defaults to False.
            fmt (str, optional): The format to generate (currently forces PNG for viewing). Defaults to "png".
            **kwargs: Additional arguments for `save_dag`.
        """
        # Force PNG for viewing compatibility with view_img
        if fmt != "png":
             logger.warning(f"Forcing format to 'png' for viewing. Original format was '{fmt}'.")
             fmt = "png"

        # Use save_dag with view=True
        self.save_dag(
            name=name,
            path=None, # Save to default location
            inputs=inputs,
            final_vars=final_vars,
            config=config,
            executor=executor,
            reload=reload,
            fmt=fmt,
            view=True, # Set view=True
            **kwargs,
        )


    def _get_files(self) -> list[str]:
        """List all pipeline-related files (.py and .yml) in the internal filesystem."""
        py_files = self._fs.glob(posixpath.join(self._pipelines_dir, "**/*.py"))
        yml_files = self._fs.glob(posixpath.join(self._cfg_dir, "pipelines", "**/*.yml"))
        return sorted(py_files + yml_files)

    def _get_names(self) -> list[str]:
        """List the names of all pipelines based on .py files in the internal filesystem."""
        py_files = self._fs.glob(posixpath.join(self._pipelines_dir, "**/*.py"))
        # Extract names relative to the pipelines directory
        names = []
        prefix_len = len(self._pipelines_dir) + 1 # +1 for the separator
        for fn in py_files:
             if fn.startswith(self._pipelines_dir + posixpath.sep):
                  name = fn[prefix_len:-3] # Remove dir prefix and .py suffix
                  name = name.replace(posixpath.sep, ".") # Replace path sep with dot
                  names.append(name)
        return sorted(names)


    def get_summary(
        self, name: str, reload: bool = True
    ) -> dict[str, Any]:
        """
        Get a summary of a pipeline including configuration and functions.

        Args:
            name (str): The name of the pipeline.
            reload (bool, optional): Whether to reload the config and module. Defaults to True.

        Returns:
            dict[str, Any]: A dictionary containing the pipeline summary.
        """
        if not hasattr(self, 'cfg') or self.cfg.pipeline.name != name or reload:
             self.load_config(name=name, reload=reload)
        if not hasattr(self, "_module") or self._module.__name__ != name or reload:
             self.load_module(name=name, reload=reload)

        dr, shutdown = self._get_driver(name=name, reload=False) # Use already loaded module/config

        summary = {
            "name": name,
            "description": getattr(self.cfg.pipeline, 'description', 'N/A'),
            "config": self.cfg.pipeline.to_dict(),
            "functions": [f.name for f in dr.list_available_variables()],
            # Add more details as needed, e.g., schedule status
            "schedule_enabled": getattr(self.cfg.pipeline.schedule, 'enabled', False),
            "schedule_trigger": getattr(self.cfg.pipeline.schedule.trigger, 'to_dict', lambda: {})(),
        }
        if shutdown:
             shutdown()
        return summary


    def show_summary(
        self, name: str, reload: bool = True, console: Console | None = None
    ) -> None:
        """
        Display a rich summary of a pipeline.

        Args:
            name (str): The name of the pipeline.
            reload (bool, optional): Whether to reload the config and module. Defaults to True.
            console (Console | None, optional): Rich console instance. Defaults to None.
        """
        _console = console or Console()
        summary_data = self.get_summary(name, reload=reload)

        # Helper to add dictionary items to a Rich Tree
        def add_dict_to_tree(tree: Tree, dict_data: dict, style: str = "green"):
            for key, value in dict_data.items():
                if isinstance(value, dict):
                    branch = tree.add(f"[bold]{key}[/]:", style=style)
                    add_dict_to_tree(branch, value, style=style)
                elif isinstance(value, list):
                     # Display lists more compactly
                     items_str = ", ".join(map(str, value))
                     if len(items_str) > 100: # Truncate long lists
                          items_str = items_str[:100] + "..."
                     tree.add(f"[bold]{key}[/]: [{items_str}]", style=style)
                else:
                    tree.add(f"[bold]{key}[/]: {value}", style=style)

        # Main Panel
        main_panel = Panel(title=f"Pipeline Summary: [bold blue]{name}[/]", expand=False)
        _console.print(main_panel)

        # Configuration Tree
        config_tree = Tree("📋 Configuration", style="bold magenta", guide_style="magenta")
        # Exclude name/description as they are shown elsewhere
        config_to_show = summary_data["config"].copy()
        config_to_show.pop("name", None)
        config_to_show.pop("description", None)
        add_dict_to_tree(config_tree, config_to_show, style="magenta")
        _console.print(config_tree)

        # Functions Panel
        functions_panel = Panel(
             Syntax("\n".join(summary_data["functions"]), "python", theme="default", line_numbers=False),
             title="🐍 Functions",
             border_style="green",
             expand=False
        )
        _console.print(functions_panel)

        # Description Panel (if exists)
        if summary_data["description"] != 'N/A':
             desc_panel = Panel(summary_data["description"], title="📝 Description", border_style="dim")
             _console.print(desc_panel)


    @property
    def summary(self) -> dict[str, dict | str]:
        """Get a summary of all pipelines."""
        return self._all_pipelines()


    def _all_pipelines(
        self,
        display: bool = False,
        reload: bool = True,
        console: Console | None = None,
    ) -> dict[str, dict | str]:
        """
        Internal helper to get or display summaries for all pipelines.

        Args:
            display (bool, optional): Whether to display the summaries. Defaults to False.
            reload (bool, optional): Whether to reload config/modules. Defaults to True.
            console (Console | None, optional): Rich console instance. Defaults to None.

        Returns:
            dict[str, dict | str]: Dictionary of pipeline summaries if display is False.
        """
        _console = console or Console()
        pipeline_names = self.list_pipelines()
        all_summaries = {}

        if not pipeline_names:
             logger.warning("No pipelines found.")
             return {}

        if display:
             _console.print(f"[bold]--- All Pipeline Summaries ({len(pipeline_names)}) ---[/]")

        for name in pipeline_names:
            try:
                summary = self.get_summary(name, reload=reload)
                all_summaries[name] = summary
                if display:
                    self.show_summary(name, reload=False, console=_console) # Don't reload again
                    _console.print("-" * 20) # Separator
            except Exception as e:
                logger.error(f"Error getting summary for pipeline '{name}': {e}")
                all_summaries[name] = {"error": str(e)}
                if display:
                     _console.print(f"[bold red]Error getting summary for '{name}': {e}[/]")
                     _console.print("-" * 20) # Separator

        return all_summaries


    def show_pipelines(self) -> None:
        """Display summaries for all pipelines."""
        self._all_pipelines(display=True, reload=True)


    def list_pipelines(self) -> list[str]:
        """
        List the names of all pipelines found in the configured pipelines directory.

        Returns:
            list[str]: A sorted list of pipeline names.
        """
        return self._get_names()


    @property
    def pipelines(self) -> list[str]:
        """Property to get the list of pipeline names."""
        return self.list_pipelines()


# --- Standalone Functions (using default PipelineManager) ---

# Note: These functions create a default PipelineManager instance on each call.
# For multiple operations, it's more efficient to instantiate PipelineManager once.

def run(
    name: str,
    inputs: dict | None = None,
    final_vars: list | None = None,
    config: dict | None = None,
    executor: str | None = None,
    with_tracker: bool | None = None,
    with_opentelemetry: bool | None = None,
    with_progressbar: bool | None = None,
    reload: bool = False,
    base_dir: str | None = None,
    storage_options: dict | Munch | BaseStorageOptions = {},
    **kwargs,
) -> dict[str, Any]:
    """Standalone function to run a pipeline."""
    with PipelineManager(base_dir=base_dir, storage_options=storage_options) as pm:
        return pm.run(
            name=name,
            inputs=inputs,
            final_vars=final_vars,
            config=config,
            executor=executor,
            with_tracker=with_tracker,
            with_opentelemetry=with_opentelemetry,
            with_progressbar=with_progressbar,
            reload=reload,
            **kwargs,
        )


def run_job(
    name: str,
    inputs: dict | None = None,
    final_vars: list | None = None,
    config: dict | None = None,
    executor: str | None = None,
    with_tracker: bool | None = None,
    with_opentelemetry: bool | None = None,
    with_progressbar: bool | None = None,
    reload: bool = False,
    worker_type: str | None = None,
    base_dir: str | None = None,
    storage_options: dict | Munch | BaseStorageOptions = {},
    **kwargs,
) -> str:
    """Standalone function to add a pipeline run job to the worker queue."""
    with PipelineManager(base_dir=base_dir, storage_options=storage_options) as pm:
        return pm.run_job(
            name=name,
            inputs=inputs,
            final_vars=final_vars,
            config=config,
            executor=executor,
            with_tracker=with_tracker,
            with_opentelemetry=with_opentelemetry,
            with_progressbar=with_progressbar,
            reload=reload,
            worker_type=worker_type,
            **kwargs,
        )


def add_job(
    name: str,
    inputs: dict | None = None,
    final_vars: list | None = None,
    config: dict | None = None,
    executor: str | None = None,
    with_tracker: bool | None = None,
    with_opentelemetry: bool | None = None,
    with_progressbar: bool | None = None,
    reload: bool = False,
    worker_type: str | None = None,
    base_dir: str | None = None,
    storage_options: dict | Munch | BaseStorageOptions = {},
    **kwargs,
) -> str:
    """Standalone alias for run_job."""
    with PipelineManager(base_dir=base_dir, storage_options=storage_options) as pm:
        return pm.add_job(
            name=name,
            inputs=inputs,
            final_vars=final_vars,
            config=config,
            executor=executor,
            with_tracker=with_tracker,
            with_opentelemetry=with_opentelemetry,
            with_progressbar=with_progressbar,
            reload=reload,
            worker_type=worker_type,
            **kwargs,
        )


def schedule(
    name: str,
    trigger: str | dict,
    inputs: dict | None = None,
    final_vars: list | None = None,
    config: dict | None = None,
    executor: str | None = None,
    with_tracker: bool | None = None,
    with_opentelemetry: bool | None = None,
    with_progressbar: bool | None = None,
    reload: bool = False,
    worker_type: str | None = None,
    base_dir: str | None = None,
    storage_options: dict | Munch | BaseStorageOptions = {},
    **kwargs,
) -> str:
    """Standalone function to schedule a pipeline run."""
    with PipelineManager(base_dir=base_dir, storage_options=storage_options) as pm:
        return pm.schedule(
            name=name,
            trigger=trigger,
            inputs=inputs,
            final_vars=final_vars,
            config=config,
            executor=executor,
            with_tracker=with_tracker,
            with_opentelemetry=with_opentelemetry,
            with_progressbar=with_progressbar,
            reload=reload,
            worker_type=worker_type,
            **kwargs,
        )


def new(
    name: str,
    description: str = "A new pipeline",
    template: str = "default",
    overwrite: bool = False,
    base_dir: str | None = None,
    storage_options: dict | Munch | BaseStorageOptions = {},
    **kwargs,
):
    """Standalone function to create a new pipeline."""
    with PipelineManager(base_dir=base_dir, storage_options=storage_options) as pm:
        pm.new(
            name=name,
            description=description,
            template=template,
            overwrite=overwrite,
            **kwargs,
        )


def delete(
    name: str,
    cfg: bool = True,
    module: bool = False,
    base_dir: str | None = None,
    storage_options: dict | Munch | BaseStorageOptions = {},
):
    """Standalone function to delete a pipeline."""
    with PipelineManager(base_dir=base_dir, storage_options=storage_options) as pm:
        pm.delete(name=name, cfg=cfg, module=module)


def save_dag(
    name: str,
    path: str | None = None,
    inputs: dict | None = None,
    final_vars: list | None = None,
    config: dict | None = None,
    executor: str | None = None,
    reload: bool = False,
    fmt: str = "png",
    view: bool = False,
    base_dir: str | None = None,
    storage_options: dict | Munch | BaseStorageOptions = {},
    **kwargs,
):
    """Standalone function to save a pipeline DAG."""
    with PipelineManager(base_dir=base_dir, storage_options=storage_options) as pm:
        pm.save_dag(
            name=name,
            path=path,
            inputs=inputs,
            final_vars=final_vars,
            config=config,
            executor=executor,
            reload=reload,
            fmt=fmt,
            view=view,
            **kwargs,
        )


def show_dag(
    name: str,
    inputs: dict | None = None,
    final_vars: list | None = None,
    config: dict | None = None,
    executor: str | None = None,
    reload: bool = False,
    fmt: str = "png",
    base_dir: str | None = None,
    storage_options: dict | Munch | BaseStorageOptions = {},
    **kwargs,
):
    """Standalone function to show a pipeline DAG."""
    with PipelineManager(base_dir=base_dir, storage_options=storage_options) as pm:
        pm.show_dag(
            name=name,
            inputs=inputs,
            final_vars=final_vars,
            config=config,
            executor=executor,
            reload=reload,
            fmt=fmt,
            **kwargs,
        )


def get_summary(
    name: str,
    reload: bool = True,
    base_dir: str | None = None,
    storage_options: dict | Munch | BaseStorageOptions = {},
) -> dict[str, Any]:
    """Standalone function to get a pipeline summary."""
    with PipelineManager(base_dir=base_dir, storage_options=storage_options) as pm:
        return pm.get_summary(name=name, reload=reload)


def show_summary(
    name: str,
    reload: bool = True,
    base_dir: str | None = None,
    storage_options: dict | Munch | BaseStorageOptions = {},
):
    """Standalone function to show a pipeline summary."""
    with PipelineManager(base_dir=base_dir, storage_options=storage_options) as pm:
        pm.show_summary(name=name, reload=reload)


def show_pipelines(
    base_dir: str | None = None,
    storage_options: dict | Munch | BaseStorageOptions = {},
):
    """Standalone function to show all pipeline summaries."""
    with PipelineManager(base_dir=base_dir, storage_options=storage_options) as pm:
        pm.show_pipelines()


def list_pipelines(
    base_dir: str | None = None,
    storage_options: dict | Munch | BaseStorageOptions = {},
) -> list[str]:
    """Standalone function to list all pipeline names."""
    with PipelineManager(base_dir=base_dir, storage_options=storage_options) as pm:
        return pm.list_pipelines()

# --- Deprecated Pipeline Class ---
# Keep for backward compatibility for now, but log warnings.
# Consider removing in a future version.

class Pipeline(PipelineManager):
     def __init__(self, *args, **kwargs):
          logger.warning("The 'Pipeline' class is deprecated and will be removed in a future version. Please use 'PipelineManager' instead.")
          super().__init__(*args, **kwargs)