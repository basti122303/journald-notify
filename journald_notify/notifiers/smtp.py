from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging
from smtplib import SMTP, SMTP_SSL, SMTPException, SMTPResponseException
import socket
from time import sleep
from .notifier import Notifier


class SMTPNotifier(Notifier):
    def __init__(self, host, from_addr, to_addrs, port=0, tls=True, username=None, password=None):
        self._host = host
        self._from_addr = from_addr
        self._to_addrs = to_addrs
        self._port = port
        self._tls = tls
        self._username = username
        self._password = password

        self._logger = logging.getLogger("journald-notify")

    def _prepare_conn(self):
        if self._tls:
            mailserver = SMTP_SSL(self._host, self._port)
        else:
            mailserver = SMTP(self._host, self._port)
        if self._username:
            mailserver.login(self._username, self._password)
        return mailserver

    def _prepare_msg(self, title, message):
        subject, body = self._resolve_params(title, message)
        msg = MIMEMultipart()
        msg["From"] = self._from_addr
        msg["To"] = ", ".join(self._to_addrs)
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))
        return msg

    def notify(self, title, message, retry_forever=False):
        retry_count = 0
        while retry_forever == True or retry_count < 3:
            try:
                with self._prepare_conn() as mailserver:
                    mailserver.sendmail(self._from_addr, self._to_addrs, self._prepare_msg(title, message).as_string())
            except SMTPResponseException as e:
                retry_count += 1
                self._logger.warn("Error returned from SMTP server: {0}".format(e.smtp_error))
                sleep(5)
            except SMTPException as e:
                retry_count += 1
                self._logger.warn("Error while sending email: {0}".format(e))
                sleep(5)
            except socket.error as e:
                retry_count += 1
                self._logger.warn("Error while sending email: {0}".format(e))
                sleep(5)
            else:
                break
            if retry_count % 10 == 0:
                self._logger.warn("Failed to send email after {0} attempts (title: {1})".format(retry_count, *self._resolve_params(title, "")))
        if retry_count >= 3:
            self._logger.warn("Failed to send email after three attempts (title: {0})".format(*self._resolve_params(title, "")))
