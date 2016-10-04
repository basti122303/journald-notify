import click
from .notifier import Notifier


class StdoutNotifier(Notifier):
    def __init__(self, logger):
        pass

    def notify(self, title, message, retry_forever=False):
        click.echo("Title: {}\nMessage: {}".format(title, message))
