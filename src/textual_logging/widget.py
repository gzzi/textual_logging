import logging
from typing import TYPE_CHECKING

from textual.reactive import reactive
from textual.widgets import Log

from .handler import LoggingHandler

if TYPE_CHECKING:
    from typing import Self


class Logging(Log):
    """A Log widget that captures logging output."""

    severity = reactive(logging.DEBUG)

    def __init__(
        self, logger: str | None = None, refresh_rate: float = 1 / 25, *args, **kwargs
    ):
        """
        Initialize the Logging widget.

        Args:
            logger: The name of the logger to capture. If None, captures the root logger.
            refresh_rate: How often to refresh the log display.
        """
        self.refresh_rate = refresh_rate
        self.logger = logging.getLogger(logger)
        self.handler: LoggingHandler | None = None
        super().__init__(*args, **kwargs)

    def on_mount(self) -> None:
        """Called when the widget is mounted."""
        for handler in self.logger.handlers:
            if isinstance(handler, LoggingHandler):
                self.handler = handler
                break
        else:
            return

        self.severity = self.logger.level
        self.handler.on_mount(self.app, self)
        self.set_interval(self.refresh_rate, self.handler.flush)

    def on_unmount(self) -> None:
        """Called when the widget is unmounted."""
        if self.handler is None:
            return

        self.handler.on_unmount()

    def config_changed(self):
        """Call this method when logger config change."""
        if self.handler is None:
            return

        super().clear()
        self.handler.on_config_change()

    def watch_severity(self, severity: int) -> None:
        """Called when the severity changes."""
        if self.handler is None:
            return

        super().clear()
        self.handler.on_config_change()

    def clear(self) -> Self:
        """Clear the log and previous records."""
        super().clear()

        if self.handler is not None:
            self.handler.clear()

        return self
