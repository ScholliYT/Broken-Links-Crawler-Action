from typing import Optional, List, Set

DEFAULT_WEB_AGENT: str = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)' +\
    ' AppleWebKit/537.36 (KHTML, like Gecko)' +\
    ' Chrome/133.0.0.0 Safari/537.36'
DEFAULT_RETRY_MAX_TRIES: int = 4
DEFAULT_RETRY_MAX_TIME: int = 30
DEFAULT_EXCLUDE_PREFIX: List[str] = ['mailto:', 'tel:']
DEFAULT_MAX_DEPTH: int = -1
DEFAULT_CONNECT_LIMIT_PER_HOST: int = 10
DEFAULT_TIMEOUT: int = 60
DEFAULT_SEARCH_ATTRS: Set[str] = set(['href', 'src'])


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
        self.search_attrs: Set[str] = DEFAULT_SEARCH_ATTRS
        self.agent: str = DEFAULT_WEB_AGENT
        self.alwaysgetonsite: bool = False
        self.resolvebeforefilter: bool = False
        self.connect_limit_per_host: int = \
            DEFAULT_CONNECT_LIMIT_PER_HOST
        self.timeout: int = DEFAULT_TIMEOUT


class UrlTarget():
    def __init__(self, home: str, url: str, depth: int) -> None:
        self.home = home
        self.url = url
        self.depth = depth
        # We don't know the parent element (yet)
        self.parent: Optional[UrlTarget] = None

    def child(self, url: str) -> 'UrlTarget':
        child = UrlTarget(self.home, url, self.depth - 1)
        # We store the parent Url from where we found this one in the parent
        child.parent = self
        return child

    def parent_urls(self) -> List[str]:
        if self.parent:
            return self.parent.parent_urls() + [self.parent.url]
        else:
            return []


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
