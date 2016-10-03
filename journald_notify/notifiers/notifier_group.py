from .notifier import Notifier


class NotifierGroup(Notifier):
    def __init__(self):
        self._notifiers = []

    def add_notifier(self, notifier):
        self._notifiers.append(notifier)

    def notify(self, title, message):
        for notifier in self._notifiers:
            notifier.notify(title, message)
