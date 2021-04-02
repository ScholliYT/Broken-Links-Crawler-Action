import asyncio
import aiohttp
from .linkacceptor import LinkAcceptor, LinkAcceptorBuilder
from urllib.parse import urlparse, urljoin
from .linkparser import LinkParser
from aiohttp_retry import RetryClient, ExponentialRetry  # type: ignore
from typing import List, Set, Deque, Optional
import time

DEFAULT_WEB_AGENT: str = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)' +\
    ' AppleWebKit/537.36 (KHTML, like Gecko)' +\
    ' Chrome/60.0.3112.113 Safari/537.36'
DEFAULT_RETRY_MAX_TRIES: int = 4
DEFAULT_RETRY_MAX_TIME: int = 30
DEFAULT_VERBOSE: bool = False
DEFAULT_EXCLUDE_PREFIX: List[str] = ['mailto:', 'tel:']
DEFAULT_MAX_DEPTH: int = -1


class UrlTarget():
    def __init__(self, home: str, url: str, depth: int) -> None:
        self.home = home
        self.url = url
        self.depth = depth


class UrlFetchResponse():
    def __init__(self, urltarget: UrlTarget):
        self.urltarget = urltarget
        self.elapsed: float
        self.status: Optional[int] = None
        self.error: Optional[Exception] = None
        self.html: Optional[str] = None


class DeadSeekerConfig:
    def __init__(self) -> None:
        self.verbose: bool = DEFAULT_VERBOSE
        self.max_time: int = DEFAULT_RETRY_MAX_TIME
        self.max_tries: int = DEFAULT_RETRY_MAX_TRIES
        self.max_depth: int = DEFAULT_MAX_DEPTH
        self.linkacceptor: LinkAcceptor = \
            LinkAcceptorBuilder()\
            .addExcludePrefix(*DEFAULT_EXCLUDE_PREFIX).build()
        self.agent: str = DEFAULT_WEB_AGENT


class SeekResults:
    def __init__(self):
        self.successes: List[UrlFetchResponse] = list()
        self.failures: List[UrlFetchResponse] = list()
        self.elapsed: float


class DeadSeeker:
    def __init__(self, config: DeadSeekerConfig) -> None:
        self.config = config

    async def _get_urlfetchresponse(
            self,
            session: aiohttp.ClientSession,
            urltarget: UrlTarget) -> UrlFetchResponse:
        resp = UrlFetchResponse(urltarget)
        start = time.time()  # measure load time (HEAD only)
        url = urltarget.url
        end: float = -1
        try:
            async with session.head(
                    url,
                    headers={'User-Agent': self.config.agent}) as headresponse:
                end = time.time()
                resp.status = headresponse.status
                isHtml = 'html' in headresponse.headers['Content-Type']
                onSite = urltarget.home in url
                if(isHtml and onSite):
                    async with session.get(
                            url,
                            headers={'User-Agent': self.config.agent}
                            ) as getresponse:
                        resp.html = await getresponse.text()
        except aiohttp.ClientResponseError as e:
            resp.status = e.status
            resp.error = e
        except aiohttp.ClientError as e:
            resp.status = -1
            resp.error = e
        if end < 0:
            end = time.time()
        resp.elapsed = (end - start)*1000
        return resp

    async def _main(self, urls: List[str]) -> SeekResults:
        start = time.time()
        results = SeekResults()
        visited: Set[str] = set()
        targets: Deque[UrlTarget] = Deque()
        for url in urls:
            visited.add(url)
            targets.appendleft(UrlTarget(url, url, self.config.max_depth))
        linkparser = LinkParser(self.config.linkacceptor)
        retry_options = ExponentialRetry(
                            attempts=self.config.max_tries,
                            exceptions=[aiohttp.ClientError])
        async with RetryClient(
                raise_for_status=True, retry_options=retry_options) as session:
            while targets:
                tasks = []
                while targets:
                    urltarget = targets.pop()
                    tasks.append(
                        asyncio.create_task(
                            self._get_urlfetchresponse(session, urltarget)))
                for task in asyncio.as_completed(tasks):  # completed first
                    resp = await task
                    self._log_result(resp)
                    if(resp.error):
                        results.failures.append(resp)
                    else:
                        results.successes.append(resp)
                    url = resp.urltarget.url
                    depth = resp.urltarget.depth
                    if(resp.html and depth != 0):
                        home = resp.urltarget.home
                        linkparser.reset()
                        linkparser.feed(resp.html)
                        for newurl in linkparser.links:
                            if not bool(
                                    urlparse(newurl).netloc):  # relative link?
                                newurl = urljoin(resp.urltarget.home, newurl)
                            if newurl not in visited:
                                visited.add(newurl)
                                targets.appendleft(
                                    UrlTarget(home, newurl, depth - 1))
        results.elapsed = (time.time() - start) * 1000
        return results

    def _log_result(self, resp: UrlFetchResponse):
        if self.config.verbose:
            status = resp.status
            message = status if status > 0 else str(resp.error)
            url = resp.urltarget.url
            elapsed = f'{resp.elapsed:.2f} ms'
            self._log(f'{message} - {url} - {elapsed}')

    def _log(self, message: str) -> None:
        if self.config.verbose:
            print(message)

    def seek(self, urls: List[str]) -> SeekResults:
        results = asyncio.run(self._main(urls))
        self._log(f'Process took {results.elapsed:.2f}')
        return results
