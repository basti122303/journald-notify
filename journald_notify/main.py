from functools import partial
import os
import threading
import tempfile
import socket
import logging
from time import sleep
import traceback
import click
from systemd import journal
from ._config import load as config_loader
from ._ipfinder import IPFinder
from . import notifiers



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
ipfinder = IPFinder()


def _notify(app_notifiers, title, body, retry=False):
    for notifier in app_notifiers._notifiers:
        while True:
            try:
                notifier.notify(title, body)
            except socket.error:
                if not retry:
                    raise
                logger.error("Socket error: {}", traceback.format_exc())
                sleep(5)
            else:
                break


def _get_ip_info(add_public_ip, add_local_ips):
    body = ""
    if add_public_ip:
        try:
            body += "Public IP: {}\n".format(ipfinder.public_ip)
        except Exception as e:
            logger.error("Could not get the public IP: {}".format(e))
            logger.debug("Could not get the public IP: {}", traceback.format_exc())
            body += "Failed to get the public IP\n"
    if add_local_ips:
        try:
            body += "Local IPs:\n{}\n\n".format("\n".join("- {}: {}".format(*addr) for addr in ipfinder.local_ips))
        except Exception as e:
            logger.error("Could not get local IPs: {}".format(e))
            logger.debug("Could not get local IPs: {}", traceback.format_exc())
            body += "Failed to get local IPs\n"
    return body


def _notify_boot(app_notifiers, boot_file_path, boot_settings):
    if os.path.isfile(boot_file_path):
        return

    body = partial(_get_ip_info, boot_settings.get("add_public_ip", False), boot_settings.get("add_local_ips", False))
    _notify(app_notifiers, "System booted", body, True)

    with open(boot_file_path, "wb"):
        pass


@click.group()
@click.option("-v", "--verbose", is_flag=True)
def entry_point(verbose=False):
    if verbose:
        logger.setLevel(logging.DEBUG)


@entry_point.command()
@click.option("-c", "--config-file", required=True, type=click.File("r"))
@click.option("--boot-file", "boot_file_path", required=False, type=click.Path(exists=False, dir_okay=False, readable=False, path_type=str), default=os.path.join(tempfile.gettempdir(), ".journald-notify_boot"), envvar="JOURNALD_NOTIFY_BOOTFILE")
def run(config_file, boot_file_path):
    app_config = config_loader(config_file)
    app_notifiers = notifiers.create_notifiers(app_config.notifiers)

    boot_settings = app_config.get_settings("boot")
    if boot_settings and boot_settings.get("notify", False):
        # Notification of boot should not hold up reading from journal ASAP
        boot_notify_thread = threading.Thread(target=_notify_boot, args=(app_notifiers, boot_file_path, boot_settings), daemon=True)
        boot_notify_thread.start()

    reader = journal.Reader()
    reader.seek_tail()
    while True:
        reader.wait()
        for entry in reader:
            for f in app_config.filters:
                m = f["match"].search(entry["MESSAGE"])
                if not m:
                    continue
                _notify(app_notifiers, f["title"].format(*m.groups()), f["body"].format(*m.groups()))


@entry_point.command()
@click.option("-c", "--config-file", required=True, type=click.File("r"))
def test_filters(config_file):
    app_config = config_loader(config_file)
    app_notifiers = notifiers.create_notifiers([{"type": "stdout"}])
    reader = journal.Reader()
    reader.this_boot()

    for entry in reader:
        for f in app_config.filters:
            m = f["match"].search(entry["MESSAGE"])
            if not m:
                continue
            _notify(app_notifiers, f["title"].format(*m.groups()), f["body"].format(*m.groups()))


@entry_point.command()
@click.option("-c", "--config-file", required=True, type=click.File("r"))
def test_notifiers(config_file):
    app_config = config_loader(config_file)
    app_notifiers = notifiers.create_notifiers(app_config.notifiers)
    _notify(app_notifiers, "This is a test message", "This is the message body", True)
