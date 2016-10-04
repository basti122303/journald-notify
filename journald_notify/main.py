import os
import tempfile
import logging
import click
from ._cli import CLI


def _log_init():
    logger = logging.getLogger("journald-notify")
    logger.setLevel(logging.INFO)
    sh = logging.StreamHandler()
    sh.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    sh.setFormatter(formatter)
    logger.addHandler(sh)
    return logger


logger = _log_init()
cli = CLI(logger)


@click.group()
@click.option("-c", "--config-file", required=True, type=click.File("r"))
@click.option("-v", "--verbose", is_flag=True)
def entry_point(config_file, verbose=False):
    cli.init(config_file, verbose)


@entry_point.command()
@click.option("--boot-file", "boot_file_path", required=False, type=click.Path(exists=False, dir_okay=False, readable=False, path_type=str), default=os.path.join(tempfile.gettempdir(), ".journald-notify_boot"), envvar="JOURNALD_NOTIFY_BOOTFILE")
def run(boot_file_path):
    cli.run(boot_file_path)


@entry_point.command()
def test_filters():
    cli.test_filters()


@entry_point.command()
def test_notifiers():
    cli.test_notifiers()
