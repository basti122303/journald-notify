import re


class Filter(object):
    def __init__(self, regex, title, body="", services=[]):
        self._regex = re.compile(regex)
        self._title = title
        self._body = body
        self._services = services

    def match(self, entry, service):
        if self._services and service not in self._services:
            return None
        m = self._regex.search(entry)
        if not m:
            return None

        def match_resolver():
            title = self._title.format(*m.groups())
            body = self._body.format(*m.groups())
            return title, body
        return match_resolver


def create_filters(filter_config):
    filters = []
    for _filter in filter_config:
        filters.append(Filter(
            _filter["match"],
            _filter["title"],
            _filter.get("body", ""),
            _filter.get("services", [])
        ))
    return filters
