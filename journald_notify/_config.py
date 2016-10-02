import json
import re
import click


class ConfigError(click.ClickException):
    pass


def load(f):
    config = json.load(f)

    if not config:
        raise ConfigError("Your configuration is empty")

    return Config(config)


class Config(object):
    def __init__(self, config):
        self._notifiers = config["notifiers"]
        self._filters = self._prepare_filters(config.get("filters", []))
        self._settings = config.get("settings", {})

    def _prepare_filters(self, filters):
        _filters = []
        for f in filters:
            _filters.append({
                "match": re.compile(f["match"]),
                "title": f["match"],
                "body": f["body"]
            })
        return _filters

    @property
    def notifiers(self):
        return self._notifiers

    @property
    def filters(self):
        return self._filters

    def get_settings(self, segment):
        return self._settings.get(segment)
