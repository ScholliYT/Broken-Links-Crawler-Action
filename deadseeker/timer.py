import time
from typing import Optional


class Timer:
    def __init__(self) -> None:
        self.start: float = time.time()
        self.end: Optional[float] = None

    def stop(self) -> float:
        if (self.end is None):
            self.end = time.time()
        return self.end - self.start
