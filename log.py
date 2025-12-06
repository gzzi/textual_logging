import logging
from textual.app import App
from textual.widgets import Log, Header, Footer
from textual import work
from threading import get_ident


class LoggingLogWidget(Log):
    """A Log widget that captures logging output."""


    class LogAppHandler(logging.Handler):
        """A Logging handler for Textual apps."""

        def __init__(self, app, log_widget: 'LoggingLogWidget') -> None:
            self.app = app
            self.log_widget = log_widget
            self.tid = get_ident()
            self.lines: list[str] = []
            super().__init__()

        def emit(self, record: logging.LogRecord) -> None:
            """Invoked by logging."""
            self.lines.append(self.format(record))

        def flush(self) -> None:
            """Flush any remaining log lines."""
            if self.lines:
                if self.tid != get_ident():
                    self.app.call_from_thread(self.log_widget.write_lines, self.lines)
                else:
                    self.log_widget.write_lines(self.lines)
                self.lines.clear()


    def __init__(self, logger=None, *args, **kwargs):
        self.logger = logging.getLogger(logger)
        super().__init__(*args, **kwargs)

    def on_mount(self) -> None:
        """Called when the widget is mounted."""
        self.handler = LoggingLogWidget.LogAppHandler(self.app, self )
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


class LogApp(App):
    """An app with a simple log."""
    app = None

    BINDINGS = [("d", "toggle_dark", "Toggle dark mode"),
                ("c", "clear", "Clear")]

    def __init__(self):
        self.tid = get_ident()
        LogApp.app = self
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

    def compose(self):
        yield Header()
        yield LoggingLogWidget()
        yield Footer()

    def on_ready(self) -> None:
        self.do_some_log()

    @work(thread=True)
    def do_some_log(self) -> None:
        for i in range(10000):
            logging.warning(f"Logging line {i} from thread {get_ident()}")


if __name__ == "__main__":
    logging.basicConfig(
    level=logging.INFO,
    #  handlers=[],
    )
    logging.error("Starting LogApp")
    LogApp().run()
    logging.error("END LogApp")
