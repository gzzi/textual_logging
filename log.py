
import logging
from time import sleep
import threading
import sys,tty,os,termios

stop_threads = False

def ctrl_thread():
    global stop_threads
    while not stop_threads:
        key = getkey()
        if key == 'q' or key == 'esc':
            stop_threads = True
            break

        if key == 't':
            log = logging.getLogger()
            fmt = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            log.handlers[0].setFormatter(fmt)


def log_thread():
    log = logging.getLogger('toto')
    while not stop_threads:
        log.info('toto')
        sleep(0.25)


def getkey():
    old_settings = termios.tcgetattr(sys.stdin)
    tty.setcbreak(sys.stdin.fileno())
    try:
        while True:
            b = os.read(sys.stdin.fileno(), 3).decode()
            if len(b) == 3:
                k = ord(b[2])
            else:
                k = ord(b)
            key_mapping = {
                127: 'backspace',
                10: 'return',
                32: 'space',
                9: 'tab',
                27: 'esc',
                65: 'up',
                66: 'down',
                67: 'right',
                68: 'left'
            }
            return key_mapping.get(k, chr(k))
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    ctrl_thread = threading.Thread(target=ctrl_thread)
    try:
        ctrl_thread.start()
        log_thread()
    finally:
        stop_threads = True
        ctrl_thread.join()
