import threading


class NotifierGroup(object):
    def __init__(self, logger):
        self._logger = logger
        self._notifiers = {}

    def add_notifier(self, name, notifier):
        self._notifiers[name] = notifier

    def get_notifiers(self, limit=[]):
        if limit:
            limit = filter(lambda x: x in self._notifiers.keys(), limit)
            return { key: self._notifiers[key] for key in limit }.values()
        else:
            return self._notifiers.values()

    def notify(self, title, message, retry_forever=False, limit=[]):
        for notifier in self.get_notifiers(limit):
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
