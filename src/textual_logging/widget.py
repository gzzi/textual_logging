import logging
from textual.widgets import Log
from threading import get_ident
from textual.reactive import reactive

class Logging(Log):
    """A Log widget that captures logging output."""
    format = reactive("%(asctime)s - %(levelname)s - %(message)s")

    class LogAppHandler(logging.Handler):
        """A Logging handler for Textual apps."""

        def __init__(self, app, log_widget: 'Logging') -> None:
            self.app = app
            self.log_widget = log_widget
            self.tid = get_ident()
            self.records: list[logging.LogRecord] = []
            self.previous: list[logging.LogRecord] = []
            super().__init__()

        def emit(self, record: logging.LogRecord) -> None:
            """Invoked by logging."""
            self.records.append(record)

        def flush(self) -> None:
            """Flush any remaining log lines."""
            if self.records:
                lines = [self.format(record) for record in self.records]
                if self.tid != get_ident():
                    self.app.call_from_thread(self.log_widget.write_lines, lines)
                else:
                    self.log_widget.write_lines(lines)
                self.previous.extend(self.records)
                self.records.clear()

        def on_format_change(self) -> None:
            """Called when the format changes."""
            self.flush()
            self.records = self.previous.copy()
            self.previous.clear()
            self.flush()

        def clear(self)-> None:
            """Clear previous records."""
            self.previous.clear()
            self.records.clear()


    def __init__(self, logger=None, refresh_rate = 1/25, *args, **kwargs):
        self.refresh_rate = refresh_rate
        self.logger = logging.getLogger(logger)
        super().__init__(*args, **kwargs)

    def on_mount(self) -> None:
        """Called when the widget is mounted."""
        self.handler = Logging.LogAppHandler(self.app, self)
        self.handler.setFormatter(logging.Formatter(self.format))
        self.backup_handler = []
        for h in self.logger.handlers:
            self.backup_handler.append(h)
            self.logger.removeHandler(h)
        self.logger.addHandler(self.handler)
        self.set_interval(self.refresh_rate, self.handler.flush)

    def on_unmount(self) -> None:
        """Called when the widget is unmounted."""
        self.handler.flush()
        handlers = self.logger.handlers[:]
        for handler in handlers:
            if isinstance(handler, Logging.LogAppHandler):
                self.logger.removeHandler(handler)
        for handler in self.backup_handler:
            self.logger.addHandler(handler)

    def watch_format(self, format: str) -> None:
        """Called when the format changes."""
        super().clear()
        self.handler.setFormatter(logging.Formatter(format))
        self.handler.on_format_change()

    def clear(self) -> None:
        """Clear the log and previous records."""
        self.handler.clear()
        super().clear()
