# tests/pipelines/test_pipeline_module.py


def input_data() -> int:
    return 10


def intermediate_value(input_data: int) -> int:
    return input_data * 2


def output_value(intermediate_value: int) -> int:
    return intermediate_value + 5


def another_output(input_data: int, intermediate_value: int) -> dict:
    return {"input": input_data, "intermediate": intermediate_value}


_flaky_attempts_count = 0


def reset_flaky_attempts() -> None:
    """Resets the attempt counter for flaky_function."""
    global _flaky_attempts_count
    _flaky_attempts_count = 0


def flaky_function(input_data: int) -> int:
    """
    A function that simulates failure for the first few attempts.
    Succeeds on the 3rd attempt.
    """
    global _flaky_attempts_count
    _flaky_attempts_count += 1
    if _flaky_attempts_count < 3:  # Fails the first two times
        raise ValueError(f"Simulated failure on attempt {_flaky_attempts_count}")
    return input_data + 5


def output_from_flaky(flaky_function: int) -> int:
    """Consumes the output of flaky_function."""
    return flaky_function


def always_fails(input_data: int) -> int:
    """A function that always raises an exception."""
    raise ValueError("This will always fail")


def output_from_always_fails(always_fails: int) -> int:
    """Consumes the output of always_fails. This should ideally not be reached in tests."""
    return always_fails
