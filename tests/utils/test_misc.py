from unittest.mock import MagicMock, patch

from fsspec.implementations.local import LocalFileSystem
from fsspec.implementations.memory import MemoryFileSystem

from flowerpower.cfg.pipeline.run import ExecutorConfig
from flowerpower.utils.executor import ExecutorFactory
from flowerpower.utils.misc import get_filesystem


class TestExecutorFactoryCache:
    def test_cache_returns_same_instance_for_same_config(self):
        """Same config should return the same executor instance (cache hit)."""
        factory = ExecutorFactory()
        cfg = ExecutorConfig(type="synchronous")

        executor1 = factory.create_executor(cfg)
        executor2 = factory.create_executor(cfg)

        assert executor1 is executor2

    def test_cache_evicts_oldest_entries(self):
        """Cache should evict oldest entries when maxsize exceeded."""
        factory = ExecutorFactory()
        maxsize = factory._create_cached_executor.cache_info().maxsize

        executors = []
        for i in range(maxsize + 1):
            cfg = ExecutorConfig(type="synchronous", max_workers=i)
            executors.append(factory.create_executor(cfg))

        info = factory._create_cached_executor.cache_info()
        assert info.currsize == maxsize
        # First entry should have been evicted
        first_cfg = ExecutorConfig(type="synchronous", max_workers=0)
        new_executor = factory.create_executor(first_cfg)
        assert new_executor is not executors[0]

    def test_clear_cache_creates_new_instances(self):
        """clear_cache should invalidate cached entries."""
        factory = ExecutorFactory()
        cfg = ExecutorConfig(type="synchronous")

        executor1 = factory.create_executor(cfg)
        factory.clear_cache()
        executor2 = factory.create_executor(cfg)

        assert executor1 is not executor2


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



