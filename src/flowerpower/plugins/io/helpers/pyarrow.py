import pyarrow as pa
import polars as pl
from .opt_dtype import opt_dtype_pa 
opt_dtype = opt_dtype_pa

def unify_schemas(schemas: list[pa.Schema], use_large_dtypes:bool=False) -> pa.Schema:
    """
    Unify a list of PyArrow schemas into a single schema.

    Args:
        schemas: List of PyArrow schemas to unify.

    Returns:
        A unified PyArrow schema.
    """
    try:
        return pa.unify_schemas(schemas, promote_options="permissive")
    except (pa.lib.ArrowInvalid, pa.lib.ArrowTypeError) as e:
        _ = e.args[0]
        # If unify_schemas fails, we can try to create a schema with empty tables
        schema =  (
            pl.concat(
                [
                    # pl.from_arrow(pa.Table.from_pylist([], schema=schema))
                    pl.from_arrow(schema.empty_table())
                    for schema in schemas
                ],
                how="diagonal_relaxed",
            )
            .to_arrow()
            .schema
        )
        if not use_large_dtypes:
            return convert_large_types_to_normal(schema)
        return schema

def cast_schema(table: pa.Table, schema: pa.Schema) -> pa.Table:
    """
    Cast a PyArrow table to a given schema, updating the schema to match the table's columns.

    Args:
        table: The PyArrow table to cast.
        schema: The target schema to cast the table to.

    Returns:
        A new PyArrow table with the specified schema.
    """
    # Filter schema fields to only those present in the table
    table_columns = set(table.schema.names)
    filtered_fields = [field for field in schema if field.name in table_columns]
    updated_schema = pa.schema(filtered_fields)
    return table.select(updated_schema.names).cast(updated_schema)

def convert_large_types_to_normal(schema: pa.Schema) -> pa.Schema:
    # Define mapping of large types to standard types
    type_mapping = {
        pa.large_string(): pa.string(),
        pa.large_binary(): pa.binary(),
        pa.large_utf8(): pa.utf8(),
        pa.large_list(pa.null()): pa.list_(pa.null()),
        pa.large_list_view(pa.null()): pa.list_view(pa.null()),
    }
    # Convert fields
    new_fields = []
    for field in schema:
        field_type = field.type
        # Check if type exists in mapping
        if field_type in type_mapping:
            new_field = pa.field(
                name=field.name,
                type=type_mapping[field_type],
                nullable=field.nullable,
                metadata=field.metadata,
            )
            new_fields.append(new_field)
        # Handle large lists with nested types
        elif isinstance(field_type, pa.LargeListType):
            new_field = pa.field(
                name=field.name,
                type=pa.list_(
                    type_mapping[field_type.value_type]
                    if field_type.value_type in type_mapping
                    else field_type.value_type
                ),
                nullable=field.nullable,
                metadata=field.metadata,
            )
            new_fields.append(new_field)
        # Handle dictionary with large_string, large_utf8, or large_binary values
        elif isinstance(field_type, pa.DictionaryType):
            new_field = pa.field(
                name=field.name,
                type=pa.dictionary(
                    field_type.index_type,
                    type_mapping[field_type.value_type]
                    if field_type.value_type in type_mapping
                    else field_type.value_type,
                    field_type.ordered,
                ),
                # nullable=field.nullable,
                metadata=field.metadata,
            )
            new_fields.append(new_field)
        else:
            new_fields.append(field)

    return pa.schema(new_fields)
