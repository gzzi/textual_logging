import logging
from typing import Any, Callable

from textual import work
from textual.app import App
from textual.reactive import Reactive
from textual.widgets import Footer, Header

from .formatter import DynamicFormatter, FormatPart
from .handler import LoggingHandler
from .widget import Logging, RichLogging

DEFAULT_FORMAT = [
    FormatPart("%(asctime)s", "t", "Time"),
    FormatPart("[%(levelname)s]", "l", "Level"),
    FormatPart("%(message)s", "m", "Message"),
]

DEFAULT_RICH_FORMAT = [
    FormatPart("[blue]%(asctime)s[/]", "t", "Time"),
    FormatPart("[bold]%(levelname)8s[/]", "l", "Level"),
    FormatPart("%(message)s", "m", "Message"),
]


class TextualLogger(App[None]):
    """An app with a simple log."""

    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
        ("c", "clear", "Clear"),
        ("s", "change_severity", "Change severity"),
    ]

    def __init__(
        self,
        logger_name: str | None = None,
        use_rich: bool = False,
        **kwargs: Any,
    ):
        super().__init__(**kwargs)

        self.job: Callable[[], Any] | None = None
        self.logger_name: str | None = logger_name
        self.use_rich: bool = use_rich

        handler = self.get_textual_log_handler(self.logger_name)
        if handler is None:
            return

        if not isinstance(handler.formatter, DynamicFormatter):
            handler.setFormatter(
                DynamicFormatter(
                    DEFAULT_FORMAT if not use_rich else DEFAULT_RICH_FORMAT
                )
            )

        for part in handler.formatter.get_parts():
            self.bind(
                part.key, f"toggle_fmt('{part.key}')", description=f"Toggle {part.name}"
            )

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.theme: Reactive[str] = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )

    def action_clear(self) -> None:
        """An action to clear the log."""
        self.widget.clear()

    def action_change_severity(self) -> None:
        """An action to change the log severity."""
        if self.widget.severity == logging.DEBUG:
            self.widget.severity = logging.INFO
        elif self.widget.severity == logging.INFO:
            self.widget.severity = logging.WARNING
        elif self.widget.severity == logging.WARNING:
            self.widget.severity = logging.ERROR
        else:
            self.widget.severity = logging.DEBUG
        self.notify(
            f"Log severity changed to {logging.getLevelName(self.widget.severity)}"
        )

    def action_toggle_fmt(self, key: str) -> None:
        """Called when the format changes."""
        handler = self.get_textual_log_handler(self.logger_name)
        if handler is None:
            return

        if not isinstance(handler.formatter, DynamicFormatter):
            return

        handler.formatter.toggle_part(key)
        self.widget.config_changed()

    def compose(self):
        yield Header()
        if self.use_rich:
            self.widget = RichLogging(self.logger_name, markup=True)
        else:
            self.widget = Logging(self.logger_name)
        yield self.widget
        yield Footer()

    def on_ready(self) -> None:
        self.process()

    def get_textual_log_handler(self, name: str | None):
        """Get the Textual log handler for a given logger name."""
        logger = logging.getLogger(name)
        for handler in logger.handlers:
            if isinstance(handler, LoggingHandler):
                return handler
        return None

    @work(thread=True)
    def process(self):
        if self.job is not None:
            self.job()


def run(
    func: Callable[[], Any],
    logger_name: str | None = None,
    use_rich: bool = False,
) -> Any:
    """Run a Textual app with logging around a function.

    Args:
        func (Callable): The function to run.
        logger_name (str | None): The name of the logger to capture. If None, captures the root logger.
        use_rich (bool): Whether to use RichLogging widget instead of Logging.
    """
    app = TextualLogger(logger_name=logger_name, use_rich=use_rich)

    ret = None

    def wrapper():
        nonlocal ret
        ret = func()

    app.job = wrapper
    app.run()
    return ret
