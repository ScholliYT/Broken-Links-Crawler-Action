import time


class Timer:
    def __init__(self) -> None:
        self.start: float = time.time()
        self.end: float

    def stop(self) -> float:
        if(not self.end):
            self.end = time.time()
        return self.end - self.start
