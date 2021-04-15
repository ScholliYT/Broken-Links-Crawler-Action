import time


class Timer:
    def __init__(self):
        self.start: float = time.time()
        self.end: float = -1

    def stop(self):
        if(self.end < 0):
            self.end = time.time()
        return self.end - self.start
