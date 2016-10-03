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

    def _prepare_data(self, title, message):
        title, message = self._resolve_params(title, message)
        if self._prepend_hostname:
            title = "{} - {}".format(self._hostname, title)

        return {"type": "note", "title": title, "body": message}

    def notify(self, title, message):
        while True:
            try:
                r = self._session.post(PushbulletNotifier.PUSH_URL, json=self._prepare_data(title, message))
                r.raise_for_status()
            except requests.exceptions.ConnectionError as e:
                self._logger.warn("Could not connect to pushbullet: {}".format(e))
                sleep(5)
            except requests.exceptions.Timeout as e:
                self._logger.warn("Timeout while connecting to pushbullet: {}".format(e))
                sleep(5)
            else:
                break
