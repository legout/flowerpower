import pytest
from unittest.mock import Mock, patch

from flowerpower.cfg.pipeline.run import RunConfig, RunConfigBuilder, ExecutorConfig, WithAdapterConfig
from flowerpower.cfg.pipeline.adapter import AdapterConfig as PipelineAdapterConfig
from flowerpower.cfg.project.adapter import AdapterConfig as ProjectAdapterConfig


class TestRunConfig:
    """Test cases for RunConfig class."""

    def test_run_config_creation_with_defaults(self):
        """Test RunConfig creation with default values."""
        run_config = RunConfig()
        
        # Check default values
        assert run_config.inputs == {}
        assert run_config.final_vars == []
        assert run_config.config == {}
        assert run_config.cache == {}
        assert run_config.executor_cfg is None
        assert run_config.with_adapter_cfg is None
        assert run_config.pipeline_adapter_cfg is None
        assert run_config.project_adapter_cfg is None
        assert run_config.adapter is None
        assert run_config.reload is False
        assert run_config.log_level is None
        assert run_config.max_retries is None
        assert run_config.retry_delay is None
        assert run_config.jitter_factor is None
        assert run_config.retry_exceptions is None
        assert run_config.on_success is None
        assert run_config.on_failure is None

    def test_run_config_creation_with_values(self):
        """Test RunConfig creation with specific values."""
        inputs = {"x": 1, "y": 2}
        final_vars = ["result1", "result2"]
        config = {"param": "value"}
        cache = {"recompute": ["node1"]}
        executor_cfg = ExecutorConfig(type="threadpool", max_workers=4)
        with_adapter_cfg = WithAdapterConfig(hamilton_tracker=True)
        pipeline_adapter_cfg = PipelineAdapterConfig()
        project_adapter_cfg = ProjectAdapterConfig()
        adapter = {"custom": Mock()}
        retry_exceptions = (ValueError, TypeError)
        on_success = Mock()
        on_failure = Mock()

        run_config = RunConfig(
            inputs=inputs,
            final_vars=final_vars,
            config=config,
            cache=cache,
            executor_cfg=executor_cfg,
            with_adapter_cfg=with_adapter_cfg,
            pipeline_adapter_cfg=pipeline_adapter_cfg,
            project_adapter_cfg=project_adapter_cfg,
            adapter=adapter,
            reload=True,
            log_level="DEBUG",
            max_retries=3,
            retry_delay=2.0,
            jitter_factor=0.2,
            retry_exceptions=retry_exceptions,
            on_success=on_success,
            on_failure=on_failure,
        )

        assert run_config.inputs == inputs
        assert run_config.final_vars == final_vars
        assert run_config.config == config
        assert run_config.cache == cache
        assert run_config.executor_cfg == executor_cfg
        assert run_config.with_adapter_cfg == with_adapter_cfg
        assert run_config.pipeline_adapter_cfg == pipeline_adapter_cfg
        assert run_config.project_adapter_cfg == project_adapter_cfg
        assert run_config.adapter == adapter
        assert run_config.reload is True
        assert run_config.log_level == "DEBUG"
        assert run_config.max_retries == 3
        assert run_config.retry_delay == 2.0
        assert run_config.jitter_factor == 0.2
        assert run_config.retry_exceptions == retry_exceptions
        assert run_config.on_success == on_success
        assert run_config.on_failure == on_failure

    def test_run_config_to_dict(self):
        """Test RunConfig to_dict conversion."""
        inputs = {"x": 1}
        final_vars = ["result"]
        config = {"param": "value"}
        executor_cfg = ExecutorConfig(type="synchronous")
        
        run_config = RunConfig(
            inputs=inputs,
            final_vars=final_vars,
            config=config,
            executor_cfg=executor_cfg,
        )
        
        result_dict = run_config.to_dict()
        
        assert result_dict["inputs"] == inputs
        assert result_dict["final_vars"] == final_vars
        assert result_dict["config"] == config
        assert result_dict["executor_cfg"] == executor_cfg.to_dict()

    def test_run_config_from_dict(self):
        """Test RunConfig from_dict creation."""
        data = {
            "inputs": {"x": 1, "y": 2},
            "final_vars": ["result1", "result2"],
            "config": {"param": "value"},
            "cache": {"recompute": ["node1"]},
            "executor_cfg": {"type": "threadpool", "max_workers": 4},
            "with_adapter_cfg": {"hamilton_tracker": True},
            "reload": True,
            "log_level": "DEBUG",
            "max_retries": 3,
            "retry_delay": 2.0,
            "jitter_factor": 0.2,
        }
        
        run_config = RunConfig.from_dict(data)
        
        assert run_config.inputs == {"x": 1, "y": 2}
        assert run_config.final_vars == ["result1", "result2"]
        assert run_config.config == {"param": "value"}
        assert run_config.cache == {"recompute": ["node1"]}
        assert run_config.executor_cfg.type == "threadpool"
        assert run_config.executor_cfg.max_workers == 4
        assert run_config.with_adapter_cfg.hamilton_tracker is True
        assert run_config.reload is True
        assert run_config.log_level == "DEBUG"
        assert run_config.max_retries == 3
        assert run_config.retry_delay == 2.0
        assert run_config.jitter_factor == 0.2

    def test_run_config_from_dict_with_defaults(self):
        """Test RunConfig from_dict with minimal data."""
        data = {"inputs": {"x": 1}}
        
        run_config = RunConfig.from_dict(data)
        
        assert run_config.inputs == {"x": 1}
        assert run_config.final_vars == []
        assert run_config.config == {}
        assert run_config.cache == {}
        assert run_config.executor_cfg is None
        assert run_config.reload is False
        assert run_config.log_level is None
        assert run_config.max_retries is None


class TestRunConfigBuilder:
    """Test cases for RunConfigBuilder class."""

    def test_builder_default_values(self):
        """Test RunConfigBuilder with default values."""
        builder = RunConfigBuilder()
        run_config = builder.build()
        
        # Should match RunConfig defaults
        assert run_config.inputs == {}
        assert run_config.final_vars == []
        assert run_config.config == {}
        assert run_config.cache == {}
        assert run_config.executor_cfg is None
        assert run_config.with_adapter_cfg is None
        assert run_config.pipeline_adapter_cfg is None
        assert run_config.project_adapter_cfg is None
        assert run_config.adapter is None
        assert run_config.reload is False
        assert run_config.log_level is None
        assert run_config.max_retries is None
        assert run_config.retry_delay is None
        assert run_config.jitter_factor is None
        assert run_config.retry_exceptions is None
        assert run_config.on_success is None
        assert run_config.on_failure is None

    def test_builder_fluent_interface(self):
        """Test RunConfigBuilder fluent interface."""
        inputs = {"x": 1, "y": 2}
        final_vars = ["result1", "result2"]
        config = {"param": "value"}
        executor_cfg = ExecutorConfig(type="threadpool")
        with_adapter_cfg = WithAdapterConfig(hamilton_tracker=True)
        pipeline_adapter_cfg = PipelineAdapterConfig()
        project_adapter_cfg = ProjectAdapterConfig()
        adapter = {"custom": Mock()}
        retry_exceptions = (ValueError, TypeError)
        on_success = Mock()
        on_failure = Mock()

        run_config = (
            RunConfigBuilder()
            .with_inputs(inputs)
            .with_final_vars(final_vars)
            .with_config(config)
            .with_cache(cache={"recompute": ["node1"]})
            .with_executor_cfg(executor_cfg)
            .with_with_adapter_cfg(with_adapter_cfg)
            .with_pipeline_adapter_cfg(pipeline_adapter_cfg)
            .with_project_adapter_cfg(project_adapter_cfg)
            .with_adapter(adapter)
            .with_reload(True)
            .with_log_level("DEBUG")
            .with_max_retries(3)
            .with_retry_delay(2.0)
            .with_jitter_factor(0.2)
            .with_retry_exceptions(retry_exceptions)
            .with_on_success(on_success)
            .with_on_failure(on_failure)
            .build()
        )

        assert run_config.inputs == inputs
        assert run_config.final_vars == final_vars
        assert run_config.config == config
        assert run_config.cache == {"recompute": ["node1"]}
        assert run_config.executor_cfg == executor_cfg
        assert run_config.with_adapter_cfg == with_adapter_cfg
        assert run_config.pipeline_adapter_cfg == pipeline_adapter_cfg
        assert run_config.project_adapter_cfg == project_adapter_cfg
        assert run_config.adapter == adapter
        assert run_config.reload is True
        assert run_config.log_level == "DEBUG"
        assert run_config.max_retries == 3
        assert run_config.retry_delay == 2.0
        assert run_config.jitter_factor == 0.2
        assert run_config.retry_exceptions == retry_exceptions
        assert run_config.on_success == on_success
        assert run_config.on_failure == on_failure

    def test_builder_with_dict_executor_cfg(self):
        """Test RunConfigBuilder with dictionary executor config."""
        executor_dict = {"type": "threadpool", "max_workers": 4}
        
        run_config = (
            RunConfigBuilder()
            .with_executor_cfg(executor_dict)
            .build()
        )
        
        assert run_config.executor_cfg.type == "threadpool"
        assert run_config.executor_cfg.max_workers == 4

    def test_builder_with_string_executor_cfg(self):
        """Test RunConfigBuilder with string executor config."""
        run_config = (
            RunConfigBuilder()
            .with_executor_cfg("threadpool")
            .build()
        )
        
        assert run_config.executor_cfg.type == "threadpool"

    def test_builder_with_dict_with_adapter_cfg(self):
        """Test RunConfigBuilder with dictionary with_adapter config."""
        adapter_dict = {"hamilton_tracker": True, "mlflow": False}
        
        run_config = (
            RunConfigBuilder()
            .with_with_adapter_cfg(adapter_dict)
            .build()
        )
        
        assert run_config.with_adapter_cfg.hamilton_tracker is True
        assert run_config.with_adapter_cfg.mlflow is False

    def test_builder_partial_configuration(self):
        """Test RunConfigBuilder with only some fields configured."""
        run_config = (
            RunConfigBuilder()
            .with_inputs({"x": 1})
            .with_final_vars(["result"])
            .with_max_retries(5)
            .build()
        )
        
        assert run_config.inputs == {"x": 1}
        assert run_config.final_vars == ["result"]
        assert run_config.max_retries == 5
        # Other fields should have defaults
        assert run_config.config == {}
        assert run_config.reload is False
        assert run_config.log_level is None

    def test_builder_reset(self):
        """Test RunConfigBuilder reset functionality."""
        builder = RunConfigBuilder()
        
        # Configure some values
        builder.with_inputs({"x": 1}).with_max_retries(3)
        
        # Reset should clear all values
        builder.reset()
        run_config = builder.build()
        
        # Should be back to defaults
        assert run_config.inputs == {}
        assert run_config.max_retries is None

    def test_builder_from_existing_config(self):
        """Test RunConfigBuilder from existing RunConfig."""
        original_config = RunConfig(
            inputs={"x": 1},
            final_vars=["result"],
            max_retries=3,
            log_level="INFO"
        )
        
        # Create builder from existing config
        builder = RunConfigBuilder.from_config(original_config)
        
        # Modify and build new config
        new_config = (
            builder
            .with_max_retries(5)  # Override max_retries
            .with_retry_delay(1.0)  # Add new field
            .build()
        )
        
        # Should preserve original values except where overridden
        assert new_config.inputs == {"x": 1}
        assert new_config.final_vars == ["result"]
        assert new_config.max_retries == 5  # Overridden
        assert new_config.retry_delay == 1.0  # Added
        assert new_config.log_level == "INFO"  # Preserved

    def test_builder_immutability(self):
        """Test that RunConfigBuilder builds immutable configs."""
        builder = RunConfigBuilder()
        run_config1 = builder.with_inputs({"x": 1}).build()
        
        # Modify builder and build again
        run_config2 = builder.with_inputs({"x": 2}).build()
        
        # First config should not be affected
        assert run_config1.inputs == {"x": 1}
        assert run_config2.inputs == {"x": 2}