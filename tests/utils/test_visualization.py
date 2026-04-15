"""Tests for visualization utilities."""

import subprocess
from unittest.mock import MagicMock, patch

import pytest

from flowerpower.utils.visualization import (
    view_img,
    _validate_image_format,
    _create_temp_image_file,
    _open_image_viewer,
    _cleanup_temp_file,
)


class TestValidateImageFormat:
    """Test cases for _validate_image_format helper."""

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


class TestCreateTempImageFile:
    """Test cases for _create_temp_image_file helper."""

    @patch("flowerpower.utils.visualization.tempfile.NamedTemporaryFile")
    @patch("flowerpower.utils.visualization.validate_file_path")
    def test_create_temp_image_file_string_data(self, mock_validate, mock_tempfile):
        """Test _create_temp_image_file with string data."""
        mock_tmp = MagicMock()
        mock_tmp.name = "/tmp/test.svg"
        mock_tempfile.return_value.__enter__.return_value = mock_tmp

        result = _create_temp_image_file("test data", "svg")

        mock_tmp.write.assert_called_once_with("test data".encode("utf-8"))
        mock_validate.assert_called_once_with("/tmp/test.svg", allow_relative=False)
        assert result == "/tmp/test.svg"

    @patch("flowerpower.utils.visualization.tempfile.NamedTemporaryFile")
    @patch("flowerpower.utils.visualization.validate_file_path")
    def test_create_temp_image_file_bytes_data(self, mock_validate, mock_tempfile):
        """Test _create_temp_image_file with bytes data."""
        mock_tmp = MagicMock()
        mock_tmp.name = "/tmp/test.png"
        mock_tempfile.return_value.__enter__.return_value = mock_tmp

        result = _create_temp_image_file(b"test data", "png")

        mock_tmp.write.assert_called_once_with(b"test data")
        mock_validate.assert_called_once_with("/tmp/test.png", allow_relative=False)
        assert result == "/tmp/test.png"


class TestOpenImageViewer:
    """Test cases for _open_image_viewer helper."""

    @patch("subprocess.run")
    @patch("platform.system")
    def test_open_image_viewer_macos(self, mock_platform, mock_subprocess):
        """Test _open_image_viewer on macOS."""
        mock_platform.return_value = "Darwin"

        _open_image_viewer("/tmp/test.svg")

        mock_subprocess.assert_called_once_with(
            ["open", "/tmp/test.svg"], check=True, timeout=10
        )

    @patch("subprocess.run")
    @patch("platform.system")
    def test_open_image_viewer_linux(self, mock_platform, mock_subprocess):
        """Test _open_image_viewer on Linux."""
        mock_platform.return_value = "Linux"

        _open_image_viewer("/tmp/test.png")

        mock_subprocess.assert_called_once_with(
            ["xdg-open", "/tmp/test.png"], check=True, timeout=10
        )

    @patch("platform.system")
    @patch("flowerpower.utils.visualization.os.startfile", create=True)
    def test_open_image_viewer_windows(self, mock_startfile, mock_platform):
        """Test _open_image_viewer on Windows."""
        mock_platform.return_value = "Windows"

        _open_image_viewer("/tmp/test.jpg")

        mock_startfile.assert_called_once_with("/tmp/test.jpg")

    @patch("platform.system")
    def test_open_image_viewer_unsupported_platform(self, mock_platform):
        """Test _open_image_viewer on unsupported platform."""
        mock_platform.return_value = "UnsupportedOS"

        with pytest.raises(OSError, match="Unsupported platform: UnsupportedOS"):
            _open_image_viewer("/tmp/test.gif")


class TestCleanupTempFile:
    """Test cases for _cleanup_temp_file helper."""

    @patch("flowerpower.utils.visualization.os.unlink")
    def test_cleanup_temp_file_success(self, mock_unlink):
        """Test _cleanup_temp_file successful cleanup."""
        _cleanup_temp_file("/tmp/test.svg")
        mock_unlink.assert_called_once_with("/tmp/test.svg")

    @patch("flowerpower.utils.visualization.os.unlink")
    def test_cleanup_temp_file_error(self, mock_unlink):
        """Test _cleanup_temp_file handles OSError gracefully."""
        mock_unlink.side_effect = OSError("File not found")

        # Should not raise an exception
        _cleanup_temp_file("/tmp/nonexistent.svg")
        mock_unlink.assert_called_once_with("/tmp/nonexistent.svg")


class TestViewImg:
    """Test cases for the view_img function."""

    @patch("flowerpower.utils.visualization._validate_image_format")
    @patch("flowerpower.utils.visualization._create_temp_image_file")
    @patch("flowerpower.utils.visualization._open_image_viewer")
    @patch("flowerpower.utils.visualization._cleanup_temp_file")
    @patch("flowerpower.utils.visualization.time.sleep")
    def test_view_img_success(
        self, mock_sleep, mock_cleanup, mock_open, mock_create, mock_validate
    ):
        """Test view_img successful execution."""
        mock_validate.return_value = "svg"
        mock_create.return_value = "/tmp/test.svg"

        view_img("test data", "svg")

        mock_validate.assert_called_once_with("svg")
        mock_create.assert_called_once_with("test data", "svg")
        mock_open.assert_called_once_with("/tmp/test.svg")
        mock_sleep.assert_called_once_with(2)
        mock_cleanup.assert_called_once_with("/tmp/test.svg")

    @patch("flowerpower.utils.visualization._validate_image_format")
    @patch("flowerpower.utils.visualization._create_temp_image_file")
    @patch("flowerpower.utils.visualization._open_image_viewer")
    @patch("flowerpower.utils.visualization._cleanup_temp_file")
    def test_view_img_open_error(
        self, mock_cleanup, mock_open, mock_create, mock_validate
    ):
        """Test view_img handles opening errors gracefully."""
        mock_validate.return_value = "png"
        mock_create.return_value = "/tmp/test.png"
        mock_open.side_effect = subprocess.CalledProcessError(1, "xdg-open")

        with pytest.raises(RuntimeError, match="Failed to open file"):
            view_img("test data", "png")

        # Cleanup should be called on error
        mock_cleanup.assert_called_once_with("/tmp/test.png")
