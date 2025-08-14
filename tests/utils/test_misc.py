from typing import Any

import msgspec
import pytest

# Assuming misc.py is in src/flowerpower/utils/
from flowerpower.utils.misc import (get_partitions_from_path,
                                    update_config_from_dict,
                                    update_nested_dict)

# --- Tests for get_partitions_from_path ---


def test_get_partitions_from_path_hive_style():
    path = "/data/lake/db/table_name/event_date=2023-01-01/country=US/data.parquet"
    partitioning = "hive"
    expected = [("event_date", "2023-01-01"), ("country", "US")]
    assert get_partitions_from_path(path, partitioning) == expected


def test_get_partitions_from_path_hive_style_no_file_extension():
    path = "/data/lake/db/table_name/event_date=2023-01-01/country=US"
    partitioning = "hive"
    expected = [("event_date", "2023-01-01"), ("country", "US")]
    assert get_partitions_from_path(path, partitioning) == expected


def test_get_partitions_from_path_hive_style_no_partitions():
    path = "/data/lake/db/table_name/data.parquet"
    partitioning = "hive"
    expected = []
    assert get_partitions_from_path(path, partitioning) == expected


def test_get_partitions_from_path_hive_style_root_path():
    path = "/"
    partitioning = "hive"
    expected = []
    assert get_partitions_from_path(path, partitioning) == expected


def test_get_partitions_from_path_single_string_partitioning():
    # This case seems a bit underspecified or potentially misinterpreting the logic in the original code.
    # Let's assume path is relative for this to make sense as 'data' being the value.
    path_relative = "some_value_for_customer_type/more_data/file.txt"
    expected_relative = [("customer_type", "some_value_for_customer_type")]
    assert get_partitions_from_path(path_relative, "customer_type") == expected_relative

    path_absolute = "/root_dir_is_value/another_level/file.txt"
    # parts will be ['', 'root_dir_is_value', 'another_level']
    # parts[0] is '', so it's [('customer_type', '')] - this is likely not intended.
    # The original function seems to work better with relative-like paths or paths not starting with '/'
    # when partitioning is a single string (non-hive).
    # Given the code: `parts = path.split("/")`, then `(partitioning, parts[0])`
    # If path = "/value/...", parts = ["", "value", ...], so parts[0] = ""
    # If path = "value/...", parts = ["value", ...], so parts[0] = "value"
    # Let's test the actual behavior.
    assert get_partitions_from_path(path_absolute, "customer_type") == [
        ("customer_type", "")
    ]


def test_get_partitions_from_path_list_partitioning():
    path = "/data/region/US/year/2023/month/12/data.csv"
    partitioning = ["region", "year", "month"]
    expected = [("region", "US"), ("year", "2023"), ("month", "12")]
    assert get_partitions_from_path(path, partitioning) == expected


def test_get_partitions_from_path_list_partitioning_no_file_extension():
    path = "/data/region/US/year/2023/month/12"
    partitioning = ["region", "year", "month"]
    expected = [("region", "US"), ("year", "2023"), ("month", "12")]
    assert get_partitions_from_path(path, partitioning) == expected


def test_get_partitions_from_path_list_partitioning_fewer_parts_than_keys():
    path = "/data/region/US/year/2023"  # Only two actual partition values in path
    partitioning = ["region", "year", "month"]  # Expecting three keys
    # The code `parts[-len(partitioning):]` will take the last 3 parts.
    # parts for "/data/region/US/year/2023" -> ['', 'data', 'region', 'US', 'year', '2023']
    # parts[-3:] -> ['US', 'year', '2023'] if we consider the relevant parts from path.dirname
    # path = os.path.dirname(path) -> /data/region/US/year
    # parts = ['', 'data', 'region', 'US', 'year']
    # parts[-3:] = ['region', 'US', 'year']
    # zip(['region', 'year', 'month'], ['region', 'US', 'year'])
    expected = [("region", "region"), ("year", "US"), ("month", "year")]
    assert get_partitions_from_path(path, partitioning) == expected


def test_get_partitions_from_path_list_empty_partitioning_list():
    path = "/data/region/US/year/2023/data.csv"
    partitioning = []
    expected = []
    assert get_partitions_from_path(path, partitioning) == expected


def test_get_partitions_from_path_none_partitioning():
    path = "/data/some/path/file.txt"
    # When partitioning is None, the function behaves like list partitioning
    # with an empty list if we strictly follow the code path.
    # else: return list(zip(partitioning, parts[-len(partitioning) :]))
    # If partitioning is None, this will raise a TypeError in zip or len.
    # This indicates a potential bug or unhandled case in the original function.
    with pytest.raises(
        TypeError
    ):  # Expecting an error due to len(None) or zip(None, ...)
        get_partitions_from_path(path, None)


# --- Tests for update_nested_dict ---


def test_update_nested_dict_simple_update():
    original = {"a": 1, "b": {"x": 10, "y": 20}}
    updates = {"b": {"y": 25, "z": 30}, "c": 3}
    expected = {"a": 1, "b": {"x": 10, "y": 25, "z": 30}, "c": 3}
    assert update_nested_dict(original, updates) == expected


def test_update_nested_dict_add_new_keys():
    original = {"a": 1}
    updates = {"b": 2, "c": {"d": 3}}
    expected = {"a": 1, "b": 2, "c": {"d": 3}}
    assert update_nested_dict(original, updates) == expected


def test_update_nested_dict_empty_original():
    original = {}
    updates = {"a": 1, "b": {"c": 2}}
    expected = {"a": 1, "b": {"c": 2}}
    assert update_nested_dict(original, updates) == expected


def test_update_nested_dict_empty_updates():
    original = {"a": 1, "b": {"c": 2}}
    updates = {}
    expected = {"a": 1, "b": {"c": 2}}  # Should return a copy
    result = update_nested_dict(original, updates)
    assert result == expected
    assert id(result) != id(original)  # Ensure it's a copy


def test_update_nested_dict_non_dict_in_original_overwritten():
    original = {"a": 1, "b": "not_a_dict"}
    updates = {"b": {"c": 2}}
    expected = {"a": 1, "b": {"c": 2}}
    assert update_nested_dict(original, updates) == expected


def test_update_nested_dict_non_dict_in_updates_overwrites():
    original = {"a": 1, "b": {"c": 2}}
    updates = {"b": "not_a_dict_either"}
    expected = {"a": 1, "b": "not_a_dict_either"}
    assert update_nested_dict(original, updates) == expected


def test_update_nested_dict_deeper_nesting():
    original = {"a": {"b": {"c": 1, "d": 2}, "e": 3}}
    updates = {"a": {"b": {"d": 4, "f": 5}}}
    expected = {"a": {"b": {"c": 1, "d": 4, "f": 5}, "e": 3}}
    assert update_nested_dict(original, updates) == expected


# --- Tests for update_config_from_dict ---


# Define simple msgspec Structs for testing
class NestedStruct(msgspec.Struct, kw_only=True):
    value1: int
    value2: str | None = None


class ExampleStruct(msgspec.Struct, kw_only=True):
    field_a: str
    field_b: int = 10
    nested: NestedStruct | None = None
    other_nested: dict[str, Any] | None = None


def test_update_config_from_dict_simple_fields():
    struct_instance = ExampleStruct(field_a="initial_a")
    updates = {"field_a": "updated_a", "field_b": 20}

    updated_struct = update_config_from_dict(struct_instance, updates)

    assert updated_struct.field_a == "updated_a"
    assert updated_struct.field_b == 20
    assert updated_struct.nested is None  # Not touched


def test_update_config_from_dict_with_nested_struct():
    struct_instance = ExampleStruct(
        field_a="initial_a", nested=NestedStruct(value1=100, value2="initial_nested")
    )
    updates = {
        "field_a": "updated_a",
        "nested": {"value1": 150, "value2": "updated_nested_val"},
    }

    updated_struct = update_config_from_dict(struct_instance, updates)

    assert updated_struct.field_a == "updated_a"
    assert updated_struct.nested is not None
    assert updated_struct.nested.value1 == 150
    assert updated_struct.nested.value2 == "updated_nested_val"


def test_update_config_from_dict_nested_struct_partial_update():
    struct_instance = ExampleStruct(
        field_a="initial_a", nested=NestedStruct(value1=100, value2="initial_nested")
    )
    updates = {
        "nested": {"value2": "updated_nested_only"}
    }  # Only update one field in nested

    updated_struct = update_config_from_dict(struct_instance, updates)

    assert updated_struct.field_a == "initial_a"  # Unchanged
    assert updated_struct.nested is not None
    assert updated_struct.nested.value1 == 100  # Unchanged from original nested
    assert updated_struct.nested.value2 == "updated_nested_only"


def test_update_config_from_dict_nested_struct_becomes_none():
    struct_instance = ExampleStruct(
        field_a="initial_a", nested=NestedStruct(value1=100, value2="initial_nested")
    )
    updates = {"nested": None}

    updated_struct = update_config_from_dict(struct_instance, updates)
    assert updated_struct.nested is None


def test_update_config_from_dict_nested_struct_from_none():
    struct_instance = ExampleStruct(field_a="initial_a", nested=None)
    updates = {"nested": {"value1": 200, "value2": "new_nested"}}

    updated_struct = update_config_from_dict(struct_instance, updates)

    assert updated_struct.nested is not None
    assert updated_struct.nested.value1 == 200
    assert updated_struct.nested.value2 == "new_nested"


def test_update_config_from_dict_with_plain_nested_dict():
    struct_instance = ExampleStruct(
        field_a="initial_a", other_nested={"key1": "val1", "sub": {"s1": 10}}
    )
    updates = {
        "other_nested": {
            "key1": "updated_val1",
            "sub": {"s1": 20, "s2": 30},
            "new_key": "added",
        }
    }
    updated_struct = update_config_from_dict(struct_instance, updates)

    assert updated_struct.other_nested is not None
    assert updated_struct.other_nested["key1"] == "updated_val1"
    assert updated_struct.other_nested["sub"]["s1"] == 20
    assert updated_struct.other_nested["sub"]["s2"] == 30
    assert updated_struct.other_nested["new_key"] == "added"


def test_update_config_from_dict_key_not_in_struct():
    struct_instance = ExampleStruct(field_a="initial")
    updates = {"field_c_not_exists": "new_value"}  # This key is not in TestStruct

    # The current implementation of update_config_from_dict uses msgspec.to_builtins
    # and then msgspec.convert. If a key from `updates` is not in the struct's
    # original dict representation, it won't be added by msgspec.convert unless
    # the struct supports extra fields (which default msgspec.Struct does not without `gc=False`).
    # Let's test the behavior.
    updated_struct = update_config_from_dict(struct_instance, updates)

    # Expect that 'field_c_not_exists' is NOT added to the struct
    with pytest.raises(AttributeError):
        getattr(updated_struct, "field_c_not_exists")
    # Ensure original fields are untouched if not in updates
    assert updated_struct.field_a == "initial"


def test_update_config_from_dict_type_coercion_or_error():
    struct_instance = ExampleStruct(field_a="initial", field_b=10)
    updates = {"field_b": "not_an_int"}  # Type mismatch for field_b

    with pytest.raises(msgspec.ValidationError):  # msgspec.convert should raise this
        update_config_from_dict(struct_instance, updates)

    # Test case: update with a compatible type (e.g. float for an int field, if conversion is supported)
    # msgspec is strict by default.
    # updates_compatible = {"field_b": 20.0} # float
    # updated_struct_compat = update_config_from_dict(struct_instance, updates_compatible)
    # assert updated_struct_compat.field_b == 20 # Should be converted to int


class StructWithExtraFields(msgspec.Struct, kw_only=True, gc=False):
    known_field: str


def test_update_config_from_dict_struct_with_extra_fields_gc_false():
    struct_instance = StructWithExtraFields(known_field="hello")
    # Add an extra field to the instance (possible because gc=False)
    struct_instance.extra = 123  # type: ignore

    updates = {"known_field": "world", "new_extra": 456, "extra": 789}

    # Convert to dict, update, convert back
    # 1. struct_instance to dict: {'known_field': 'hello', 'extra': 123}
    # 2. updates applied: {'known_field': 'world', 'extra': 789, 'new_extra': 456}
    # 3. convert back to StructWithExtraFields
    updated_struct = update_config_from_dict(struct_instance, updates)

    assert updated_struct.known_field == "world"
    assert getattr(updated_struct, "extra") == 789
    assert getattr(updated_struct, "new_extra") == 456


# It's important to note that update_config_from_dict as implemented
# first converts the entire struct to a dict, then updates this dict using
# the update_nested_dict logic, and then converts it back to the struct type.
# This means if a field in the `updates` dict is a complex object that should
# replace a field in the struct, but that field in the struct is also a struct,
# the update_nested_dict will try to merge them as dicts, which might not be
# the intended behavior if a full replacement was expected for that sub-object.
# However, the current implementation seems to handle nested msgspec.Structs correctly
# because msgspec.convert will re-validate and structure the data.


def test_update_config_from_dict_original_struct_unmodified():
    original_nested = NestedStruct(value1=1, value2="orig_nested")
    struct_instance = ExampleStruct(
        field_a="original_a", field_b=5, nested=original_nested
    )

    updates = {"field_b": 50, "nested": {"value1": 10}}

    updated_struct = update_config_from_dict(struct_instance, updates)

    # Check updated struct
    assert updated_struct.field_b == 50
    assert updated_struct.nested.value1 == 10
    assert (
        updated_struct.nested.value2 == "orig_nested"
    )  # from original nested, as only value1 was updated

    # Check original struct and its nested component are unmodified
    assert struct_instance.field_a == "original_a"
    assert struct_instance.field_b == 5
    assert (
        struct_instance.nested is original_nested
    )  # Should ideally be a copy, but current code reuses if not updated
    assert struct_instance.nested.value1 == 1
    assert struct_instance.nested.value2 == "orig_nested"

    # If nested is updated, msgspec.convert will create new nested instances.
    # Let's verify the IDs if the nested object itself is being updated.
    original_nested_id = id(struct_instance.nested)
    if "nested" in updates:
        assert id(updated_struct.nested) != original_nested_id
    else:
        assert id(updated_struct.nested) == original_nested_id

    # More specific check for nested object identity
    struct_instance_2 = ExampleStruct(field_a="a", nested=NestedStruct(value1=1))
    updates_no_nested_change = {"field_a": "b"}
    updated_2 = update_config_from_dict(struct_instance_2, updates_no_nested_change)
    assert id(struct_instance_2.nested) == id(
        updated_2.nested
    )  # No change to nested, should be same obj

    updates_with_nested_change = {"nested": {"value1": 2}}
    updated_3 = update_config_from_dict(struct_instance_2, updates_with_nested_change)
    assert id(struct_instance_2.nested) != id(
        updated_3.nested
    )  # Change to nested, should be new obj
    assert updated_3.nested.value1 == 2
    assert struct_instance_2.nested.value1 == 1  # Original nested object unchanged
