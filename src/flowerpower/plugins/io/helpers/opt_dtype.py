

import polars as pl
import pyarrow as pa
import pyarrow.compute as pc
import numpy as np

def opt_dtype_pl(
    table: pl.DataFrame | pl.LazyFrame,
    include: str | list[str] | None = None,
    exclude: str | list[str] | None = None,
    strict: bool = True,
    shrink_dtype: bool = True,
    time_zone: str | None = None,
) -> pl.DataFrame | pl.LazyFrame:
    """Optimize dtypes of a Polars DataFrame or LazyFrame by inferring the best type from string data.

    Args:
        table: Polars DataFrame or LazyFrame to optimize.
        include: Columns to include in optimization. If None, all columns are included.
        exclude: Columns to exclude from optimization.
        strict: If True, raises an error on conversion failure; if False, returns original series.
        shrink_dtype: If True, attempts to shrink numeric dtypes to smaller types.
        time_zone: Optional time zone to use when parsing datetime strings.
                   If strings have timezones, they will be converted to this zone.
                   If strings are naive, they will be localized to this zone.

    Returns:
        Polars DataFrame or LazyFrame with optimized dtypes.
    """
    # Pre-compiled regex for performance
    # Handles optional sign, integers, floats (with '.' or ','), and scientific notation.
    NUMERIC_REGEX = r"^[-+]?[0-9]*[.,]?[0-9]+([eE][-+]?[0-9]+)?$"
    # Handles common boolean representations (case-insensitive).
    BOOLEAN_REGEX = r"^(true|false|1|0|yes|ja|no|nein|t|f|y|j|n)$"
    BOOLEAN_TRUE_REGEX = r"^(true|1|yes|ja|t|y|j)$"
    # A heuristic to identify columns that are likely dates. Polars' `to_datetime`
    # is flexible, so this check doesn't need to be exhaustive.
    DATETIME_REGEX = r"^\d{4}-\d{2}-\d{2}"


    def opt_dtype(
        df: pl.DataFrame,
        include: str | list[str] | None = None,
        exclude: str | list[str] | None = None,
        time_zone: str | None = None,
    ) -> pl.DataFrame:
        """
        Analyzes and optimizes the data types of a Polars DataFrame for performance
        and memory efficiency.

        This version includes:
        - Robust numeric, boolean, and datetime casting from strings.
        - Handling of whitespace and common null-like string values.
        - Casting of columns containing only nulls to pl.Int8.

        Args:
            df: The DataFrame to optimize.
            include: A list of columns to forcefully include in the optimization.
            exclude: A list of columns to exclude from the optimization.
            time_zone: Optional time zone for datetime parsing.

        Returns:
            An optimized Polars DataFrame with improved data types.
        """
        # Phase 1: Analysis - Determine columns to process and build a list of
        # transformation expressions without executing them immediately.
        if isinstance(include, str):
            include = [include]
        if isinstance(exclude, str):
            exclude = [exclude]

        cols_to_process = df.columns
        if include:
            cols_to_process = [col for col in include if col in df.columns]
        if exclude:
            cols_to_process = [col for col in cols_to_process if col not in exclude]

        expressions = []
        for col_name in cols_to_process:
            s = df[col_name]

            # NEW: If a column is entirely null, cast it to Int8 and skip other checks.
            if s.is_null().all():
                expressions.append(pl.col(col_name).cast(pl.Int8))
                continue
            
            dtype = s.dtype

            # 1. Optimize numeric columns by shrinking their size
            if dtype.is_numeric():
                expressions.append(pl.col(col_name).shrink_dtype())
                continue

            # 2. Optimize string columns by casting to more specific types
            if dtype == pl.Utf8:
                # Create a cleaned column expression that first strips whitespace, then
                # replaces common null-like strings.
                cleaned_col = (
                    pl.col(col_name)
                    .str.strip_chars()
                    .replace({"-": None, "": None, "None": None})
                )

                # Analyze a stripped, non-null version of the series to decide the cast type
                s_non_null = s.drop_nulls()
                if len(s_non_null) == 0:
                    # The column only contains nulls or null-like strings.
                    # Cast to Int8 as requested for all-null columns.
                    expressions.append(pl.col(col_name).cast(pl.Int8))
                    continue
                
                s_stripped_non_null = s_non_null.str.strip_chars()

                # Check for boolean type
                if s_stripped_non_null.str.to_lowercase().str.contains(BOOLEAN_REGEX).all():
                    expr = cleaned_col.str.to_lowercase().str.contains(BOOLEAN_TRUE_REGEX)
                    expressions.append(expr.alias(col_name))
                    continue
                
                # Check for numeric type
                if s_stripped_non_null.str.contains(NUMERIC_REGEX).all():
                    is_float = s_stripped_non_null.str.contains(r"[.,eE]").any()
                    numeric_col = cleaned_col.str.replace_all(",", ".")
                    if is_float:
                        expressions.append(numeric_col.cast(pl.Float64).shrink_dtype().alias(col_name))
                    else:
                        expressions.append(numeric_col.cast(pl.Int64).shrink_dtype().alias(col_name))
                    continue

                # Check for datetime type using a fast heuristic
                try:
                    if s_stripped_non_null.str.contains(DATETIME_REGEX).all():
                        expressions.append(cleaned_col.str.to_datetime(strict=False, time_unit='us', time_zone=time_zone).alias(col_name))
                        continue
                except pl.exceptions.PolarsError:
                    pass

        # Phase 2: Execution - If any optimizations were identified, apply them
        # all at once for maximum parallelism and performance.
        if not expressions:
            return df

        return df.with_columns(expressions)

    return opt_dtype(
        table,
        include=include,
        exclude=exclude,
        time_zone=time_zone,
        # Note: The 'strict' and 'shrink_dtype' parameters from opt_dtype_pl
        # are not directly passed to this nested opt_dtype's signature.
        # 'shrink_dtype' is used via .shrink_dtype() calls.
        # 'strict' (from opt_dtype_pl) is not currently implemented for string->datetime
        # conversion logic, which uses a hardcoded strict=False in to_datetime.
    )


def opt_dtype_pa(
    table: pa.Table,
    include: str | list[str] | None = None,
    exclude: str | list[str] | None = None,
    strict: bool = True,
    shrink_dtype: bool = True,
) -> pa.Table:
    """Optimize dtypes of a PyArrow Table by inferring the best type from string data.

    Args:
        table (pa.Table): The PyArrow Table to optimize.
        include (str | list[str], optional): Columns to include in optimization. Defaults to None.
        exclude (str | list[str], optional): Columns to exclude from optimization. Defaults to None.
        strict (bool, optional): Whether to raise errors on failed conversions. Defaults to True.
        shrink_dtype (bool, optional): Whether to attempt to shrink dtypes where possible. Defaults to True.
    
    Returns:
        pa.Table: A new PyArrow Table with optimized dtypes.
    """

    # Regex patterns (mirroring opt_dtype_pl)
    NUMERIC_REGEX = r"^[-+]?[0-9]*[.,]?[0-9]+([eE][-+]?[0-9]+)?$"
    BOOLEAN_REGEX = r"^(true|false|1|0|yes|ja|no|nein|t|f|y|j|n)$"
    BOOLEAN_TRUE_REGEX = r"^(true|1|yes|ja|t|y|j)$"
    DATETIME_REGEX = r"^\d{4}-\d{2}-\d{2}"

    NULL_PATTERN = r"^(-|None|NULL|null|NaN|nan|\s*)$"

    def _clean_nulls(arr: pa.Array) -> pa.Array:
        null_mask = pc.match_substring_regex(arr, NULL_PATTERN)
        return pc.if_else(null_mask, None, arr)

    def _is_all_null(arr: pa.Array) -> bool:
        return pc.all(pc.is_null(arr)).as_py()

    def _is_numeric(arr: pa.Array) -> bool:
        is_num = pc.match_substring_regex(arr, NUMERIC_REGEX)
        is_null = pc.is_null(arr)
        is_empty = pc.equal(arr, "")
        return pc.all(pc.or_(pc.or_(is_num, is_null), is_empty)).as_py()

    def _is_boolean(arr: pa.Array) -> bool:
        arr_lower = pc.utf8_lower(arr)
        is_bool = pc.match_substring_regex(arr_lower, BOOLEAN_REGEX)
        is_null = pc.is_null(arr)
        is_empty = pc.equal(arr, "")
        return pc.all(pc.or_(pc.or_(is_bool, is_null), is_empty)).as_py()

    def _is_datetime(arr: pa.Array) -> bool:
        is_dt = pc.match_substring_regex(arr, DATETIME_REGEX)
        is_null = pc.is_null(arr)
        is_empty = pc.equal(arr, "")
        return pc.all(pc.or_(pc.or_(is_dt, is_null), is_empty)).as_py()

    def _cast_numeric(arr: pa.Array, shrink_dtype: bool, strict: bool) -> pa.Array:
        arr = pc.replace_substring(arr, ",", ".")
        arr = _clean_nulls(arr)
        # If any value has a decimal or 'e', cast to float, else int
        has_decimal = pc.match_substring_regex(arr, r"[.,eE]")
        has_nan = pc.match_substring_regex(arr, r"NaN|nan")
        try:
            if pc.any(has_decimal).as_py() or pc.any(has_nan).as_py():
                float_arr = pc.cast(arr, pa.float64())
                return _shrink_float(float_arr) if shrink_dtype else float_arr
            else:
                int_arr = pc.cast(arr, pa.int64())
                return _shrink_int(int_arr) if shrink_dtype else int_arr
        except Exception as e:
            if strict:
                raise type(e)(f"{str(e)} Failed to cast to numeric. Consider setting `strict=False`.")
            return arr

    def _cast_boolean(arr: pa.Array) -> pa.Array:
        arr_lower = pc.utf8_lower(arr)
        is_true = pc.match_substring_regex(arr_lower, BOOLEAN_TRUE_REGEX)
        is_null = pc.is_null(arr)
        return pc.if_else(is_null, None, pc.if_else(is_true, True, False))

    def _cast_datetime(arr: pa.Array, strict: bool) -> pa.Array:
        try:
            return pc.strptime(arr, format=None, unit="us")
        except Exception:
            # Try common fallback formats
            for fmt in ["%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"]:
                try:
                    return pc.strptime(arr, format=fmt, unit="us")
                except Exception:
                    continue
            if strict:
                raise ValueError("Could not parse datetime strings")
            return arr

    def _shrink_float(arr: pa.Array) -> pa.Array:
        if not pa.types.is_floating(arr.type):
            return arr
        if _is_all_null(arr):
            return pa.array([None] * len(arr), type=pa.int8())
        valid = arr.filter(pc.is_valid(arr))
        if len(valid) == 0:
            return arr
        min_val = pc.min(valid).as_py()
        max_val = pc.max(valid).as_py()
        # float32 range: ±3.4028235e+38
        if (
            (abs(min_val) <= 3.4028235e38 or min_val == 0)
            and (abs(max_val) <= 3.4028235e38 or max_val == 0)
        ):
            return pc.cast(arr, pa.float32())
        return arr

    def _shrink_int(arr: pa.Array) -> pa.Array:
        if not pa.types.is_integer(arr.type):
            return arr
        if _is_all_null(arr):
            return pa.array([None] * len(arr), type=pa.int8())
        valid = arr.filter(pc.is_valid(arr))
        if len(valid) == 0:
            return arr
        min_val = pc.min(valid).as_py()
        max_val = pc.max(valid).as_py()
        if min_val >= 0:
            if max_val <= 255:
                return pc.cast(arr, pa.uint8())
            elif max_val <= 65535:
                return pc.cast(arr, pa.uint16())
            elif max_val <= 4294967295:
                return pc.cast(arr, pa.uint32())
            else:
                return pc.cast(arr, pa.uint64())
        else:
            if min_val >= -128 and max_val <= 127:
                return pc.cast(arr, pa.int8())
            elif min_val >= -32768 and max_val <= 32767:
                return pc.cast(arr, pa.int16())
            elif min_val >= -2147483648 and max_val <= 2147483647:
                return pc.cast(arr, pa.int32())
            else:
                return pc.cast(arr, pa.int64())

    def _optimize_array(arr: pa.Array, strict: bool, shrink_dtype: bool) -> pa.Array:
        # All-null: shrink to int8 unless timestamp/date/time
        if _is_all_null(arr):
            if pa.types.is_timestamp(arr.type) or pa.types.is_date(arr.type) or pa.types.is_time(arr.type):
                return arr
            return pa.array([None] * len(arr), type=pa.int8())
        # Non-string: shrink numeric types if requested
        if not pa.types.is_string(arr.type):
            if shrink_dtype:
                if pa.types.is_floating(arr.type):
                    return _shrink_float(arr)
                if pa.types.is_integer(arr.type):
                    return _shrink_int(arr)
            return arr
        # String: clean and infer
        arr = _clean_nulls(arr)
        arr_non_null = arr.filter(pc.is_valid(arr))
        if len(arr_non_null) == 0:
            return pa.array([None] * len(arr), type=pa.int8())
        # Boolean
        if _is_boolean(arr_non_null):
            return _cast_boolean(arr)
        # Numeric
        if _is_numeric(arr_non_null):
            return _cast_numeric(arr, shrink_dtype, strict)
        # Datetime
        if _is_datetime(arr_non_null):
            return _cast_datetime(arr, strict)
        # Fallback: keep as string
        return arr

    def _get_common_pyarrow_type(type_list: list[pa.DataType]) -> pa.DataType:
        """
        Determines a common PyArrow DataType that can represent all types in a list.
        Handles promotion for boolean, integer, float, timestamp, and string types.
        """
        if not type_list:
            return pa.null()

        # Filter out null types, but if all are null, return null
        non_null_types = [t for t in type_list if not pa.types.is_null(t)]
        if not non_null_types:
            return pa.null()  # All types were null

        if len(set(non_null_types)) == 1:
            return non_null_types[0]

        # Boolean promotion (all must be boolean)
        if all(pa.types.is_boolean(t) for t in non_null_types):
            return pa.bool_()

        # Integer promotion
        if all(pa.types.is_integer(t) for t in non_null_types):
            current_min_val_possible = float('inf')
            current_max_val_possible = float('-inf')

            for t in non_null_types:
                pd_dtype_str = t.to_pandas_dtype()
                type_info = np.iinfo(pd_dtype_str) # np.iinfo works for both signed and unsigned
                current_min_val_possible = min(current_min_val_possible, type_info.min)
                current_max_val_possible = max(current_max_val_possible, type_info.max)

            must_be_signed = current_min_val_possible < 0

            if must_be_signed:
                for bits in [8, 16, 32, 64]:
                    # Check against the numpy type equivalent for range
                    np_type_info = np.iinfo(getattr(np, f"int{bits}"))
                    if np_type_info.min <= current_min_val_possible and current_max_val_possible <= np_type_info.max:
                        return getattr(pa, f"int{bits}")()
                return pa.int64() # Fallback if somehow not covered (e.g., extremely large range beyond int64)
            else:  # Can be unsigned (current_min_val_possible >= 0)
                for bits in [8, 16, 32, 64]:
                    np_type_info = np.iinfo(getattr(np, f"uint{bits}"))
                    if np_type_info.min <= current_min_val_possible and current_max_val_possible <= np_type_info.max:
                        return getattr(pa, f"uint{bits}")()
                return pa.uint64() # Fallback

        # Floating point promotion
        if all(pa.types.is_floating(t) for t in non_null_types):
            if any(t == pa.float64() for t in non_null_types):
                return pa.float64()
            return pa.float32() # If all are float32

        # Timestamp promotion
        if all(pa.types.is_timestamp(t) for t in non_null_types):
            unit_order = {'s': 0, 'ms': 1, 'us': 2, 'ns': 3}
            final_unit_val = -1
            final_unit_str = 's' # Default to second, promote to finer
            for t in non_null_types:
                if unit_order[t.unit] > final_unit_val:
                    final_unit_val = unit_order[t.unit]
                    final_unit_str = t.unit
            
            # Timezone logic:
            # 1. If all TZs are identical (can be None), use that.
            # 2. If mix of None and one specific TZ, use that TZ.
            # 3. If multiple different non-None TZs, becomes naive (None TZ) - this matches original's implied behavior.
            #    A more robust system might convert to UTC or raise error.
            unique_tzs = set(t.tz for t in non_null_types)
            final_tz = None
            if len(unique_tzs) == 1:
                final_tz = unique_tzs.pop()
            else:
                non_none_tzs = set(tz for tz in unique_tzs if tz is not None)
                if len(non_none_tzs) == 1:
                    final_tz = non_none_tzs.pop()
                # If len(non_none_tzs) > 1 (conflicting TZs) or len(non_none_tzs) == 0 (all were None, already handled by unique_tzs.pop() if len was 1)
                # then final_tz remains None.
            return pa.timestamp(final_unit_str, tz=final_tz)

        # String promotion
        if all(pa.types.is_string(t) or pa.types.is_large_string(t) for t in non_null_types):
            if any(pa.types.is_large_string(t) for t in non_null_types):
                return pa.large_string()
            return pa.string()

        # Fallback for mixed types not covered above (e.g., int and float)
        # This path should ideally not be hit if upstream logic sends categorized type lists.
        is_numeric_mix = all(pa.types.is_integer(t) or pa.types.is_floating(t) for t in non_null_types) and \
                        any(pa.types.is_integer(t) for t in non_null_types) and \
                        any(pa.types.is_floating(t) for t in non_null_types)
        if is_numeric_mix:
            return pa.float64()

        # Ultimate fallback: if types are truly mixed and unpromotable (e.g. int and list)
        # or a type not handled above. Original code defaulted to string.
        # Consider raising a TypeError if no common ground found.
        # For now, maintaining string as the final fallback.
        # logging.warning(f"Could not find a specific common type for {non_null_types}, falling back to string.")
        return pa.string()

    def _clean_string_array_for_parsing(arr: pa.Array) -> pa.Array:
        # Trim whitespace and convert null-like patterns to nulls
        arr = pc.utf8_trim(arr, options=pc.TrimOptions(characters=" \t\n\r\v\f"))
        null_mask = pc.match_substring_regex(arr, r"^(-|None|NULL|null|NaN|nan|\s*)$")
        return pc.if_else(null_mask, None, arr)

    def _process_column_for_optimization(
        col: pa.ChunkedArray,
        strict: bool,
        shrink_dtype: bool,
    ) -> pa.ChunkedArray:
        # If not string, process/shrink and unify types
        if not pa.types.is_string(col.type):
            processed_chunks = []
            chunk_types = []
            for chunk in col.iterchunks():
                arr = chunk
                if shrink_dtype:
                    if pa.types.is_floating(arr.type):
                        arr = _shrink_float(arr)
                    elif pa.types.is_integer(arr.type):
                        arr = _shrink_int(arr)
                processed_chunks.append(arr)
                chunk_types.append(arr.type)
            common_type = _get_common_pyarrow_type(chunk_types)
            processed_chunks = [pc.cast(arr, common_type) if arr.type != common_type else arr for arr in processed_chunks]
            return pa.chunked_array(processed_chunks, type=common_type)

        # String column: two-pass strategy
        cleaned_chunks = []
        col_can_be_bool = True
        col_can_be_datetime = True
        col_can_be_numeric = True
        col_numeric_requires_float = False
        col_all_null = True

        # Analysis pass
        for chunk in col.iterchunks():
            cleaned = _clean_string_array_for_parsing(chunk)
            cleaned_chunks.append(cleaned)
            non_null = cleaned.filter(pc.is_valid(cleaned))
            if len(non_null) == 0:
                continue
            col_all_null = False
            # Analyze type
            if not _is_boolean(non_null):
                col_can_be_bool = False
            if not _is_datetime(non_null):
                col_can_be_datetime = False
            if not _is_numeric(non_null):
                col_can_be_numeric = False
            else:
                # If any value has decimal or 'e', require float
                has_decimal = pc.match_substring_regex(non_null, r"[.,eE]")
                if pc.any(has_decimal).as_py():
                    col_numeric_requires_float = True

        # Decide target type for column
        if col_all_null:
            target_type = pa.int8()
        elif col_can_be_bool:
            target_type = pa.bool_()
        elif col_can_be_datetime:
            target_type = pa.timestamp('us')
        elif col_can_be_numeric:
            target_type = pa.float64() if col_numeric_requires_float else pa.int64()
        else:
            target_type = pa.string()

        # Transformation pass
        transformed_chunks = []
        chunk_types = []
        any_chunk_failed = False
        for cleaned in cleaned_chunks:
            arr = cleaned
            try:
                if target_type == pa.int8():
                    arr = pa.array([None] * len(arr), type=pa.int8())
                elif target_type == pa.bool_():
                    arr = _cast_boolean(arr)
                elif pa.types.is_timestamp(target_type):
                    arr = _cast_datetime(arr, strict)
                elif pa.types.is_floating(target_type) or pa.types.is_integer(target_type):
                    arr = _cast_numeric(arr, shrink_dtype, strict)
                else:
                    arr = arr
                # If cast succeeded but type is not exactly target_type, cast
                if arr.type != target_type and target_type != pa.string():
                    arr = pc.cast(arr, target_type)
            except Exception:
                if strict:
                    raise
                arr = arr.cast(pa.string()) if not pa.types.is_string(arr.type) else arr
                any_chunk_failed = True
            transformed_chunks.append(arr)
            chunk_types.append(arr.type)

        # If strict=False and any chunk failed, fallback all to string
        if not strict and any_chunk_failed and target_type != pa.string():
            transformed_chunks = [pc.cast(arr, pa.string()) if not pa.types.is_string(arr.type) else arr for arr in transformed_chunks]
            target_type = pa.string()

        # Shrinking for numerics after fallback
        if shrink_dtype and (pa.types.is_floating(target_type) or pa.types.is_integer(target_type)):
            shrunk_chunks = []
            shrunk_types = []
            for arr in transformed_chunks:
                if pa.types.is_floating(arr.type):
                    arr = _shrink_float(arr)
                elif pa.types.is_integer(arr.type):
                    arr = _shrink_int(arr)
                shrunk_chunks.append(arr)
                shrunk_types.append(arr.type)
            common_type = _get_common_pyarrow_type(shrunk_types)
            shrunk_chunks = [pc.cast(arr, common_type) if arr.type != common_type else arr for arr in shrunk_chunks]
            return pa.chunked_array(shrunk_chunks, type=common_type)

        # Final assembly
        final_type = _get_common_pyarrow_type(chunk_types)
        transformed_chunks = [pc.cast(arr, final_type) if arr.type != final_type else arr for arr in transformed_chunks]
        return pa.chunked_array(transformed_chunks, type=final_type)

    def _optimize_table(
        table: pa.Table,
        include: str | list[str] | None,
        exclude: str | list[str] | None,
        strict: bool,
        shrink_dtype: bool,
    ) -> pa.Table:
        # Determine columns to process
        columns = list(table.column_names)
        if include is not None:
            if isinstance(include, str):
                include = [include]
            columns = [c for c in include if c in table.column_names]
        if exclude is not None:
            if isinstance(exclude, str):
                exclude = [exclude]
            columns = [c for c in columns if c not in exclude]
        # Build new columns
        col_dict = {}
        for col in table.column_names:
            if col in columns:
                col_dict[col] = _process_column_for_optimization(table[col], strict, shrink_dtype)
            else:
                col_dict[col] = table[col]
        return pa.table(col_dict)

    return _optimize_table(
        table,
        include=include,
        exclude=exclude,
        strict=strict,
        shrink_dtype=shrink_dtype,
    )
