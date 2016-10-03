from .notifier import Notifier
from .notifier_group import NotifierGroup
from .pushbullet import PushbulletNotifier
from .smtp import SMTPNotifier
from .stdout import StdoutNotifier
from .._config import ConfigError


def create_notifiers(notifier_config):
    notifier_group = NotifierGroup()
    for n in notifier_config:
        if "type" not in n:
            raise ConfigError("Missing notifer type")
        if "enabled" in n and n["enabled"] == False:
            continue
        if n["type"] == "pushbullet":
            notifier_group.add_notifier(PushbulletNotifier(**n["config"]))
        elif n["type"] == "smtp":
            notifier_group.add_notifier(SMTPNotifier(**n["config"]))
        elif n["type"] == "stdout":
            notifier_group.add_notifier(StdoutNotifier())
        else:
            raise ConfigError("Unknown notifer type {}".format(n["type"]))

    return notifier_group
