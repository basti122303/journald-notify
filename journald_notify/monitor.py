from systemd import journal


class Monitor(object):
    def __init__(self, notifier, filters):
        self._notifier = notifier
        self._filters = filters

    def _scan(self, reader):
        for entry in reader:
            for f in self._filters:
                m = f.match(entry["MESSAGE"], entry["SYSLOG_IDENTIFIER"].lower())
                if not m:
                    continue
                title, body = m()
                self._notifier.notify(title, body)

    def monitor(self):
        reader = journal.Reader()
        reader.seek_tail()
        while True:
            reader.wait()
            self._scan(reader)

    def scan(self):
        reader = journal.Reader()
        reader.this_boot()
        self._scan(reader)
