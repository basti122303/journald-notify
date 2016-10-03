class Notifier(object):
    def notify(self, title, message):
        raise NotImplementedError()

    def _resolve_params(self, title, message):
        if callable(title):
            title = title()
        if callable(message):
            message = message()
        return title, message
