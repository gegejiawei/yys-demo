from sys import argv
from datetime import datetime


class LOG(object):
    def __init__(self, debug_mode=False):
        self.debug_mode = debug_mode

    def debug(self, text: str) -> None:
        if self.debug_mode:
            print(f"[DBUG] <{datetime.now().strftime('%H:%M:%S')}> => {text}")
