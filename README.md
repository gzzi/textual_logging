# Textual widget to display python logging log entry

The goal of `textual_logging.Logging` widget is to display log from python logging library inside a textual application.
The records are saved in order to change format later and to speedup display.

The logger can be specified when instanciating the widget. By default the root logger is used.
This allow to have multiple widget on the same application showing different logger.

The logger can use any formatter.
The logger must have a `textual_logging.LoggingHandler` handler.

## Example

The file [runner.py](./src/textual_logging/runner.py) contain a example application `textual_logging.TextualLogger` that use the widget.
It also conain a function `textual_logging.run` that can be used directly with a `Callable`.

The file [demo.py](./src/textual_logging/demo.py) show a basic usage.

## Demo

Run:

```bash
python3 -m textual_logging
```

it will log 10'000 messages in each severity.
You can press `t` to show/hide log record time.
You can press `c` to clear the logs.
You can press `s` to change severity.
To exit, press `Ctrl + q`.
