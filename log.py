import logging
from textual.app import App
from textual.widgets import Log
from textual.logging import TextualHandler
from time import sleep
from textual import work
from textual._context import active_app
import sys
from threading import get_ident



class LogApp(App):
    """An app with a simple log."""
    app = None

    def __init__(self):
        self.tid = get_ident()
        LogApp.app = self
        super().__init__()

    def compose(self):
        yield Log()

    def on_ready(self) -> None:
        log = self.query_one(Log)
        log.write_line("Hello, World!")
        self.do_some_log()

    @work(thread=True)
    def do_some_log(self) -> None:
        for i in range(3):
            logging.warning(f"Logging line {i} from thread {get_ident()}")
            sleep(0.25)

class LogAppHandler(logging.Handler):
    """A Logging handler for Textual apps."""

    def emit(self, record: logging.LogRecord) -> None:
        """Invoked by logging."""
        message = self.format(record)
        if LogApp.app is None:
            print(message, file=sys.stderr)
        else:
            log = LogApp.app.query_one(Log)
            if LogApp.app.tid != get_ident():
                LogApp.app.call_from_thread(log.write_line, message)
                # app.call_from_thread(log.refresh_lines, 3, 3)
            else:
                log.write_line(message)
                # log.refresh_lines(3, 3)

if __name__ == "__main__":
    logging.basicConfig(
    level=logging.INFO,
    handlers=[LogAppHandler()],
    )
    LogApp().run()
