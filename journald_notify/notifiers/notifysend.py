import subprocess
from time import sleep
from .notifier import Notifier


class NotifySendNotifier(Notifier):
    def __init__(self, logger, sudo=True, headless=True, retry_interval=10):
        self._logger = logger
        self._sudo = sudo
        self._headless = headless
        self._retry_interval = retry_interval

    def _prepare_cmd(self, title, message):
        summary, body = self._resolve_params(title, message)
        cmdline = []
        if self._sudo:
            cmdline.append("sudo")
        if self._headless:
            cmdline.append("notify-send-headless")
        else:
            cmdline.append("notify-send")
        if summary:
            cmdline.append(summary)
        if body:
            cmdline.append(body)
        return cmdline

    def notify(self, title, message, retry_forever=False):
        retry_count = 0
        while retry_forever == True or retry_count < 3:
            try:
                subprocess.run(self._prepare_cmd(title, message), check=True)
            except subprocess.CalledProcessError as e:
                retry_count += 1
                self._logger.warn("Error while attempting to contact notification daemon: {0}".format(e))
                sleep(self._retry_interval)
            except subprocess.SubprocessError:
                retry_count += 1
                self._logger.warn("Unknown error while attempting to contact notification daemon: {0}".format(e))
            else:
                break
            if retry_count % 10 == 0:
                # Warn every 10 attempts. Should only happen when retrying forever.
                self._logger.warn("Failed to contact notification daemon after {0} attempts (title: {1})".format(retry_count, *self._resolve_params(title, "")))
        if retry_count >= 3:
            self._logger.warn("Failed to contact notification daemon after at least three attempts (title: {0})".format(*self._resolve_params(title, "")))
