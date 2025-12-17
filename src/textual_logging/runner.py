import logging
from typing import Any, Callable

from textual import work
from textual.app import App
from textual.reactive import reactive, Reactive
from textual.widgets import Footer, Header

from .handler import LoggingHandler
from .widget import Logging


class TextualLogger(App):
    """An app with a simple log."""

    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
        ("c", "clear", "Clear"),
        ("t", "toggle_time", "Toggle time"),
        ("s", "change_severity", "Change severity"),
    ]

    format = reactive("%(asctime)s - %(levelname)s - %(message)s")

    def __init__(self, logger_name: str | None = None, **kwargs: Any):
        super().__init__(**kwargs)
        self.logger_name: str | None = logger_name
        self.job: Callable[[], Any] | None = None

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.theme: Reactive[str] = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )

    def action_clear(self) -> None:
        """An action to clear the log."""
        log = self.query_one(Logging)
        log.clear()

    def action_toggle_time(self) -> None:
        """An action to toggle time in the log format."""
        if "%(asctime)s" in self.format:
            self.format = "%(levelname)s - %(message)s"
        else:
            self.format = "%(asctime)s - %(levelname)s - %(message)s"

    def action_change_severity(self) -> None:
        """An action to change the log severity."""
        log = self.query_one(Logging)
        if log.severity == logging.DEBUG:
            log.severity = logging.INFO
        elif log.severity == logging.INFO:
            log.severity = logging.WARNING
        elif log.severity == logging.WARNING:
            log.severity = logging.ERROR
        else:
            log.severity = logging.DEBUG
        self.notify(f"Log severity changed to {logging.getLevelName(log.severity)}")

    def get_textual_log_handler(self, name: str | None):
        """Get the Textual log handler for a given logger name."""
        logger = logging.getLogger(name)
        for handler in logger.handlers:
            if isinstance(handler, LoggingHandler):
                return handler
        return None

    def watch_format(self, format: str) -> None:
        """Called when the format changes."""
        handler = self.get_textual_log_handler(self.logger_name)
        if handler is None:
            return

        handler.setFormatter(logging.Formatter(format))
        log = self.query_one(Logging)
        log.config_changed()

    def compose(self):
        yield Header()
        yield Logging(self.logger_name)
        yield Footer()

    def on_ready(self) -> None:
        self.process()

    @work(thread=True)
    def process(self):
        if self.job is not None:
            self.job()


def run(func: Callable[[], Any], logger_name: str | None = None) -> Any:
    """Run a Textual app with logging around a function.

    Args:
        func (Callable): The function to run.
        logger_name (str | None): The name of the logger to capture. If None, captures the root logger.
    """
    app = TextualLogger(logger_name)

    ret = None

    def wrapper():
        nonlocal ret
        ret = func()

    app.job = wrapper
    app.run()
    return ret
