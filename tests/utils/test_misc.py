from unittest.mock import MagicMock, patch

from fsspec.implementations.local import LocalFileSystem
from fsspec.implementations.memory import MemoryFileSystem

from flowerpower.cfg.pipeline.run import ExecutorConfig
from flowerpower.utils.executor import ExecutorFactory
from flowerpower.utils.misc import dict_to_namespace, get_filesystem


class TestExecutorFactoryCache:
    def test_cache_returns_same_instance_for_same_config(self) -> None:
        """Same config should return the same executor instance (cache hit)."""
        factory = ExecutorFactory()
        cfg = ExecutorConfig(type="synchronous")

        executor1 = factory.create_executor(cfg)
        executor2 = factory.create_executor(cfg)

        assert executor1 is executor2

    def test_cache_evicts_oldest_entries(self) -> None:
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

    def test_clear_cache_creates_new_instances(self) -> None:
        """clear_cache should invalidate cached entries."""
        factory = ExecutorFactory()
        cfg = ExecutorConfig(type="synchronous")

        executor1 = factory.create_executor(cfg)
        factory.clear_cache()
        executor2 = factory.create_executor(cfg)

        assert executor1 is not executor2


class TestDictToNamespace:
    """Tests for dict_to_namespace and DictNamespace."""

    def test_attribute_access(self) -> None:
        """Top-level keys are accessible as attributes."""
        ns = dict_to_namespace({"fs": "s3", "batch_size": 32})

        assert ns.fs == "s3"
        assert ns.batch_size == 32

    def test_bracket_access(self) -> None:
        """Dict-style bracket access remains available for reading."""
        ns = dict_to_namespace({"fs": "s3", "batch_size": 32})

        assert ns["fs"] == "s3"
        assert ns["batch_size"] == 32

    def test_nested_dicts(self) -> None:
        """Nested dictionaries are recursively converted."""
        ns = dict_to_namespace(
            {
                "model": {"name": "resnet", "layers": 50},
                "optimizer": {"lr": 0.01, "type": "adam"},
            }
        )

        assert ns.model.name == "resnet"
        assert ns.model.layers == 50
        assert ns.optimizer.lr == 0.01
        assert ns.optimizer.type == "adam"
        assert ns["model"]["name"] == "resnet"

    def test_lists_with_dicts(self) -> None:
        """Lists containing dictionaries are recursively converted."""
        ns = dict_to_namespace(
            {"transforms": [{"name": "resize"}, {"name": "normalize"}]}
        )

        assert isinstance(ns.transforms, list)
        assert ns.transforms[0].name == "resize"
        assert ns.transforms[1].name == "normalize"
        assert ns["transforms"][0]["name"] == "resize"

    def test_non_dict_values_preserved(self) -> None:
        """Primitives, lists, and other values are passed through."""
        ns = dict_to_namespace({"count": 42, "names": ["a", "b"], "flag": True})

        assert ns.count == 42
        assert ns.names == ["a", "b"]
        assert ns.flag is True

    def test_invalid_identifier_keys(self) -> None:
        """Keys that are not valid identifiers work via bracket access."""
        ns = dict_to_namespace({"123": "numeric", "foo-bar": "dash"})

        assert ns["123"] == "numeric"
        assert ns["foo-bar"] == "dash"

    def test_kwargs_unpacking(self) -> None:
        """Namespaces can be unpacked with ** for use in decorators."""
        ns = dict_to_namespace({"fs": "s3", "batch_size": 32})

        assert {**ns} == {"fs": "s3", "batch_size": 32}

    def test_special_keys(self) -> None:
        """Keys that collide with namespace internals remain accessible."""
        ns = dict_to_namespace({"__dict__": "value", "__class__": "klass"})

        assert ns["__dict__"] == "value"
        assert ns["__class__"] == "klass"


class TestGetFilesystem:
    def test_get_filesystem_with_existing_fs(self) -> None:
        mock_fs = MagicMock(spec=MemoryFileSystem)
        assert get_filesystem(mock_fs) is mock_fs

    def test_get_filesystem_with_none_fs_default_type(self) -> None:
        with patch("flowerpower.utils.misc.filesystem") as mock_filesystem:
            mock_fs = MagicMock(spec=LocalFileSystem)
            mock_filesystem.return_value = mock_fs

            result = get_filesystem(fs=None)

            mock_filesystem.assert_called_once_with("file")
            assert result is mock_fs

    def test_get_filesystem_with_none_fs_custom_type(self) -> None:
        with patch("flowerpower.utils.misc.filesystem") as mock_filesystem:
            mock_fs = MagicMock(spec=MemoryFileSystem)
            mock_filesystem.return_value = mock_fs

            result = get_filesystem(fs=None, fs_type="memory")

            mock_filesystem.assert_called_once_with("memory")
            assert result is mock_fs

    def test_get_filesystem_with_different_fs_types(self) -> None:
        with patch("flowerpower.utils.misc.filesystem") as mock_filesystem:
            mock_fs = MagicMock()
            mock_filesystem.return_value = mock_fs

            for fs_type in ["file", "memory", "s3", "gcs"]:
                result = get_filesystem(fs=None, fs_type=fs_type)
                mock_filesystem.assert_called_with(fs_type)
                assert result is mock_fs
                mock_filesystem.reset_mock()



