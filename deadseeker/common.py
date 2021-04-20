from typing import Optional, List

DEFAULT_WEB_AGENT: str = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)' +\
    ' AppleWebKit/537.36 (KHTML, like Gecko)' +\
    ' Chrome/60.0.3112.113 Safari/537.36'
DEFAULT_RETRY_MAX_TRIES: int = 4
DEFAULT_RETRY_MAX_TIME: int = 30
DEFAULT_EXCLUDE_PREFIX: List[str] = ['mailto:', 'tel:']
DEFAULT_MAX_DEPTH: int = -1
DEFAULT_MAX_CONCURRENT_REQUESTS: int = 0


class SeekerConfig:
    def __init__(self) -> None:
        self.max_time: int = DEFAULT_RETRY_MAX_TIME
        self.max_tries: int = DEFAULT_RETRY_MAX_TRIES
        self.max_depth: int = DEFAULT_MAX_DEPTH
        self.includeprefix: List[str] = []
        self.excludeprefix: List[str] = DEFAULT_EXCLUDE_PREFIX
        self.includesuffix: List[str] = []
        self.excludesuffix: List[str] = []
        self.includecontained: List[str] = []
        self.excludecontained: List[str] = []
        self.agent: str = DEFAULT_WEB_AGENT
        self.alwaysgetonsite: bool = False
        self.max_concurrequests: int = \
            DEFAULT_MAX_CONCURRENT_REQUESTS


class UrlTarget():
    def __init__(self, home: str, url: str, depth: int) -> None:
        self.home = home
        self.url = url
        self.depth = depth


class UrlFetchResponse():
    def __init__(self, urltarget: UrlTarget):
        self.urltarget = urltarget
        self.elapsed: float
        self.status: int = 0
        self.error: Optional[Exception] = None
        self.html: Optional[str] = None


class UrlFetchResponseHandler:
    def handle_response(self, resp: UrlFetchResponse) -> None:
        pass


class SeekResults:
    def __init__(self) -> None:
        self.successes: List[UrlFetchResponse] = list()
        self.failures: List[UrlFetchResponse] = list()
        self.elapsed: float
