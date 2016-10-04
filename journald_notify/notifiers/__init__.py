from .notifier import Notifier
from .notifier_group import NotifierGroup
from .pushbullet import PushbulletNotifier
from .smtp import SMTPNotifier
from .stdout import StdoutNotifier
from .._config import ConfigError


def create_notifiers(notifier_config):
    notifier_group = NotifierGroup()
    for _notifier in notifier_config:
        if "type" not in n:
            raise ConfigError("Missing notifer type")
        if "enabled" in _notfier and _notifier["enabled"] == False:
            continue

        if _notifier["type"] == "pushbullet":
            notifier_group.add_notifier(PushbulletNotifier(**_notifier["config"]))
        elif _notifier["type"] == "smtp":
            notifier_group.add_notifier(SMTPNotifier(**_notifier["config"]))
        elif _notifier["type"] == "stdout":
            notifier_group.add_notifier(StdoutNotifier())
        else:
            raise ConfigError("Unknown notifer type {}".format(_notifier["type"]))
    return notifier_group
