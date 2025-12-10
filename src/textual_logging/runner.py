import logging

from textual.app import App
from textual.widgets import Header, Footer
from textual import work
from .widget import Logging

class TextualLogger(App):
    """An app with a simple log."""

    BINDINGS = [("d", "toggle_dark", "Toggle dark mode"),
                ("c", "clear", "Clear"),
                ("t", "toggle_time", "Toggle time"),
                ("s", "change_severity", "Change severity")]

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )

    def action_clear(self) -> None:
        """An action to clear the log."""
        log = self.query_one(Logging)
        log.clear()

    def action_toggle_time(self) -> None:
        """An action to toggle time in the log format."""
        log = self.query_one(Logging)
        if "%(asctime)s" in log.format:
            log.format = "%(levelname)s - %(message)s"
        else:
            log.format = "%(asctime)s - %(levelname)s - %(message)s"

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

    def compose(self):
        yield Header()
        yield Logging()
        yield Footer()

    def on_ready(self) -> None:
        self.process()

    @work(thread=True)
    def process(self):
        self.job()


def run(func):
    """Run a Textual app with logging around a function.

    Args:
        func (Callable): The function to run.
    """
    app = TextualLogger()

    ret = None
    def wrapper():
        nonlocal ret
        ret = func()

    app.job = wrapper
    app.run()
    return ret
