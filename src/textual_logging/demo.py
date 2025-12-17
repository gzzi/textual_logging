import logging

from .handler import LoggingHandler
from .runner import run


def demo():
    """A simple demo of the logging widget."""
    for i in range(10000):
        logging.debug(f"Logging line {i} *")
        logging.info(f"Logging line {i}  *")
        logging.warning(f"Logging line {i}   *")
        logging.error(f"Logging line {i}    *")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, handlers=[LoggingHandler()])
    logging.info("Starting demo")
    run(demo)
    logging.info("Demo finished")
