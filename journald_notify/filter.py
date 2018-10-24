import re
from ._config import ConfigError

field_condition_types = {
    "lte": lambda condition, field_value: field_value != None and field_value <= condition["value"],
    "eq": lambda condition, field_value: field_value == condition["value"],
    "neq": lambda condition, field_value: field_value != condition["value"],
}

def check_field_conditions(field_conditions, entry):
    for field, condition in field_conditions.items():
        if not field_condition_types[condition["type"]](condition, entry.get(field)):
            return False
    return True

class Filter(object):
    def __init__(self, regex, services=[], notifiers=[], conditions=[], field_conditions=[]):
        self._regex = re.compile(regex)
        self._services = services
        self.notifiers = notifiers
        self._conditions = conditions
        self._field_conditions = field_conditions

    def match(self, entry, service):
        if self._services and service not in self._services:
            return None
        m = self._regex.search(entry["MESSAGE"])
        if not m:
            return None
        matched_values = m.groupdict()

        if self._conditions:
            if not self._check_conditions(matched_values):
                return None

        if self._field_conditions:
            if not check_field_conditions(self._field_conditions, entry):
                return None

        return True

    def _check_conditions(self, matched_values):
        for key, value in matched_values.items():
            if key not in self._conditions:
                continue
            condition_type = self._conditions[key]["type"]
            if condition_type == "exclude":
                for exclude in self._conditions[key]["exclude"]:
                    if re.search(exclude, value):
                        return False
            elif condition_type == "include":
                for include in self._conditions[key]["include"]:
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
            _filter.get("services", []),
            _filter.get("notifiers", []),
            _filter.get("conditions", []),
            _filter.get("field_conditions", [])
        ))
    return filters
