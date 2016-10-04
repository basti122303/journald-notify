# journald-notify
systemd's journal is awesome. Wouldn't it be more awesome if it could send notifications?

journald-notify is a daemon that listens to the systemd's journal and sends notifications based on filters that you specify. Currently it supports sending push notifications through SMTP or [Pushbullet](https://www.pushbullet.com/).

## Usage
See `examples/journald-notify.json` for an example of a configuration file. There are two subcommands to help testing your configuration:

1. `journald-notify -c /path/to/config.json test_notifiers` will try to send a test message through all of your notifiers.
2. `journald-notify -c /path/to/config.json test_filters` will run through your journal history and print entries matching your filters.

Once your configuration is set you can run `journald-notify -c /path/to/config.json run` and wait for push notifications.

You can also check out `examples/journald-notify.service` for a systemd unit file.

## Notes
This is a fork of `pushbullet` by r-darwish. I re-wrote most of the code because I was unhappy about a few things. Most notably, it would not start reading from the journal until it had sent the boot notification, and it would not reliably detect the public and private IP addresses unless network connectivity was available as soon as the program was launched. This rewrite solves those problems, and also stops it from spamming into the journal itself during periods where internet connectivity is lacking.

Other motivations for the rewrite include removing the unnecessary dependnecies on the logbook and yaml packages. JSON configuration is just as good and comes built-in with python, while YAML support does not. Also, python's built-in logging module is more than good enough for the majority of problems.

Finally, this rewrite is more flexible with the filters it lets you apply. You can specify one or more services that a filter should target specifically, or you can specify none at all and just use it for boot notifications.
