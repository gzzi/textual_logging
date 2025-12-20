import logging
import sys
from threading import get_ident
from typing import TYPE_CHECKING

from textual.app import App
from textual.widgets import Log, RichLog

if TYPE_CHECKING:
    from .widget import Logging, RichLogging


class LoggingHandler(logging.Handler):
    """A Logging handler for Textual apps."""

    def __init__(self) -> None:
        self.app: App | None = None
        self.records: list[logging.LogRecord] = []
        self.previous: list[logging.LogRecord] = []
        super().__init__()

    def on_mount(self, app: App, log_widget: "Logging | RichLogging") -> None:
        self.app = app
        self.log_widget = log_widget
        self.tid = get_ident()

    def on_unmount(self) -> None:
        self.flush()
        self.app = None

    def emit(self, record: logging.LogRecord) -> None:
        """Invoked by logging."""
        if self.app is None:
            print(self.format(record), file=sys.stderr)
            return

        self.records.append(record)

    def flush(self) -> None:
        """Flush any remaining log lines."""
        if self.records:
            lines = [
                self.format(record)
                for record in self.records
                if record.levelno >= self.log_widget.severity
            ]
            self.write_lines(lines)
            self.previous.extend(self.records)
            self.records.clear()

    def write_lines(self, lines: list[str]) -> None:
        """Write lines to the log widget."""
        if isinstance(self.log_widget, Log):
            if self.tid != get_ident() and self.app is not None:
                self.app.call_from_thread(self.log_widget.write_lines, lines)
            else:
                self.log_widget.write_lines(lines)
        if isinstance(self.log_widget, RichLog):
            content = "\n".join(lines)
            if self.tid != get_ident() and self.app is not None:
                self.app.call_from_thread(self.log_widget.write, content)
            else:
                self.log_widget.write(content)

    def on_config_change(self) -> None:
        """Called when the format changes."""
        self.flush()
        self.records = self.previous.copy()
        self.previous.clear()
        self.flush()

    def clear(self) -> None:
        """Clear previous records."""
        self.previous.clear()
        self.records.clear()
