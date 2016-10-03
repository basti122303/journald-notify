import click
from .notifier import Notifier


class StdoutNotifier(Notifier):
    def notify(self, title, message):
        click.echo("Title: {}\nMessage: {}".format(title, message))
