# Implementation Result

ticket: flo-2n9o (child: flo-kv7v)
status: ready-for-validation

## Summary

Moved visualization-only image viewer helpers from `utils.misc` to a dedicated `utils.visualization` module. This completes the child task **flo-kv7v** of the epic **flo-2n9o**.

### Changes Made:
1. **Created new module** `src/flowerpower/utils/visualization.py` containing:
   - `_validate_image_format()` - Validates image format to prevent injection attacks
   - `_create_temp_image_file()` - Creates temporary file with image data
   - `_open_image_viewer()` - Opens image viewer with the given file path (cross-platform)
   - `_cleanup_temp_file()` - Cleans up temporary files
   - `view_img()` - Main function to view image data using system's default viewer

2. **Updated** `src/flowerpower/pipeline/visualizer.py`:
   - Changed import from `from ..utils.misc import view_img` to `from ..utils.visualization import view_img`

3. **Slimmed down** `src/flowerpower/utils/misc.py`:
   - Removed imports only used for image viewing: `os`, `subprocess`, `tempfile`, `time`, `validate_file_path`
   - Removed all image viewing helper functions
   - Now only contains `get_filesystem()` helper

4. **Updated tests**:
   - Created `tests/utils/test_visualization.py` with all visualization test cases
   - Updated `tests/utils/test_misc.py` to only test `get_filesystem()`

## Files Changed

- `src/flowerpower/utils/visualization.py` (new file)
- `src/flowerpower/pipeline/visualizer.py` (updated import)
- `src/flowerpower/utils/misc.py` (removed image viewing code)
- `tests/utils/test_visualization.py` (new file)
- `tests/utils/test_misc.py` (updated to remove visualization tests)

## Context Used

- `src/flowerpower/utils/misc.py` - Source file containing image viewing helpers
- `src/flowerpower/pipeline/visualizer.py` - Consumer of view_img
- `tests/utils/test_misc.py` - Existing tests to be split

## Validation

- deferred to `ticket-test-fix`

## Validation Evidence

```
$ python -m pytest tests/utils/test_visualization.py -v
============================= test session starts ==============================
platform darwin -- Python 3.12.8, pytest-8.4.2, pluggy-1.6.0
collected 12 items

tests/utils/test_visualization.py::TestValidateImageFormat::test_validate_image_format_valid PASSED
tests/utils/test_visualization.py::TestValidateImageFormat::test_validate_image_format_invalid PASSED
tests/utils/test_visualization.py::TestCreateTempImageFile::test_create_temp_image_file_string_data PASSED
tests/utils/test_visualization.py::TestCreateTempImageFile::test_create_temp_image_file_bytes_data PASSED
tests/utils/test_visualization.py::TestOpenImageViewer::test_open_image_viewer_macos PASSED
tests/utils/test_visualization.py::TestOpenImageViewer::test_open_image_viewer_linux PASSED
tests/utils/test_visualization.py::TestOpenImageViewer::test_open_image_viewer_windows PASSED
tests/utils/test_visualization.py::TestOpenImageViewer::test_open_image_viewer_unsupported_platform PASSED
tests/utils/test_visualization.py::TestCleanupTempFile::test_cleanup_temp_file_success PASSED
tests/utils/test_visualization.py::TestCleanupTempFile::test_cleanup_temp_file_error PASSED
tests/utils/test_visualization.py::TestViewImg::test_view_img_success PASSED
tests/utils/test_visualization.py::TestViewImg::test_view_img_open_error PASSED
============================== 12 passed in 1.86s =============================

$ python -m pytest tests/utils/test_misc.py -v
============================= test session starts ==============================
platform darwin -- Python 3.12.8, pytest-8.4.2, pluggy-1.6.0
collected 5 items

tests/utils/test_misc.py::TestGetFilesystem::test_get_filesystem_with_existing_fs PASSED
tests/utils/test_misc.py::TestGetFilesystem::test_get_filesystem_with_none_fs_default_type PASSED
tests/utils/test_misc.py::TestGetFilesystem::test_get_filesystem_with_none_fs_custom_type PASSED
tests/utils/test_misc.py::TestGetFilesystem::test_get_filesystem_with_different_fs_types PASSED
tests/utils/test_misc.py::TestGetFilesystem::test_get_filesystem_real_filesystem PASSED
============================== 5 passed in 0.58s =============================

$ python -c "from flowerpower.pipeline.visualizer import PipelineVisualizer; print('Import successful')"
Import successful
```

## Remaining Issues

- none
