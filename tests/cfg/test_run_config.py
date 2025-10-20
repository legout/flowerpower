import tempfile
from pathlib import Path
from unittest.mock import Mock

import pytest
import yaml
from fsspec_utils import filesystem

from flowerpower.cfg.pipeline import PipelineConfig
from flowerpower.cfg.pipeline.run import (
    CallbackSpec,
    DEPRECATED_RETRY_FIELDS,
    ExecutorConfig,
    RunConfig,
    WithAdapterConfig,
)
from flowerpower.cfg.pipeline.adapter import AdapterConfig as PipelineAdapterConfig
from flowerpower.cfg.project.adapter import AdapterConfig as ProjectAdapterConfig
from flowerpower.utils.config import RunConfigBuilder


class TestRunConfig:
    """Test cases for RunConfig class."""

    def test_run_config_creation_with_defaults(self):
        """Test RunConfig creation with default values."""
        run_config = RunConfig()
        
        # Check default values
        assert run_config.inputs == {}
        assert run_config.final_vars == []
        assert run_config.config == {}
        assert run_config.cache is False
        assert run_config.executor.type == "threadpool"
        assert run_config.with_adapter.hamilton_tracker is False
        assert run_config.pipeline_adapter_cfg is None
        assert run_config.project_adapter_cfg is None
        assert run_config.adapter is None
        assert run_config.reload is False
        assert run_config.log_level == "INFO"
        assert run_config.max_retries == 3
        assert run_config.retry_delay == 1
        assert run_config.jitter_factor == 0.1
        assert run_config.retry_exceptions == [Exception]
        assert run_config.on_success is None
        assert run_config.on_failure is None

    def test_run_config_creation_with_values(self):
        """Test RunConfig creation with specific values."""
        inputs = {"x": 1, "y": 2}
        final_vars = ["result1", "result2"]
        config = {"param": "value"}
        cache = {"recompute": ["node1"]}
        executor = ExecutorConfig(type="threadpool", max_workers=4)
        with_adapter = WithAdapterConfig(hamilton_tracker=True)
        pipeline_adapter_cfg = PipelineAdapterConfig()
        project_adapter_cfg = ProjectAdapterConfig()
        adapter = {"custom": Mock()}
        retry_exceptions = [ValueError, TypeError]
        on_success = Mock()
        on_failure = Mock()

        run_config = RunConfig(
            inputs=inputs,
            final_vars=final_vars,
            config=config,
            cache=cache,
            executor=executor,
            with_adapter=with_adapter,
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
        assert run_config.executor == executor
        assert run_config.with_adapter == with_adapter
        assert run_config.pipeline_adapter_cfg == pipeline_adapter_cfg
        assert run_config.project_adapter_cfg == project_adapter_cfg
        assert run_config.adapter == adapter
        assert run_config.reload is True
        assert run_config.log_level == "DEBUG"
        assert run_config.max_retries == 3
        assert run_config.retry_delay == 2.0
        assert run_config.jitter_factor == 0.2
        assert run_config.retry_exceptions == retry_exceptions
        assert run_config.on_success.func == on_success
        assert run_config.on_failure.func == on_failure

    def test_run_config_to_dict(self):
        """Test RunConfig to_dict conversion."""
        inputs = {"x": 1}
        final_vars = ["result"]
        config = {"param": "value"}
        executor = ExecutorConfig(type="synchronous")
        
        run_config = RunConfig(
            inputs=inputs,
            final_vars=final_vars,
            config=config,
            executor=executor,
        )
        
        result_dict = run_config.to_dict()
        
        assert result_dict["inputs"] == inputs
        assert result_dict["final_vars"] == final_vars
        assert result_dict["config"] == config
        assert result_dict["executor"]["type"] == "synchronous"
        assert "max_retries" not in result_dict
        assert "retry_delay" not in result_dict
        assert "jitter_factor" not in result_dict
        assert "retry_exceptions" not in result_dict
        assert "retry" in result_dict
        assert result_dict["retry"]["max_retries"] == run_config.retry.max_retries

    def test_run_config_from_dict(self):
        """Test RunConfig from_dict creation."""
        data = {
            "inputs": {"x": 1, "y": 2},
            "final_vars": ["result1", "result2"],
            "config": {"param": "value"},
            "cache": {"recompute": ["node1"]},
            "executor": {"type": "threadpool", "max_workers": 4},
            "with_adapter": {"hamilton_tracker": True},
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
        assert run_config.executor.type == "threadpool"
        assert run_config.executor.max_workers == 4
        assert run_config.with_adapter.hamilton_tracker is True
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
        assert run_config.cache is False
        assert run_config.executor.type == "threadpool"  # Has default
        assert run_config.reload is False
        assert run_config.log_level == "INFO"  # Has default
        assert run_config.max_retries == 3  # Has default

    def test_run_config_warns_on_legacy_retry_fields(self):
        """Using deprecated top-level retry fields should emit a warning."""
        with pytest.warns(DeprecationWarning):
            RunConfig(max_retries=5)


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
        assert run_config.cache is False
        assert run_config.executor.type == "threadpool"
        assert run_config.with_adapter.hamilton_tracker is False
        assert run_config.pipeline_adapter_cfg is None
        assert run_config.project_adapter_cfg is None
        assert run_config.adapter is None
        assert run_config.reload is False
        assert run_config.log_level == "INFO"
        assert run_config.max_retries == 3
        assert run_config.retry_delay == 1
        assert run_config.jitter_factor == 0.1
        assert run_config.retry_exceptions == [Exception]
        assert run_config.on_success is None
        assert run_config.on_failure is None

    def test_builder_fluent_interface(self):
        """Test RunConfigBuilder fluent interface."""
        inputs = {"x": 1, "y": 2}
        final_vars = ["result1", "result2"]
        config = {"param": "value"}
        executor = ExecutorConfig(type="threadpool")
        with_adapter = WithAdapterConfig(hamilton_tracker=True)
        pipeline_adapter_cfg = PipelineAdapterConfig()
        project_adapter_cfg = ProjectAdapterConfig()
        adapter = {"custom": Mock()}
        retry_exceptions = [ValueError, TypeError]
        on_success = Mock()
        on_failure = Mock()

        run_config = (
            RunConfigBuilder()
            .with_inputs(inputs)
            .with_final_vars(final_vars)
            .with_config(config)
            .with_cache(cache={"recompute": ["node1"]})
            .with_executor(executor)
            .with_with_adapter_cfg(with_adapter)
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
        assert run_config.executor == executor
        assert run_config.with_adapter == with_adapter
        assert run_config.pipeline_adapter_cfg == pipeline_adapter_cfg
        assert run_config.project_adapter_cfg == project_adapter_cfg
        assert run_config.adapter == adapter
        assert run_config.reload is True
        assert run_config.log_level == "DEBUG"
        assert run_config.max_retries == 3
        assert run_config.retry_delay == 2.0
        assert run_config.jitter_factor == 0.2
        assert run_config.retry_exceptions == retry_exceptions
        assert run_config.on_success.func == on_success
        assert run_config.on_failure.func == on_failure

    def test_builder_with_dict_executor(self):
        """Test RunConfigBuilder with dictionary executor config."""
        executor_dict = {"type": "threadpool", "max_workers": 4}
        
        run_config = (
            RunConfigBuilder()
            .with_executor(executor_dict)
            .build()
        )
        
        assert run_config.executor.type == "threadpool"
        assert run_config.executor.max_workers == 4

    def test_builder_with_string_executor(self):
        """Test RunConfigBuilder with string executor config."""
        run_config = (
            RunConfigBuilder()
            .with_executor("threadpool")
            .build()
        )
        
        assert run_config.executor.type == "threadpool"

    def test_builder_with_dict_with_adapter(self):
        """Test RunConfigBuilder with dictionary with_adapter config."""
        adapter_dict = {"hamilton_tracker": True, "mlflow": False}
        
        run_config = (
            RunConfigBuilder()
            .with_with_adapter_cfg(adapter_dict)
            .build()
        )
        
        assert run_config.with_adapter.hamilton_tracker is True
        assert run_config.with_adapter.mlflow is False

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
        assert run_config.log_level == "INFO"

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
        assert run_config.max_retries == 3

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


class TestRunConfigPersistence:
    def test_pipeline_save_omits_deprecated_retry_fields(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            fs = filesystem(tmpdir, cached=False, dirfs=True)
            pipeline_cfg = PipelineConfig(
                name="retry-clean",
                run=RunConfig(
                    max_retries=5,
                    retry_delay=2.5,
                    jitter_factor=0.3,
                    retry_exceptions=["ValueError"],
                ),
            )

            pipeline_cfg.save(name="retry-clean", base_dir=tmpdir, fs=fs)

            config_path = Path(tmpdir) / "conf" / "pipelines" / "retry-clean.yml"
            with config_path.open() as fh:
                data = yaml.safe_load(fh)

        run_section = data["run"]
        for field in DEPRECATED_RETRY_FIELDS:
            assert field not in run_section
        assert run_section["retry"]["max_retries"] == 5
        assert run_section["retry"]["retry_delay"] == 2.5
        assert run_section["retry"]["jitter_factor"] == 0.3
        assert run_section["retry"]["retry_exceptions"] == ["ValueError"]

    def test_pipeline_load_migrates_deprecated_retry_fields(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            fs = filesystem(tmpdir, cached=False, dirfs=True)
            pipeline_dir = Path(tmpdir) / "conf" / "pipelines"
            pipeline_dir.mkdir(parents=True)

            legacy_path = pipeline_dir / "legacy.yml"
            with legacy_path.open("w") as fh:
                yaml.safe_dump(
                    {
                        "run": {
                            "max_retries": 7,
                            "retry_delay": 3,
                            "jitter_factor": 0.4,
                            "retry_exceptions": ["TimeoutError"],
                        }
                    },
                    fh,
                )

            pipeline_cfg = PipelineConfig.load(base_dir=tmpdir, name="legacy", fs=fs)

            assert pipeline_cfg.run.retry.max_retries == 7
            assert pytest.approx(pipeline_cfg.run.retry.retry_delay) == 3.0
            assert pipeline_cfg.run.retry.jitter_factor == 0.4
            assert pipeline_cfg.run.retry.retry_exceptions == [TimeoutError]
            assert pipeline_cfg.run.max_retries == 7

            with legacy_path.open() as fh:
                rewritten = yaml.safe_load(fh)

        run_section = rewritten["run"]
        for field in DEPRECATED_RETRY_FIELDS:
            assert field not in run_section
        assert run_section["retry"]["max_retries"] == 7
        assert run_section["retry"]["retry_delay"] == 3.0
        assert run_section["retry"]["jitter_factor"] == 0.4
        assert run_section["retry"]["retry_exceptions"] == ["TimeoutError"]


class TestRetryConfig:
    """Test cases for RetryConfig class."""

    def test_retry_config_to_dict_converts_exceptions_to_strings(self):
        """Test that RetryConfig.to_dict() converts exception classes to their string names."""
        from flowerpower.cfg.pipeline.run import RetryConfig
        
        # Create a RetryConfig with exception classes
        retry_config = RetryConfig(
            max_retries=3,
            retry_delay=1.0,
            jitter_factor=0.1,
            retry_exceptions=[ValueError, TypeError, RuntimeError]  # Exception classes
        )
        
        # Convert to dict
        result = retry_config.to_dict()
        
        # Verify the result
        assert result["max_retries"] == 3
        assert result["retry_delay"] == 1.0
        assert result["jitter_factor"] == 0.1
        assert result["retry_exceptions"] == ["ValueError", "TypeError", "RuntimeError"]
        
        # Ensure all are strings, not exception classes
        assert all(isinstance(exc, str) for exc in result["retry_exceptions"])
        
        # Ensure no class representation artifacts
        assert not any("<class '" in exc for exc in result["retry_exceptions"])

    def test_retry_config_to_dict_handles_string_exceptions(self):
        """Test that RetryConfig.to_dict() preserves known string exceptions as-is."""
        from flowerpower.cfg.pipeline.run import RetryConfig
        
        # Create a RetryConfig with known string exceptions
        retry_config = RetryConfig(
            max_retries=2,
            retry_delay=0.5,
            retry_exceptions=["ValueError", "TypeError"]  # Known string exceptions
        )
        
        # Convert to dict
        result = retry_config.to_dict()
        
        # Verify the result
        assert result["retry_exceptions"] == ["ValueError", "TypeError"]
        assert all(isinstance(exc, str) for exc in result["retry_exceptions"])

    def test_retry_config_to_dict_handles_mixed_exceptions(self):
        """Test that RetryConfig.to_dict() handles mixed string and class exceptions."""
        from flowerpower.cfg.pipeline.run import RetryConfig
        
        # Create a RetryConfig and manually set mixed exceptions
        retry_config = RetryConfig(
            max_retries=1,
            retry_delay=2.0,
            retry_exceptions=[ValueError, "TypeError"]  # Mixed types (known string)
        )
        
        # Convert to dict
        result = retry_config.to_dict()
        
        # Verify the result - should be all strings
        assert result["retry_exceptions"] == ["ValueError", "TypeError"]
        assert all(isinstance(exc, str) for exc in result["retry_exceptions"])
