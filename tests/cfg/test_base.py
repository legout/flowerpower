from unittest.mock import MagicMock, mock_open

import msgspec
import pytest
from fsspec.implementations.memory import MemoryFileSystem

from flowerpower.cfg.base import BaseConfig

# --- Helper Structs for Testing ---


class SimpleConfig(BaseConfig, kw_only=True):
    name: str
    value: int = 10  # Field with a default value
    optional_field: str | None = None
    nested: dict[str, str] | None = None


class AnotherConfig(BaseConfig, kw_only=True):
    id: str
    data: list[int]


# --- Tests for BaseConfig ---


def test_base_config_to_dict():
    config = SimpleConfig(name="test", value=20, nested={"key": "val"})
    expected_dict = {
        "name": "test",
        "value": 20,
        "optional_field": None,
        "nested": {"key": "val"},
    }
    assert config.to_dict() == expected_dict


def test_base_config_from_dict():
    data = {"name": "from_dict_test", "value": 50, "optional_field": "opt_val"}
    config = SimpleConfig.from_dict(data)
    assert isinstance(config, SimpleConfig)
    assert config.name == "from_dict_test"
    assert config.value == 50
    assert config.optional_field == "opt_val"
    assert config.nested is None  # Not provided, should be default


def test_base_config_from_dict_missing_required_field():
    data = {"value": 50}  # Missing 'name'
    with pytest.raises(msgspec.ValidationError):
        SimpleConfig.from_dict(data)


def test_base_config_from_dict_incorrect_type():
    data = {"name": "wrong_type_test", "value": "not_an_int"}
    with pytest.raises(msgspec.ValidationError):
        SimpleConfig.from_dict(data)


def test_base_config_to_yaml(mocker):
    mock_fs = MemoryFileSystem()
    mocker.patch("fsspec.filesystem").return_value = mock_fs  # Patch default fs

    config = SimpleConfig(name="yaml_test", value=30, optional_field="present")
    path = "test_config.yaml"

    config.to_yaml(path, fs=mock_fs)  # Explicitly pass mock_fs for clarity

    # MemoryFileSystem adds a leading slash to paths
    assert f"/{path}" in mock_fs.store

    # Verify content
    with mock_fs.open(path, "rb") as f:
        content = f.read()

    # msgspec.yaml.encode uses msgspec's internal YAML encoder.
    # We can compare by decoding it back or by comparing with a known good YAML string.
    # Let's decode it back for a robust check.
    # Note: msgspec's YAML output might not have --- or ... markers by default.
    # And order might differ if not 'deterministic' (which it is by default in BaseConfig)
    decoded_from_yaml = msgspec.yaml.decode(content, type=SimpleConfig)
    assert decoded_from_yaml.name == "yaml_test"
    assert decoded_from_yaml.value == 30
    assert decoded_from_yaml.optional_field == "present"


def test_base_config_to_yaml_no_fs_provided(mocker):
    mock_file_open = mock_open()
    mocker.patch("builtins.open", mock_file_open)
    # Mock fsspec.filesystem to return a MagicMock that has an .open method
    mock_fs_instance = MagicMock()
    mock_fs_instance.open = mock_file_open
    mocker.patch("fsspec.filesystem", return_value=mock_fs_instance)

    config = SimpleConfig(name="yaml_test_no_fs", value=35)
    path = "test_config_no_fs.yaml"

    config.to_yaml(path)  # No fs provided, should use default from fsspec

    # The get_filesystem function is now used, which calls fsspec.filesystem
    # and then the filesystem's open method is called
    mock_fs_instance.open.assert_called_once()
    # Check what was written to the mock file
    # msgspec.yaml.encode returns bytes
    expected_yaml_bytes = msgspec.yaml.encode(config, order="deterministic")

    # mock_open().write() calls are a bit tricky to inspect directly for all chunks.
    # We can check the first call's argument.
    args, _ = mock_fs_instance.open().write.call_args
    assert args[0] == expected_yaml_bytes


def test_base_config_from_yaml(mocker):
    mock_fs = MemoryFileSystem()
    mocker.patch("fsspec.filesystem").return_value = mock_fs

    test_yaml_content = "name: yaml_load_test\nvalue: 70\noptional_field: loaded_opt\n"
    path = "memory://load_config.yaml"

    with mock_fs.open(path, "w") as f:
        f.write(test_yaml_content)

    config = SimpleConfig.from_yaml(path, fs=mock_fs)

    assert isinstance(config, SimpleConfig)
    assert config.name == "yaml_load_test"
    assert config.value == 70
    assert config.optional_field == "loaded_opt"


def test_base_config_from_yaml_no_fs_provided(mocker):
    test_yaml_content = "name: yaml_load_no_fs\nvalue: 75\n"
    
    # Create a mock file handle that returns our test content
    mock_file_handle = MagicMock()
    mock_file_handle.__enter__.return_value.read.return_value = test_yaml_content
    mock_file_handle.__exit__.return_value = None
    
    # Create a mock filesystem that returns our mock file handle
    mock_fs_instance = MagicMock()
    mock_fs_instance.open.return_value = mock_file_handle
    
    # Mock the filesystem function directly in the misc module
    mocker.patch("flowerpower.utils.misc.filesystem", return_value=mock_fs_instance)

    path = "load_config_no_fs.yaml"
    config = SimpleConfig.from_yaml(path)  # No fs, should use default

    mock_fs_instance.open.assert_called_once_with(path)
    assert isinstance(config, SimpleConfig)
    assert config.name == "yaml_load_no_fs"
    assert config.value == 75


def test_base_config_update_method():
    config = SimpleConfig(name="initial_name", value=100, nested={"a": "1", "b": "2"})
    update_data = {
        "name": "updated_name",
        "optional_field": "now_set",
        "value": 101,
        "nested": {"b": "updated_b", "c": "3"},
    }

    config.update(update_data)

    assert config.name == "updated_name"
    assert config.value == 101
    assert config.optional_field == "now_set"
    assert config.nested == {
        "a": "1",
        "b": "updated_b",
        "c": "3",
    }  # Nested dicts are updated


def test_base_config_update_method_new_field():
    config = SimpleConfig(name="initial_name", value=100)
    update_data = {"new_field_runtime": "added"}

    # With msgspec.Struct, we can't add new fields at runtime
    # The update method should only update existing fields
    with pytest.raises(TypeError):
        config.update(update_data)


def test_base_config_merge_dict_method():
    config = SimpleConfig(
        name="original", value=10, optional_field="orig_opt", nested={"x": "orig_x"}
    )
    update_dict = {
        "name": "merged_name",
        "value": 20,
        "nested": {"y": "new_y"},
    }

    merged_config = config.merge_dict(update_dict)

    # Original config should not be modified
    assert config.name == "original"
    assert config.value == 10
    assert config.optional_field == "orig_opt"
    assert config.nested == {"x": "orig_x"}

    # Merged config should have updates
    assert merged_config.name == "merged_name"
    assert merged_config.value == 20
    assert (
        merged_config.optional_field == "orig_opt"
    )  # Not in update_dict, so remains from original copy
    assert merged_config.nested == {
        "x": "orig_x",
        "y": "new_y",
    }  # Nested dicts are updated


def test_base_config_merge_method_simple():
    target = SimpleConfig(name="target", value=1, optional_field="target_opt")
    # Source: 'name' is different, 'value' is default, 'optional_field' is new
    source = SimpleConfig(
        name="source_name",
        value=10,  # Default value for SimpleConfig.value
        optional_field="source_opt_new",
    )

    merged = target.merge(source)

    # Target should be unchanged
    assert target.name == "target"
    assert target.value == 1
    assert target.optional_field == "target_opt"

    # The current merge logic creates a copy of target and then updates with source values
    # Since 'name' is not None, it gets updated from source
    # Since 'value' is not None, it gets updated from source (even if it's the default)
    # Since 'optional_field' is not None, it gets updated from source
    assert merged.name == "source_name"  # From source
    assert merged.value == 10  # From source
    assert merged.optional_field == "source_opt_new"  # From source


class ConfigWithNoDefaults(BaseConfig, kw_only=True):
    field_a: str
    field_b: int | None  # Explicitly None is different from missing default


def test_base_config_merge_method_no_explicit_defaults_source_has_none():
    target = ConfigWithNoDefaults(field_a="target_a", field_b=100)
    source = ConfigWithNoDefaults(
        field_a="source_a", field_b=None
    )  # field_b is None, which is its default if no other default provided

    merged = target.merge(source)

    assert merged.field_a == "source_a"  # From source
    # Since field_b in source is None (its implicit default if not otherwise specified), target's value should be kept.
    assert merged.field_b == 100


def test_base_config_merge_method_source_fields_are_all_defaults():
    target = SimpleConfig(name="target_name", value=1, optional_field="target_opt")
    # Let's make a source where 'name' is set, but 'value' and 'optional_field' are defaults.
    source_for_merge = SimpleConfig(
        name="a_name", value=10, optional_field=None
    )  # 10 and None are defaults for SimpleConfig

    merged = target.merge(source_for_merge)

    # The current merge logic creates a copy of target and then updates with source values
    # Since 'name' is not None, it gets updated from source
    # Since 'value' is not None, it gets updated from source (even if it's the default)
    # Since 'optional_field' is None, it keeps the target's value
    assert merged.name == "a_name"  # Name from source
    assert merged.value == 10  # Value from source
    assert merged.optional_field == "target_opt"  # From target, as source.optional_field is None


def test_base_config_merge_method_type_mismatch():
    target = SimpleConfig(name="target")
    source_other_type = AnotherConfig(id="source_id", data=[1, 2])

    with pytest.raises(TypeError) as excinfo:
        target.merge(source_other_type)
    assert "Source must be an instance of SimpleConfig, not AnotherConfig" in str(
        excinfo.value
    )


def test_base_config_to_yaml_notimplementederror(mocker):
    # Mock get_filesystem to return a filesystem that doesn't support 'wb'
    mock_fs = MagicMock()
    mock_fs.open.side_effect = NotImplementedError("The filesystem does not support writing files.")
    mocker.patch("flowerpower.utils.misc.get_filesystem", return_value=mock_fs)

    config = SimpleConfig(name="test")
    # Pass the mock filesystem directly to ensure it's used
    with pytest.raises(
        NotImplementedError, match="The filesystem does not support writing files."
    ):
        config.to_yaml("anypath.yaml", fs=mock_fs)


# Additional test for merge when source has a field not in target (should not happen with same types)
# This is implicitly covered by type checking in merge and struct field definitions.


# Test for merge with nested structures (current merge is shallow for non-dict attributes)
class NestedOuterConfig(BaseConfig, kw_only=True):
    id: str
    inner: SimpleConfig | None = None


def test_base_config_merge_with_nested_structs():
    target = NestedOuterConfig(
        id="outer_target", inner=SimpleConfig(name="inner_target_name", value=1)
    )
    source = NestedOuterConfig(
        id="outer_source", inner=SimpleConfig(name="inner_source_name", value=200)
    )  # inner.value=200 (non-default)

    merged = target.merge(source)
    assert merged.id == "outer_source"
    # The current merge logic does a direct setattr for non-default fields.
    # If 'inner' is a struct, it will replace the entire 'inner' struct from target with source's 'inner' struct.
    # It does not recursively merge the fields of the nested structs. This is the expected behavior from the code.
    assert merged.inner is not None
    assert merged.inner.name == "inner_source_name"
    assert merged.inner.value == 200

    # Scenario: source.inner.value is default, source.inner.name is not.
    source_inner_default_val = NestedOuterConfig(
        id="outer_source_def", inner=SimpleConfig(name="inner_source_name_2", value=10)
    )  # value=10 is default for SimpleConfig
    merged_2 = target.merge(source_inner_default_val)

    assert merged_2.id == "outer_source_def"
    # The entire source_inner_default_val.inner object will be assigned to merged_2.inner
    # because source_inner_default_val.inner itself is not its default (which would be None for NestedOuterConfig.inner)
    assert merged_2.inner is not None
    assert merged_2.inner.name == "inner_source_name_2"
    assert (
        merged_2.inner.value == 10
    )  # This is the default value from SimpleConfig, carried over as part of the source's inner object.
    # The merge logic for BaseConfig checks if source.inner is default, not fields *within* source.inner.

    # Scenario: source.inner is None (its default for NestedOuterConfig)
    source_inner_is_none = NestedOuterConfig(id="outer_source_inner_none", inner=None)
    merged_3 = target.merge(source_inner_is_none)
    assert merged_3.id == "outer_source_inner_none"
    assert (
        merged_3.inner is not None
    )  # Should take from target, as source.inner is default (None)
    assert merged_3.inner.name == "inner_target_name"
    assert merged_3.inner.value == 1


class ConfigWithDefaultsInMeta(BaseConfig, kw_only=True):
    name: str = msgspec.field(default="default_name")
    value: int = msgspec.field(default=55)


def test_base_config_merge_with_msgspec_field_defaults():
    target = ConfigWithDefaultsInMeta(name="target_name", value=11)  # non-defaults
    source = ConfigWithDefaultsInMeta(name="source_name", value=55)  # value is default

    merged = target.merge(source)
    assert merged.name == "source_name"  # from source (not None)
    assert merged.value == 55  # from source (even though it's the default)

    source_both_default = ConfigWithDefaultsInMeta(name="default_name", value=55)
    merged_2 = target.merge(source_both_default)
    assert merged_2.name == "default_name"  # from source (not None)
    assert merged_2.value == 55  # from source (even though it's the default)

    source_name_default = ConfigWithDefaultsInMeta(
        name="default_name", value=22
    )  # name is default
    merged_3 = target.merge(source_name_default)
    assert merged_3.name == "default_name"  # from source (not None)
    assert merged_3.value == 22  # from source (not default)
