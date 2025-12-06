from textual.app import App
from textual.widgets import Header, Footer
from textual import work
from .widget import LoggingWidget
import logging


class TextualLogger(App):
    """An app with a simple log."""

    BINDINGS = [("d", "toggle_dark", "Toggle dark mode"),
                ("c", "clear", "Clear"),
                ("t", "toggle_time", "Toggle time")]

    def __init__(self):
        super().__init__()

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )

    def action_clear(self) -> None:
        """An action to clear the log."""
        log = self.query_one(LoggingWidget)
        log.clear()

    def action_toggle_time(self) -> None:
        """An action to toggle time in the log format."""
        log = self.query_one(LoggingWidget)
        if "%(asctime)s" in log.format:
            log.format = "%(levelname)s - %(message)s"
        else:
            log.format = "%(asctime)s - %(levelname)s - %(message)s"

    def compose(self):
        yield Header()
        yield LoggingWidget()
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
