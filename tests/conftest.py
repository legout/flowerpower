import os
import shutil
import tempfile
from pathlib import Path

import pytest
import fsspec

@pytest.fixture
def temp_project_dir():
    """Create a temporary directory for testing.
    
    This fixture creates a temporary directory and changes the current working
    directory to it. After the test is complete, it changes back to the original
    directory and removes the temporary one.
    
    Returns:
        Path: Path to the temporary directory
    """
    # Store the current working directory
    original_cwd = Path.cwd()
    
    # Create a temporary directory
    temp_dir = Path(tempfile.mkdtemp())
    
    try:
        # Change to the temporary directory
        os.chdir(temp_dir)
        # Yield the path to the temporary directory
        yield temp_dir
    finally:
        # Always change back to the original directory
        os.chdir(original_cwd)
        # Clean up the temporary directory
        shutil.rmtree(temp_dir)

@pytest.fixture
def memory_fs():
    """Create an in-memory filesystem using fsspec.

    This fixture provides a fsspec memory filesystem for testing filesystem
    operations without writing to disk.

    Returns:
        fsspec.filesystem: An in-memory filesystem instance
    """
    fs = fsspec.filesystem("memory")
    yield fs
    fs.store.clear()  # Clean up after test
