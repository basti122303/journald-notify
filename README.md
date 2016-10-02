# journald-notify
systemd's journal is awesome. Wouldn't it be more awesome if it could send notifications?

journald-notify is a daemon that listens to the systemd's journal and sends notifications based on filters that you specify. Currently it supports sending push notifications through SMTP or [Pushbullet](https://www.pushbullet.com/).

## Usage
See `examples/journald-notify.yml` for an example of a configuration file. There are two subcommands to help testing your configuration:

1. `journald-notify test_notifiers -c path_to_config` will try to send a test message through all of your notifiers.
2. `journald-notify test_filters -c path_to_config` will run through your journal history and print entries matching your filters.

Once your configuration is set you can run `journald-notify run -c path_to_config` and wait for push notifications.

You can also check out `examples/journald-notify.service` for a systemd unit file.
