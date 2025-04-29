import warnings

warnings.warn(
    "`flowerpower.mqtt` is deprecated, use `flowerpower.plugins.mqtt` instead",
    DeprecationWarning,
    stacklevel=2
)

from flowerpower.plugins.mqtt import MqttConfig, MqttManager, MQTTManager #noqa: E402

__all__ = ["MqttConfig", "MqttManager", "MQTTManager"]
