
from .runner import run
import logging

def demo():
    """A simple demo of the logging widget."""
    for i in range(10000):
        logging.warning(f"Logging line {i}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.info("Starting demo")
    run(demo)
    logging.info("Demo finished")
