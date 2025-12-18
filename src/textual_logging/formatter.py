from logging import Formatter
from dataclasses import dataclass


@dataclass
class FormatPart:
    fmt: str
    key: str
    name: str
    active: bool = True


class DynamicFormatter(Formatter):
    """A logging formatter that can change its format dynamically."""

    def __init__(
        self, fmt: list[FormatPart], formatter_cls: type[Formatter] = Formatter
    ) -> None:
        super().__init__()
        self.parts = fmt
        self.formatter_cls = formatter_cls
        self.refresh_format()

    def get_parts(self) -> list[FormatPart]:
        """Get the format parts."""
        return self.parts

    def toggle_part(self, key: str) -> None:
        """Toggle a part of the format on or off."""
        for part in self.parts:
            if part.key == key:
                part.active = not part.active
                break
        self.refresh_format()

    def refresh_format(self) -> None:
        """Set a new format for the formatter."""
        fmt = " ".join(part.fmt for part in self.parts if part.active)
        self._formatter = self.formatter_cls(fmt)

    def format(self, record):
        """Format a log record."""
        return self._formatter.format(record)
