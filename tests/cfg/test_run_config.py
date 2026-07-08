import tempfile
import warnings
from pathlib import Path
from types import ModuleType
from unittest.mock import Mock

import pytest
import yaml
from fsspeckit import filesystem

from flowerpower.cfg.pipeline import PipelineConfig
from flowerpower.cfg.pipeline.run import (
    DEPRECATED_RETRY_FIELDS,
    CallbackSpec,
    ExecutorConfig,
    RetryConfig,
    RunConfig,
    WithAdapterConfig,
)
from flowerpower.cfg.pipeline.adapter import AdapterConfig as PipelineAdapterConfig
from flowerpower.cfg.project.adapter import AdapterConfig as ProjectAdapterConfig
from flowerpower.utils.config import (
    RunConfigBuilder,
    merge_run_config_with_kwargs,
    merge_run_configs,
    validate_resolved_run_config,
)
from flowerpower.utils.security import SecurityError


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
        assert run_config.additional_modules is None
        assert run_config.async_driver is None
        assert run_config.async_driver is None

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
        additional_modules = ["setup", ModuleType("custom_mod")]

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
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
                additional_modules=additional_modules,
                async_driver=True,
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
        assert run_config.additional_modules[0] == "setup"
        assert run_config.additional_modules[1].__name__ == "custom_mod"
        assert run_config.async_driver is True

    def test_run_config_to_dict(self):
        """Test RunConfig to_dict conversion."""
        inputs = {"x": 1}
        final_vars = ["result"]
        config = {"param": "value"}
        executor = ExecutorConfig(type="synchronous")
        
        extra_module = ModuleType("setup")
        run_config = RunConfig(
            inputs=inputs,
            final_vars=final_vars,
            config=config,
            executor=executor,
            additional_modules=["setup", extra_module],
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
        assert result_dict["additional_modules"] == ["setup", "setup"]
        assert "async_driver" not in result_dict

    def test_run_config_to_dict_includes_async_driver_when_set(self):
        run_config = RunConfig(async_driver=True)
        result_dict = run_config.to_dict()
        assert result_dict["async_driver"] is True

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
        
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
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
        assert run_config.async_driver is None

    def test_nested_retry_wins_over_flat_fields_in_constructor(self):
        """Nested retry config takes precedence over deprecated flat fields."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            run_config = RunConfig(
                retry=RetryConfig(max_retries=5, retry_delay=2.0, jitter_factor=0.3),
                max_retries=3,
                retry_delay=1.0,
                jitter_factor=0.1,
            )
        assert run_config.retry.max_retries == 5
        assert run_config.retry.retry_delay == 2.0
        assert run_config.retry.jitter_factor == 0.3

    def test_nested_retry_wins_over_flat_fields_in_from_dict(self):
        """A nested retry block wins over deprecated top-level fields from a dict."""
        data = {
            "retry": {"max_retries": 5, "retry_delay": 2.0, "jitter_factor": 0.3},
            "max_retries": 3,
            "retry_delay": 1.0,
            "jitter_factor": 0.1,
        }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            run_config = RunConfig.from_dict(data)
        assert run_config.retry.max_retries == 5
        assert run_config.retry.retry_delay == 2.0
        assert run_config.retry.jitter_factor == 0.3

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
        assert run_config.additional_modules is None

    def test_builder_with_additional_modules(self):
        builder = RunConfigBuilder()
        module_obj = ModuleType("builder_mod")

        builder.with_additional_modules(["setup"])
        builder.with_additional_modules([module_obj, "setup"])

        run_config = builder.build()

        assert run_config.additional_modules[0] == "setup"
        assert run_config.additional_modules[1] is module_obj
        assert len(run_config.additional_modules) == 2

    def test_builder_with_async_driver_toggle(self):
        builder = RunConfigBuilder()
        builder.with_async_driver(True)
        run_config = builder.build()
        assert run_config.async_driver is True

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

    def test_builder_immutability_for_nested_retry_config(self):
        """Built configs should not share nested retry state with the builder."""
        builder = RunConfigBuilder().with_retry_config(max_retries=1, retry_delay=2.0)
        run_config1 = builder.build()

        builder.with_retry_delay(99.0)
        run_config2 = builder.build()

        assert run_config1.retry.retry_delay == 2.0
        assert run_config2.retry.retry_delay == 99.0

    def test_builder_copies_mutable_inputs_from_caller(self):
        """Builder should not retain references to caller-owned mutable inputs."""
        inputs = {"x": 1}
        final_vars = ["result"]
        adapter = {"custom": Mock()}

        builder = (
            RunConfigBuilder()
            .with_inputs(inputs)
            .with_final_vars(final_vars)
            .with_adapter(adapter)
        )

        inputs["x"] = 2
        final_vars.append("other")
        adapter["extra"] = Mock()

        run_config = builder.build()

        assert run_config.inputs == {"x": 1}
        assert run_config.final_vars == ["result"]
        assert list(run_config.adapter) == ["custom"]

    def test_builder_copies_adapter_config_structs_from_caller(self):
        """Builder should not retain references to caller-owned adapter config structs."""
        pipeline_cfg = PipelineAdapterConfig.from_dict(
            {"hamilton_tracker": {"project_id": 123}}
        )
        project_cfg = ProjectAdapterConfig.from_dict(
            {"hamilton_tracker": {"api_key": "secret"}}
        )

        builder = (
            RunConfigBuilder()
            .with_pipeline_adapter_cfg(pipeline_cfg)
            .with_project_adapter_cfg(project_cfg)
        )

        pipeline_cfg.hamilton_tracker.project_id = 999
        project_cfg.hamilton_tracker.api_key = "changed"

        run_config = builder.build()

        assert run_config.pipeline_adapter_cfg.hamilton_tracker.project_id == 123
        assert run_config.project_adapter_cfg.hamilton_tracker.api_key == "secret"

    def test_builder_copies_callback_spec_state(self):
        """Built configs should not share mutable callback kwargs with the builder."""
        callback = Mock()
        builder = RunConfigBuilder().with_on_success(
            (callback, ("extra",), {"flag": True})
        )

        run_config1 = builder.build()
        run_config1.on_success.kwargs["flag"] = False
        run_config2 = builder.build()

        assert run_config2.on_success.kwargs == {"flag": True}

    def test_builder_from_config_does_not_mutate_original_on_partial_overrides(self):
        """Builder should clone the base config and merge partial nested overrides."""
        original = RunConfig(
            executor=ExecutorConfig(type="local", max_workers=None, num_cpus=None),
            with_adapter=WithAdapterConfig(mlflow=True),
            pipeline_adapter_cfg=PipelineAdapterConfig.from_dict(
                {"hamilton_tracker": {"project_id": 123}}
            ),
        )

        new_config = (
            RunConfigBuilder.from_config(original)
            .with_executor({"max_workers": 2})
            .with_with_adapter_cfg({"hamilton_tracker": True})
            .with_pipeline_adapter_cfg({"hamilton_tracker": {"tags": {"env": "prod"}}})
            .build()
        )

        assert original.executor.type == "local"
        assert original.executor.max_workers is None
        assert original.with_adapter.mlflow is True
        assert original.with_adapter.hamilton_tracker is False
        assert original.pipeline_adapter_cfg.hamilton_tracker.project_id == 123
        assert original.pipeline_adapter_cfg.hamilton_tracker.tags == {}

        assert new_config.executor.type == "local"
        assert new_config.executor.max_workers == 2
        assert new_config.with_adapter.mlflow is True
        assert new_config.with_adapter.hamilton_tracker is True
        assert new_config.pipeline_adapter_cfg.hamilton_tracker.project_id == 123
        assert new_config.pipeline_adapter_cfg.hamilton_tracker.tags == {"env": "prod"}

    def test_builder_from_config_can_explicitly_reset_nested_structs_to_defaults(self):
        """Struct-based builder overrides should survive later pipeline-default merging."""
        base = RunConfig(
            executor=ExecutorConfig(type="local", max_workers=None, num_cpus=None),
            with_adapter=WithAdapterConfig(mlflow=True),
            retry=RetryConfig(max_retries=5, retry_delay=9.0, jitter_factor=0.3),
        )

        override = (
            RunConfigBuilder.from_config(base)
            .with_executor(ExecutorConfig(type="threadpool"))
            .with_with_adapter_cfg(WithAdapterConfig())
            .with_retry_config(max_retries=3, retry_delay=1.0, jitter_factor=0.1)
            .build()
        )

        merged = merge_run_configs(base, override)

        assert merged.executor.type == "threadpool"
        assert merged.with_adapter.mlflow is False
        assert merged.with_adapter.hamilton_tracker is False
        assert merged.retry.max_retries == 3
        assert merged.retry.retry_delay == 1.0
        assert merged.retry.jitter_factor == 0.1

    def test_builder_from_config_can_explicitly_reset_simple_fields_to_defaults(self):
        """Builder should preserve explicit resets of simple fields during merge."""
        base = RunConfig(
            inputs={"x": 1},
            final_vars=["out"],
            config={"a": 1},
            log_level="DEBUG",
            reload=True,
            async_driver=True,
        )

        override = (
            RunConfigBuilder.from_config(base)
            .with_inputs({})
            .with_final_vars([])
            .with_config({})
            .with_log_level("INFO")
            .with_reload(False)
            .with_async_driver(None)
            .build()
        )

        merged = merge_run_configs(base, override)

        assert merged.inputs == {}
        assert merged.final_vars == []
        assert merged.config == {}
        assert merged.log_level == "INFO"
        assert merged.reload is False
        assert merged.async_driver is None

    def test_explicit_simple_resets_survive_repeated_merges(self):
        """Merged configs should retain explicit reset intent for later merges."""
        base = RunConfig(
            inputs={"x": 1},
            final_vars=["out"],
            config={"a": 1},
            log_level="DEBUG",
            reload=True,
            async_driver=True,
        )

        override = (
            RunConfigBuilder.from_config(base)
            .with_inputs({})
            .with_final_vars([])
            .with_config({})
            .with_log_level("INFO")
            .with_reload(False)
            .with_async_driver(None)
            .build()
        )

        merged_once = merge_run_configs(base, override)
        merged_twice = merge_run_configs(base, merged_once)

        assert merged_twice.inputs == {}
        assert merged_twice.final_vars == []
        assert merged_twice.config == {}
        assert merged_twice.log_level == "INFO"
        assert merged_twice.reload is False
        assert merged_twice.async_driver is None

    def test_builder_rejects_dangerous_callbacks(self):
        with pytest.raises(SecurityError, match="Dangerous callback function"):
            RunConfigBuilder().with_on_success(eval)


class TestMergeRunConfig:
    def test_merge_additional_modules_merges_and_deduplicates(self):
        module_obj = ModuleType("merge_mod")
        run_config = RunConfig(additional_modules=["setup"])

        merge_run_config_with_kwargs(
            run_config,
            {"additional_modules": [module_obj, "setup"]},
        )

        assert run_config.additional_modules[0] == "setup"
        assert run_config.additional_modules[1] is module_obj
        assert len(run_config.additional_modules) == 2

    def test_merge_async_driver_toggle(self):
        run_config = RunConfig()
        merge_run_config_with_kwargs(run_config, {"async_driver": True})
        assert run_config.async_driver is True

    def test_merge_async_driver_none_preserved(self):
        """Regression: async_driver=None must clear the toggle instead of being ignored."""
        run_config = RunConfig(async_driver=True)
        merge_run_config_with_kwargs(run_config, {"async_driver": None})
        assert run_config.async_driver is None

    def test_merge_executor_cfg_preserves_existing_fields(self):
        run_config = RunConfig(executor=ExecutorConfig(type="local", max_workers=None, num_cpus=None))

        merge_run_config_with_kwargs(run_config, {"executor_cfg": {"max_workers": 2}})

        assert run_config.executor.type == "local"
        assert run_config.executor.max_workers == 2
        assert run_config.executor.num_cpus is None
        assert run_config.executor_override_raw == {"max_workers": 2}

    def test_merge_flat_retry_override_normalizes_to_nested(self):
        """Deprecated flat retry fields from a later layer normalize into nested retry."""
        base = RunConfig(
            retry=RetryConfig(max_retries=3, retry_delay=1.0, jitter_factor=0.1)
        )
        override = RunConfig(
            max_retries=5,
            retry_delay=2.0,
            jitter_factor=0.3,
            retry_exceptions=["ValueError"],
        )
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            merged = merge_run_configs(base, override)
        assert merged.retry.max_retries == 5
        assert merged.retry.retry_delay == 2.0
        assert merged.retry.jitter_factor == 0.3
        assert merged.retry.retry_exceptions == [ValueError]
    def test_merge_nested_retry_override_wins(self):
        """A nested retry config from a later layer overrides the base nested retry."""
        base = RunConfig(
            retry=RetryConfig(max_retries=3, retry_delay=1.0, jitter_factor=0.1)
        )
        override = RunConfig(
            retry=RetryConfig(max_retries=5, retry_delay=2.0, jitter_factor=0.3)
        )
        merged = merge_run_configs(base, override)
        assert merged.retry.max_retries == 5
        assert merged.retry.retry_delay == 2.0
        assert merged.retry.jitter_factor == 0.3

    def test_merge_flat_retry_kwargs_normalize_to_nested(self):
        """Deprecated flat retry kwargs normalize into nested retry config."""
        run_config = RunConfig(
            retry=RetryConfig(max_retries=3, retry_delay=1.0, jitter_factor=0.1)
        )

        merge_run_config_with_kwargs(
            run_config,
            {
                "max_retries": 5,
                "retry_delay": 2.0,
                "jitter_factor": 0.3,
                "retry_exceptions": ["ValueError"],
            },
        )

        assert run_config.retry.max_retries == 5
        assert run_config.retry.retry_delay == 2.0
        assert run_config.retry.jitter_factor == 0.3
        assert run_config.retry.retry_exceptions == [ValueError]

    def test_merge_nested_retry_wins_over_flat_kwargs_in_same_layer(self):
        """Nested retry in kwargs wins over flat retry fields in the same kwargs layer."""
        run_config = RunConfig()

        merge_run_config_with_kwargs(
            run_config,
            {
                "retry": {
                    "max_retries": 5,
                    "retry_delay": 2.0,
                    "retry_exceptions": ["TimeoutError"],
                },
                "max_retries": 3,
                "retry_delay": 1.0,
                "retry_exceptions": ["ValueError"],
            },
        )

        assert run_config.retry.max_retries == 5
        assert run_config.retry.retry_delay == 2.0
        assert run_config.retry.retry_exceptions == [TimeoutError]

    def test_merge_retry_patch_preserves_existing_fields(self):
        run_config = RunConfig(retry=RetryConfig(max_retries=5, retry_delay=9.0, jitter_factor=0.3))

        merge_run_config_with_kwargs(run_config, {"retry": {"max_retries": 1}})

        assert run_config.retry.max_retries == 1
        assert run_config.retry.retry_delay == 9.0
        assert run_config.retry.jitter_factor == 0.3
        assert run_config.max_retries == 1
        assert run_config.retry_delay == 9.0

    def test_merge_with_adapter_cfg_preserves_existing_flags(self):
        run_config = RunConfig(with_adapter=WithAdapterConfig(mlflow=True))

        merge_run_config_with_kwargs(
            run_config,
            {"with_adapter_cfg": {"hamilton_tracker": True}},
        )

        assert run_config.with_adapter.hamilton_tracker is True
        assert run_config.with_adapter.mlflow is True

    def test_merge_pipeline_adapter_cfg_preserves_existing_nested_values(self):
        run_config = RunConfig(
            pipeline_adapter_cfg=PipelineAdapterConfig.from_dict(
                {"hamilton_tracker": {"project_id": 123}}
            )
        )

        merge_run_config_with_kwargs(
            run_config,
            {"pipeline_adapter_cfg": {"hamilton_tracker": {"tags": {"env": "prod"}}}},
        )

        assert run_config.pipeline_adapter_cfg.hamilton_tracker.project_id == 123
        assert run_config.pipeline_adapter_cfg.hamilton_tracker.tags == {"env": "prod"}

    def test_merge_project_adapter_cfg_preserves_existing_nested_values(self):
        run_config = RunConfig(
            project_adapter_cfg=ProjectAdapterConfig.from_dict(
                {"hamilton_tracker": {"api_key": "secret"}}
            )
        )

        merge_run_config_with_kwargs(
            run_config,
            {"project_adapter_cfg": {"hamilton_tracker": {"ui_url": "http://ui.local"}}},
        )

        assert run_config.project_adapter_cfg.hamilton_tracker.api_key == "secret"
        assert run_config.project_adapter_cfg.hamilton_tracker.ui_url == "http://ui.local"

    def test_merge_callback_tuple_normalizes_to_callback_spec(self):
        run_config = RunConfig()
        callback = Mock()

        merge_run_config_with_kwargs(
            run_config,
            {"on_success": (callback, ("extra",), {"flag": True})},
        )

        assert run_config.on_success.func is callback
        assert run_config.on_success.args == ("extra",)
        assert run_config.on_success.kwargs == {"flag": True}


class TestRunConfigPersistence:
    def test_pipeline_save_omits_deprecated_retry_fields(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            fs = filesystem(tmpdir, cached=False, dirfs=True)

            with warnings.catch_warnings():
                warnings.simplefilter("ignore", DeprecationWarning)
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

            config_path = Path(tmpdir) / "conf" / "pipelines" / "retry_clean.yml"
            with config_path.open() as fh:
                data = yaml.safe_load(fh)

        run_section = data["run"]
        for field in DEPRECATED_RETRY_FIELDS:
            assert field not in run_section
        assert run_section["retry"]["max_retries"] == 5
        assert run_section["retry"]["retry_delay"] == 2.5
        assert run_section["retry"]["jitter_factor"] == 0.3
        assert run_section["retry"]["retry_exceptions"] == ["ValueError"]

    def test_load_mixed_flat_and_nested_retry_uses_nested(self):
        """When a YAML file contains both nested and flat retry fields, nested wins."""
        with tempfile.TemporaryDirectory() as tmpdir:
            fs = filesystem(tmpdir, cached=False, dirfs=True)
            pipeline_dir = Path(tmpdir) / "conf" / "pipelines"
            pipeline_dir.mkdir(parents=True)

            mixed_path = pipeline_dir / "mixed.yml"
            with mixed_path.open("w") as fh:
                yaml.safe_dump(
                    {
                        "run": {
                            "retry": {
                                "max_retries": 5,
                                "retry_delay": 2.0,
                                "jitter_factor": 0.3,
                            },
                            "max_retries": 3,
                            "retry_delay": 1.0,
                            "jitter_factor": 0.1,
                        }
                    },
                    fh,
                )

            with warnings.catch_warnings():
                warnings.simplefilter("ignore", DeprecationWarning)
                pipeline_cfg = PipelineConfig.load(base_dir=tmpdir, name="mixed", fs=fs)

        assert pipeline_cfg.run.retry.max_retries == 5
        assert pytest.approx(pipeline_cfg.run.retry.retry_delay) == 2.0
        assert pytest.approx(pipeline_cfg.run.retry.jitter_factor) == 0.3

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


class TestExplicitNonePolicy:
    """Test cases for issue #39: explicit None semantics through sync/async paths."""

    def test_run_config_from_dict_tracks_explicit_none(self):
        """Source-edge normalization should record explicit None values."""
        run_config = RunConfig.from_dict({"async_driver": None})
        assert "async_driver" in run_config.explicit_overrides

    def test_pipeline_config_from_dict_preserves_explicit_run_none(self):
        """Pipeline config loading should preserve explicit None in run section."""
        pipeline_cfg = PipelineConfig.from_dict(
            name="test", data={"run": {"async_driver": None}}
        )
        assert "async_driver" in pipeline_cfg.run.explicit_overrides

    def test_merge_preserves_explicit_async_driver_none(self):
        """Explicit async_driver=None should clear a previous True value."""
        base = RunConfig(async_driver=True)
        override = RunConfig.from_dict({"async_driver": None})
        merged = merge_run_configs(base, override)
        assert merged.async_driver is None

    def test_merge_explicit_none_clears_structured_fields(self):
        """Explicit None for structured clearable fields should clear base values."""
        base = RunConfig(
            adapter={"key": "value"},
            pipeline_adapter_cfg={"enabled": True},
            project_adapter_cfg={"enabled": True},
            on_success=CallbackSpec(func=lambda: None),
            on_failure=CallbackSpec(func=lambda: None),
        )
        override = RunConfig.from_dict(
            {
                "adapter": None,
                "pipeline_adapter_cfg": None,
                "project_adapter_cfg": None,
                "on_success": None,
                "on_failure": None,
            }
        )
        merged = merge_run_configs(base, override)
        assert merged.adapter is None
        assert merged.pipeline_adapter_cfg is None
        assert merged.project_adapter_cfg is None
        assert merged.on_success is None
        assert merged.on_failure is None

    def test_merge_run_config_with_kwargs_clearable_none_clears(self):
        """Clearable fields should reset to None when explicitly passed."""
        run_config = RunConfig(
            inputs={"x": 1},
            config={"a": 1},
            cache=True,
            log_level="DEBUG",
            reload=True,
            additional_modules=["mod"],
            adapter={"k": "v"},
            async_driver=True,
            final_vars=["out"],
        )
        merge_run_config_with_kwargs(
            run_config,
            {
                "inputs": None,
                "config": None,
                "cache": None,
                "log_level": None,
                "reload": None,
                "additional_modules": None,
                "adapter": None,
                "async_driver": None,
                "final_vars": None,
            },
        )
        assert run_config.inputs is None
        assert run_config.config is None
        assert run_config.cache is None
        assert run_config.log_level is None
        assert run_config.reload is None
        assert run_config.additional_modules is None
        assert run_config.adapter is None
        assert run_config.async_driver is None
        assert run_config.final_vars is None

    def test_merge_run_config_with_kwargs_non_clearable_none_raises(self):
        """Non-clearable fields should reject explicit None with field-specific errors."""
        with pytest.raises(ValueError, match="executor_cfg cannot be set to None"):
            merge_run_config_with_kwargs(RunConfig(), {"executor_cfg": None})
        with pytest.raises(ValueError, match="with_adapter_cfg cannot be set to None"):
            merge_run_config_with_kwargs(RunConfig(), {"with_adapter_cfg": None})
        with pytest.raises(ValueError, match="retry cannot be set to None"):
            merge_run_config_with_kwargs(RunConfig(), {"retry": None})

    def test_validate_resolved_run_config_rejects_none_executor(self):
        """Resolved config validation should reject a None executor."""
        run_config = RunConfig(executor=None)
        with pytest.raises(ValueError, match="RunConfig.executor cannot be None"):
            validate_resolved_run_config(run_config)

    def test_run_config_from_dict_rejects_retry_none(self):
        """Non-clearable retry field should reject explicit None at source edge."""
        with pytest.raises(ValueError, match="RunConfig.retry cannot be set to None"):
            RunConfig.from_dict({"retry": None})

    def test_builder_rejects_non_clearable_none(self):
        """Builder methods for non-clearable fields should reject explicit None."""
        with pytest.raises(ValueError, match="with_executor cannot be set to None"):
            RunConfigBuilder().with_executor(None)
        with pytest.raises(ValueError, match="with_with_adapter_cfg cannot be set to None"):
            RunConfigBuilder().with_with_adapter_cfg(None)
        with pytest.raises(ValueError, match="with_executor cannot be set to None"):
            RunConfigBuilder().with_executor_cfg(None)

    def test_retry_config_to_dict_handles_string_exceptions(self):
        """Test that RetryConfig.to_dict() preserves known string exceptions as-is."""

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
