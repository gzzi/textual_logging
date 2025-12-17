from logging import Formatter
from dataclasses import dataclass


@dataclass
class FormatPart:
    fmt: str
    key: str
    name: str
    active: bool = True


class DynamicFormatter:
    """A logging formatter that can change its format dynamically."""

    def __init__(self, fmt: list[FormatPart]):
        self._fmt = fmt
        self.refresh_format()

    def toggle_part(self, key: str) -> None:
        """Toggle a part of the format on or off."""
        for part in self._fmt:
            if part.key == key:
                part.active = not part.active
                break
        self.refresh_format()

    def refresh_format(self) -> None:
        """Set a new format for the formatter."""
        fmt = " ".join(part.fmt for part in self._fmt if part.active)
        self._formatter = Formatter(fmt)

    def format(self, record):
        """Format a log record."""
        return self._formatter.format(record)
