import logging
import socket
from time import sleep
import requests
from .notifier import Notifier


class PushbulletNotifier(Notifier):
    PUSH_URL = "https://api.pushbullet.com/v2/pushes"

    def __init__(self, key, prepend_hostname=True):
        self._session = requests.Session()
        self._session.auth = (key, "")
        self._session.headers.update({'Content-Type': 'application/json'})
        self._prepend_hostname = prepend_hostname
        if self._prepend_hostname:
            self._hostname = socket.gethostname()

        self._logger = logging.getLogger("journald-notify")

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
                sleep(5)
            except requests.exceptions.Timeout as e:
                retry_count += 1
                self._logger.warn("Timeout while connecting to pushbullet: {}".format(e))
                sleep(5)
            else:
                break
            if retry_count % 10 == 0:
                self._logger.warn("Failed to connect to pushbullet after {0} attempts (title: {1})".format(retry_count, *self._resolve_params(title, "")))
        if retry_count >= 3:
            self._logger.warn("Failed to contact pushbullet after three attempts (title: {0})".format(*self._resolve_params(title, "")))
