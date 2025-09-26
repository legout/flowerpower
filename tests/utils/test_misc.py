import pytest
from unittest.mock import MagicMock, patch, mock_open
import tempfile
import os
import subprocess
import platform

from fsspec.implementations.memory import MemoryFileSystem
from fsspec.implementations.local import LocalFileSystem

from flowerpower.utils.misc import get_filesystem, view_img, _validate_image_format, _create_temp_image_file, _open_image_viewer, _cleanup_temp_file


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


class TestViewImg:
    """Test cases for the view_img function and its helpers."""

    def test_validate_image_format_valid(self):
        """Test that _validate_image_format accepts valid formats."""
        valid_formats = ["svg", "png", "jpg", "jpeg", "gif", "pdf", "html"]
        for fmt in valid_formats:
            result = _validate_image_format(fmt)
            assert result == fmt

    def test_validate_image_format_invalid(self):
        """Test that _validate_image_format rejects invalid formats."""
        invalid_formats = ["exe", "txt", "doc", "mp3", ""]
        for fmt in invalid_formats:
            with pytest.raises(ValueError, match=f"Unsupported format: {fmt}"):
                _validate_image_format(fmt)

    @patch('flowerpower.utils.misc.tempfile.NamedTemporaryFile')
    @patch('flowerpower.utils.misc.validate_file_path')
    def test_create_temp_image_file_string_data(self, mock_validate, mock_tempfile):
        """Test _create_temp_image_file with string data."""
        mock_tmp = MagicMock()
        mock_tmp.name = "/tmp/test.svg"
        mock_tempfile.return_value.__enter__.return_value = mock_tmp
        
        result = _create_temp_image_file("test data", "svg")
        
        mock_tmp.write.assert_called_once_with("test data".encode('utf-8'))
        mock_validate.assert_called_once_with("/tmp/test.svg", allow_relative=False)
        assert result == "/tmp/test.svg"

    @patch('flowerpower.utils.misc.tempfile.NamedTemporaryFile')
    @patch('flowerpower.utils.misc.validate_file_path')
    def test_create_temp_image_file_bytes_data(self, mock_validate, mock_tempfile):
        """Test _create_temp_image_file with bytes data."""
        mock_tmp = MagicMock()
        mock_tmp.name = "/tmp/test.png"
        mock_tempfile.return_value.__enter__.return_value = mock_tmp
        
        result = _create_temp_image_file(b"test data", "png")
        
        mock_tmp.write.assert_called_once_with(b"test data")
        mock_validate.assert_called_once_with("/tmp/test.png", allow_relative=False)
        assert result == "/tmp/test.png"

    @patch('subprocess.run')
    @patch('platform.system')
    def test_open_image_viewer_macos(self, mock_platform, mock_subprocess):
        """Test _open_image_viewer on macOS."""
        mock_platform.return_value = "Darwin"
        
        _open_image_viewer("/tmp/test.svg")
        
        mock_subprocess.assert_called_once_with(
            ["open", "/tmp/test.svg"], check=True, timeout=10
        )

    @patch('subprocess.run')
    @patch('platform.system')
    def test_open_image_viewer_linux(self, mock_platform, mock_subprocess):
        """Test _open_image_viewer on Linux."""
        mock_platform.return_value = "Linux"
        
        _open_image_viewer("/tmp/test.png")
        
        mock_subprocess.assert_called_once_with(
            ["xdg-open", "/tmp/test.png"], check=True, timeout=10
        )

    @patch('subprocess.run')
    @patch('platform.system')
    def test_open_image_viewer_windows(self, mock_platform, mock_subprocess):
        """Test _open_image_viewer on Windows."""
        mock_platform.return_value = "Windows"
        
        _open_image_viewer("/tmp/test.jpg")
        
        mock_subprocess.assert_called_once_with(
            ["start", "", "/tmp/test.jpg"], shell=True, check=True, timeout=10
        )

    @patch('platform.system')
    def test_open_image_viewer_unsupported_platform(self, mock_platform):
        """Test _open_image_viewer on unsupported platform."""
        mock_platform.return_value = "UnsupportedOS"
        
        with pytest.raises(OSError, match="Unsupported platform: UnsupportedOS"):
            _open_image_viewer("/tmp/test.gif")

    @patch('flowerpower.utils.misc.os.unlink')
    def test_cleanup_temp_file_success(self, mock_unlink):
        """Test _cleanup_temp_file successful cleanup."""
        _cleanup_temp_file("/tmp/test.svg")
        mock_unlink.assert_called_once_with("/tmp/test.svg")

    @patch('flowerpower.utils.misc.os.unlink')
    def test_cleanup_temp_file_error(self, mock_unlink):
        """Test _cleanup_temp_file handles OSError gracefully."""
        mock_unlink.side_effect = OSError("File not found")
        
        # Should not raise an exception
        _cleanup_temp_file("/tmp/nonexistent.svg")
        mock_unlink.assert_called_once_with("/tmp/nonexistent.svg")

    @patch('flowerpower.utils.misc._validate_image_format')
    @patch('flowerpower.utils.misc._create_temp_image_file')
    @patch('flowerpower.utils.misc._open_image_viewer')
    @patch('flowerpower.utils.misc._cleanup_temp_file')
    @patch('flowerpower.utils.misc.time.sleep')
    def test_view_img_success(self, mock_sleep, mock_cleanup, mock_open, mock_create, mock_validate):
        """Test view_img successful execution."""
        mock_validate.return_value = "svg"
        mock_create.return_value = "/tmp/test.svg"
        
        view_img("test data", "svg")
        
        mock_validate.assert_called_once_with("svg")
        mock_create.assert_called_once_with("test data", "svg")
        mock_open.assert_called_once_with("/tmp/test.svg")
        mock_sleep.assert_called_once_with(2)
        mock_cleanup.assert_called_once_with("/tmp/test.svg")

    @patch('flowerpower.utils.misc._validate_image_format')
    @patch('flowerpower.utils.misc._create_temp_image_file')
    @patch('flowerpower.utils.misc._open_image_viewer')
    @patch('flowerpower.utils.misc._cleanup_temp_file')
    def test_view_img_open_error(self, mock_cleanup, mock_open, mock_create, mock_validate):
        """Test view_img handles opening errors gracefully."""
        mock_validate.return_value = "png"
        mock_create.return_value = "/tmp/test.png"
        mock_open.side_effect = subprocess.CalledProcessError(1, "xdg-open")
        
        with pytest.raises(RuntimeError, match="Failed to open file"):
            view_img("test data", "png")
        
        # Cleanup should be called on error
        mock_cleanup.assert_called_once_with("/tmp/test.png")