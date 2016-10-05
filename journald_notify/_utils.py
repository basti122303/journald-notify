from functools import partial
import logging
import os
import traceback
from ._ipfinder import IPFinder


logger = logging.getLogger("journald-notify")
ipfinder = IPFinder()


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
            body += "Local IPs:\n{}\n".format("\n".join("- {}: {}".format(*addr) for addr in ipfinder.local_ips))
        except Exception as e:
            logger.error("Could not get local IPs: {}".format(e))
            logger.debug("Could not get local IPs: {}", traceback.format_exc())
            body += "Failed to get local IPs\n"
    return body


def _notify_boot(notifier, boot_file_path, boot_settings):
    if os.path.isfile(boot_file_path):
        return

    body = partial(_get_ip_info, boot_settings.get("add_public_ip", False), boot_settings.get("add_local_ips", False))
    notifier.notify("System booted", body, retry_forever=True, limit=boot_settings.get("notifiers", []))

    with open(boot_file_path, "wb"):
        pass
