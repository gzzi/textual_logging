import logging
from textual.app import App
from textual.widgets import Log, Header, Footer
from textual import work
from threading import get_ident
from textual.reactive import reactive

class LoggingLogWidget(Log):
    """A Log widget that captures logging output."""
    format = reactive("%(asctime)s - %(levelname)s - %(message)s")

    class LogAppHandler(logging.Handler):
        """A Logging handler for Textual apps."""

        def __init__(self, app, log_widget: 'LoggingLogWidget') -> None:
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


    def __init__(self, logger=None, *args, **kwargs):
        self.logger = logging.getLogger(logger)
        super().__init__(*args, **kwargs)

    def on_mount(self) -> None:
        """Called when the widget is mounted."""
        self.handler = LoggingLogWidget.LogAppHandler(self.app, self)
        self.handler.setFormatter(logging.Formatter(self.format))
        self.backup_handler = []
        for h in self.logger.handlers:
            self.backup_handler.append(h)
            self.logger.removeHandler(h)
        self.logger.addHandler(self.handler)
        self.set_interval(1/25, self.handler.flush)

    def on_unmount(self) -> None:
        """Called when the widget is unmounted."""
        self.handler.flush()
        handlers = self.logger.handlers[:]
        for handler in handlers:
            if isinstance(handler, LoggingLogWidget.LogAppHandler):
                self.logger.removeHandler(handler)
        for handler in self.backup_handler:
            self.logger.addHandler(handler)

    def watch_format(self, format: str) -> None:
        """Called when the format changes."""
        super().clear()
        self.handler.setFormatter(logging.Formatter(self.format))
        self.handler.on_format_change()

    def clear(self) -> None:
        """Clear the log and previous records."""
        self.handler.clear()
        super().clear()

class TextualLogger(App):
    """An app with a simple log."""

    BINDINGS = [("d", "toggle_dark", "Toggle dark mode"),
                ("c", "clear", "Clear"),
                ("t", "toggle_time", "Toggle time")]

    def __init__(self):
        self.tid = get_ident()
        super().__init__()

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )

    def action_clear(self) -> None:
        """An action to clear the log."""
        log = self.query_one(Log)
        log.clear()

    def action_toggle_time(self) -> None:
        """An action to toggle time in the log format."""
        log = self.query_one(LoggingLogWidget)
        if "%(asctime)s" in log.format:
            log.format = "%(levelname)s - %(message)s"
        else:
            log.format = "%(asctime)s - %(levelname)s - %(message)s"

    def compose(self):
        yield Header()
        yield LoggingLogWidget()
        yield Footer()

    def on_ready(self) -> None:
        self.do_some_log()

    @work(thread=True)
    def do_some_log(self) -> None:
        for i in range(10000):
            logging.warning(f"Logging line {i}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.info("Starting LogApp")
    TextualLogger().run()
    logging.info("LogApp Exit")
