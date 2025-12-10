# Textual widget to display python logging log entry

The goal of this widget is to display log from python logging library inside a textual application.

The records are saved in order to change format later.

## Demo

Run:

```bash
python3 -m src.textual_logging.demo
```

it will log 10'000 messages in each severity.
You can press `t` to show/hide log record time.
You can press `c` to clear the logs.
You can press `s` to change severity.
To exit, press `Ctrl + q`.
