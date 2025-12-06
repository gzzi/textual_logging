
import logging
from time import sleep
import threading
import sys,tty,os,termios
import termios, fcntl, sys, os

stop_threads = False

def handle_key(c):
    global stop_threads
    if c == 'q':
        stop_threads = True
    elif c == 'h':
        print("Help: Press 'q' to quit.")
    if c == 't':
        log = logging.getLogger()
        fmt = logging.Formatter(
'%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        log.handlers[0].setFormatter(fmt)

def ctrl_thread():
    global stop_threads
    while not stop_threads:

        fd = sys.stdin.fileno()

        oldterm = termios.tcgetattr(fd)
        newattr = termios.tcgetattr(fd)
        newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
        termios.tcsetattr(fd, termios.TCSANOW, newattr)

        oldflags = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, oldflags | os.O_NONBLOCK)

        try:
            while not stop_threads:
                try:
                    c = sys.stdin.read(1)
                    if c:
                        handle_key(c)
                except IOError: pass

                sleep(0.1)

        finally:
            termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)
            fcntl.fcntl(fd, fcntl.F_SETFL, oldflags)


def log_thread():
    log = logging.getLogger('toto')
    while not stop_threads:
        log.info('toto')
        sleep(0.25)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    ctrl_thread = threading.Thread(target=ctrl_thread)
    try:
        ctrl_thread.start()
        log_thread()
    except (KeyboardInterrupt, SystemExit):
        stop_threads = True
        os.system('stty sane')
    ctrl_thread.join()
