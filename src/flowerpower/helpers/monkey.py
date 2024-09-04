import sys

from dill import dumps, loads
# from cloudpickle import dumps, loads


def patch_pickle():
    """
    Patch the pickle serializer in the apscheduler module.

    This function replaces the `dumps` and `loads` functions in the `apscheduler.serializers.pickle` module
    with custom implementations.

    This is useful when you want to modify the behavior of the pickle serializer used by the apscheduler module.

    Example usage:
    patch_pickle()

    """
    sys.modules["apscheduler.serializers.pickle"].dumps = dumps
    sys.modules["apscheduler.serializers.pickle"].loads = loads
