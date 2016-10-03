import logging
from .notifier import Notifier


class NotifierGroup(Notifier):
    def __init__(self):
        self._notifiers = []

        self._logger = logging.getLogger("journald-notify")

    def add_notifier(self, notifier):
        self._notifiers.append(notifier)

    def notify(self, title, message, retry_forever=False):
        for notifier in self._notifiers:
            try:
                notifier.notify(title, message, retry_forever)
            except BaseException as e:
                self._logger.warn("Fatal error while running {0} notifier: {1}".format(notifier.__class__.__name__, e))
