from smtplib import SMTP, SMTP_SSL
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
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

    def notify(self, title, message):
        with self._prepare_conn() as mailserver:
            mailserver.sendmail(self._from_addr, self._to_addrs, self._prepare_msg(title, message).as_string())

