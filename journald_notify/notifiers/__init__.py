from .command import CommandNotifier
from .notifier import Notifier
from .notifier_group import NotifierGroup
from .notifysend import NotifySendNotifier
from .pushbullet import PushbulletNotifier
from .smtp import SMTPNotifier
from .sentry import SentryNotifier
from .stdout import StdoutNotifier
from .._config import ConfigError


class NotifierFactory(object):
    TYPE_MAPPING = {
        "notify-send": NotifySendNotifier,
        "pushbullet": PushbulletNotifier,
        "smtp": SMTPNotifier,
        "sentry": SentryNotifier,
        "stdout": StdoutNotifier,
        "command": CommandNotifier,
    }

    def __init__(self, logger):
        self._logger = logger

    def create_notifiers(self, notifier_config):
        notifier_group = NotifierGroup(self._logger)
        for name, _notifier in notifier_config.items():
            if "type" not in _notifier:
                raise ConfigError("Missing notifer type")
            if "enabled" in _notifier and _notifier["enabled"] == False:
                continue
            if _notifier["type"] not in NotifierFactory.TYPE_MAPPING:
                raise ConfigError("Unknown notifer type {}".format(_notifier["type"]))

            klass = NotifierFactory.TYPE_MAPPING[_notifier["type"]]
            notifier_group.add_notifier(name, klass(self._logger, **_notifier.get("config", {})))
        return notifier_group
