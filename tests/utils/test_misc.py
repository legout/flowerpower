import pytest
from unittest.mock import MagicMock, patch

from fsspec.implementations.memory import MemoryFileSystem
from fsspec.implementations.local import LocalFileSystem

from flowerpower.utils.misc import get_filesystem


class TestGetFilesystem:
    """Test cases for the get_filesystem helper function."""

    def test_get_filesystem_with_existing_fs(self):
        """Test that get_filesystem returns the provided filesystem instance."""
        mock_fs = MagicMock(spec=MemoryFileSystem)
        result = get_filesystem(mock_fs)
        assert result is mock_fs

    def test_get_filesystem_with_none_fs_default_type(self):
        """Test that get_filesystem creates a new filesystem when fs is None and using default fs_type."""
        with patch('flowerpower.utils.misc.filesystem') as mock_filesystem_func:
            mock_fs = MagicMock(spec=LocalFileSystem)
            mock_filesystem_func.return_value = mock_fs
            
            result = get_filesystem(fs=None)
            
            mock_filesystem_func.assert_called_once_with("file")
            assert result is mock_fs

    def test_get_filesystem_with_none_fs_custom_type(self):
        """Test that get_filesystem creates a new filesystem with custom fs_type when fs is None."""
        with patch('flowerpower.utils.misc.filesystem') as mock_filesystem_func:
            mock_fs = MagicMock(spec=MemoryFileSystem)
            mock_filesystem_func.return_value = mock_fs
            
            result = get_filesystem(fs=None, fs_type="memory")
            
            mock_filesystem_func.assert_called_once_with("memory")
            assert result is mock_fs

    def test_get_filesystem_with_different_fs_types(self):
        """Test get_filesystem with different filesystem types."""
        with patch('flowerpower.utils.misc.filesystem') as mock_filesystem_func:
            mock_fs = MagicMock()
            mock_filesystem_func.return_value = mock_fs
            
            # Test with different fs_type values
            for fs_type in ["file", "memory", "s3", "gcs"]:
                result = get_filesystem(fs=None, fs_type=fs_type)
                mock_filesystem_func.assert_called_with(fs_type)
                assert result is mock_fs
                mock_filesystem_func.reset_mock()

    def test_get_filesystem_real_filesystem(self):
        """Test get_filesystem with real filesystem creation."""
        # Test with actual filesystem creation (no mocking)
        # Use fsspec directly for memory filesystem since fsspec_utils doesn't support memory protocol
        from fsspec.implementations.memory import MemoryFileSystem
        from fsspec.implementations.local import LocalFileSystem
        from fsspec.implementations.dirfs import DirFileSystem
        
        fs = get_filesystem(fs=None, fs_type="file")
        assert isinstance(fs, DirFileSystem)
        assert isinstance(fs.fs, LocalFileSystem)
        
        # Test with a real memory filesystem instance
        memory_fs = MemoryFileSystem()
        result_fs = get_filesystem(memory_fs)
        assert result_fs is memory_fs