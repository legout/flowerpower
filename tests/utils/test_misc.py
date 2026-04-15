from unittest.mock import MagicMock, patch

from fsspec.implementations.local import LocalFileSystem
from fsspec.implementations.memory import MemoryFileSystem

from flowerpower.utils.misc import get_filesystem, view_img
from flowerpower.utils.visualization import view_img as canonical_view_img


class TestGetFilesystem:
    def test_get_filesystem_with_existing_fs(self):
        mock_fs = MagicMock(spec=MemoryFileSystem)
        assert get_filesystem(mock_fs) is mock_fs

    def test_get_filesystem_with_none_fs_default_type(self):
        with patch("flowerpower.utils.misc.filesystem") as mock_filesystem:
            mock_fs = MagicMock(spec=LocalFileSystem)
            mock_filesystem.return_value = mock_fs

            result = get_filesystem(fs=None)

            mock_filesystem.assert_called_once_with("file")
            assert result is mock_fs

    def test_get_filesystem_with_none_fs_custom_type(self):
        with patch("flowerpower.utils.misc.filesystem") as mock_filesystem:
            mock_fs = MagicMock(spec=MemoryFileSystem)
            mock_filesystem.return_value = mock_fs

            result = get_filesystem(fs=None, fs_type="memory")

            mock_filesystem.assert_called_once_with("memory")
            assert result is mock_fs

    def test_get_filesystem_with_different_fs_types(self):
        with patch("flowerpower.utils.misc.filesystem") as mock_filesystem:
            mock_fs = MagicMock()
            mock_filesystem.return_value = mock_fs

            for fs_type in ["file", "memory", "s3", "gcs"]:
                result = get_filesystem(fs=None, fs_type=fs_type)
                mock_filesystem.assert_called_with(fs_type)
                assert result is mock_fs
                mock_filesystem.reset_mock()


def test_misc_view_img_reexports_canonical_helper():
    assert view_img is canonical_view_img
