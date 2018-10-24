import sentry_sdk
from .notifier import Notifier

class SentryNotifier(Notifier):
    def __init__(self, logger, dsn):
        sentry_sdk.init(dsn)

    def notify(self, title, message, retry_forever=False):
        sentry_sdk.capture_message(title + "\n\n" + message)
