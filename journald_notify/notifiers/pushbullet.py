import socket
from time import sleep
import requests
from .notifier import Notifier


class PushbulletNotifier(Notifier):
    PUSH_URL = "https://api.pushbullet.com/v2/pushes"

    def __init__(self, logger, key, prepend_hostname=True, retry_interval=10):
        self._logger = logger
        self._session = requests.Session()
        self._session.auth = (key, "")
        self._session.headers.update({"Content-Type": "application/json"})
        self._prepend_hostname = prepend_hostname
        self._retry_interval = retry_interval
        if self._prepend_hostname:
            self._hostname = socket.gethostname()

    def _resolve_params(self, title, message):
        title, message = super(PushbulletNotifier, self)._resolve_params(title, message)
        if self._prepend_hostname:
            title = "{0} - {1}".format(self._hostname, title)
        return title, message

    def _prepare_data(self, title, message):
        title, message = self._resolve_params(title, message)

        return {"type": "note", "title": title, "body": message}

    def notify(self, title, message, retry_forever=False):
        retry_count = 0
        while retry_forever == True or retry_count < 3:
            try:
                r = self._session.post(PushbulletNotifier.PUSH_URL, json=self._prepare_data(title, message))
                r.raise_for_status()
            except requests.exceptions.ConnectionError as e:
                retry_count += 1
                self._logger.warn("Could not connect to pushbullet: {}".format(e))
                sleep(self._retry_interval)
            except requests.exceptions.Timeout as e:
                retry_count += 1
                self._logger.warn("Timeout while connecting to pushbullet: {}".format(e))
                sleep(self._retry_interval)
            else:
                break
            if retry_count % 10 == 0:
                # Warn every 10 attempts. Should only happen when retrying forever.
                self._logger.warn("Failed to connect to pushbullet after {0} attempts (title: {1})".format(retry_count, *self._resolve_params(title, "")))
        if retry_count >= 3:
            self._logger.warn("Failed to contact pushbullet after at least three attempts (title: {0})".format(*self._resolve_params(title, "")))
