import re
from ._config import ConfigError


class Filter(object):
    def __init__(self, regex, title, body="", services=[], notifiers=[], conditions=[]):
        self._regex = re.compile(regex)
        self._title = title
        self._body = body
        self._services = services
        self.notifiers = notifiers
        self._conditions = conditions

    def match(self, entry, service):
        if self._services and service not in self._services:
            return None
        m = self._regex.search(entry)
        if not m:
            return None
        matched_values = m.groupdict()

        if self._conditions:
            if not self._check_conditions(matched_values):
                return None

        def match_resolver():
            title = self._title.format(**matched_values)
            body = self._body.format(**matched_values)
            return title, body
        return match_resolver

    def _check_conditions(self, matched_values):
        for key, value in matched_values.items():
            if key not in self._conditions:
                continue
            condition_type = self._conditions[key]["type"]
            if condition_type == "exclude":
                for exclude in self._condition[key]["exclude"]:
                    if re.search(exclude, value):
                        return False
            elif condition_type == "include":
                for include in self._condition[key]["include"]:
                    if re.search(include, value):
                        return False
            else:
                raise ConfigError("Unknown condition type specified: {0}".format(condition_type))

        return True


def create_filters(filter_config):
    filters = []
    for _filter in filter_config:
        filters.append(Filter(
            _filter["match"],
            _filter["title"],
            _filter.get("body", ""),
            _filter.get("services", []),
            _filter.get("notifiers", []),
            _filter.get("conditions", [])
        ))
    return filters
