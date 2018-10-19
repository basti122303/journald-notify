from systemd import journal
from datetime import datetime
import json

def convert_key(m, k, f):
    if k in m:
        m[k] = f(m[k])

def format_date(date):
    return date.strftime("%Y-%m-%d %H:%M:%S")

def entry_to_json(entry):
    """ See https://www.freedesktop.org/software/systemd/python-systemd/_modules/systemd/journal.html for types of values
    """
    data = entry.copy()

    convert_key(data, "_SOURCE_REALTIME_TIMESTAMP", format_date)
    convert_key(data, "__REALTIME_TIMESTAMP", format_date)
    convert_key(data, "COREDUMP_TIMESTAMP", format_date)
    data.pop("MESSAGE_ID", None)
    data.pop("_MACHINE_ID", None)
    data.pop("_CURSOR", None)
    data.pop("_BOOT_ID", None)
    data.pop("_SOURCE_MONOTONIC_TIMESTAMP", None)
    data.pop("__MONOTONIC_TIMESTAMP", None)

    try:
        return json.dumps(data)
    except TypeError:
        # remove data that are not serializable to json
        for k in data.copy():
            try:
                json.dumps(data[k])
            except TypeError:
                data.pop(k, None)

    return json.dumps(data)

priorities = {
    0: "emerg",
    1: "alert",
    2: "crit",
    3: "err",
    4: "warning",
    5: "notice",
    6: "info",
    7: "debug"
}

def entry_to_priority_str(entry):
    priority = priorities[entry["PRIORITY"]] if ("PRIORITY" in entry and entry["PRIORITY"] in priorities) else "unknown"
    return priority

def entry_to_body(entry):
    message = entry["MESSAGE"] if "MESSAGE" in entry else ""
    date_str = format_date(entry["_SOURCE_REALTIME_TIMESTAMP"]) if "_SOURCE_REALTIME_TIMESTAMP" in entry else ""

    return "[" + date_str + "] " + "(" + entry_to_priority_str(entry) + "): " + message + "\n\n" + "data: " + entry_to_json(entry)

entry_to_title = entry_to_priority_str

class Monitor(object):
    def __init__(self, notifier, filters):
        self._notifier = notifier
        self._filters = filters

    def _scan(self, reader):
        for entry in reader:
            for f in self._filters:
                if not "MESSAGE" in entry:
                    continue
                service = entry["SYSLOG_IDENTIFIER"].lower() if "SYSLOG_IDENTIFIER" in entry else "__unknown"
                m = f.match(entry, service)
                if not m:
                    continue
                title = entry_to_title(entry)
                body = entry_to_body(entry)
                self._notifier.notify(title, body, limit=f.notifiers)

    def monitor(self, reader_timeout=None):
        reader = journal.Reader()
        reader.seek_tail()
        reader.get_previous()
        while True:
            reader.wait(reader_timeout)
            self._scan(reader)

    def scan(self):
        reader = journal.Reader()
        reader.this_boot()
        self._scan(reader)
