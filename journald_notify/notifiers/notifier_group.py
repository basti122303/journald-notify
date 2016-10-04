import threading
from .notifier import Notifier


class NotifierGroup(Notifier):
    def __init__(self, logger):
        self._notifiers = []

        self._logger = logger

    def add_notifier(self, notifier):
        self._notifiers.append(notifier)

    def notify(self, title, message, retry_forever=False):
        for notifier in self._notifiers:
            if retry_forever:
                # These notifications could go on forever and never actually trigger, so it's
                # important that they each run in their own thread. This at least gives some of
                # the notifiers a chance to succeed.
                # This isn't necessary when not retrying forever, as notifiers should always
                # time out after three failed attempts.
                notifier_thread = threading.Thread(target=self._notify, args=(notifier, title, message, retry_forever), daemon=True)
                notifier_thread.start()
            else:
                self._notify(notifier, title, message, retry_forever)

    def _notify(self, notifier, title, message, retry_forever):
        try:
            notifier.notify(title, message, retry_forever)
        except BaseException as e:
            self._logger.warn("Fatal error while running {0} notifier: {1}".format(notifier.__class__.__name__, e))
