import asyncio
import aiohttp
from .linkacceptor import LinkAcceptor, LinkAcceptorBuilder
from urllib.parse import urlparse, urljoin
from .linkparser import LinkParser
from aiohttp_retry import RetryClient, ExponentialRetry  # type: ignore
from typing import List, Set, Deque
import time
import logging

DEFAULT_WEB_AGENT: str = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)' +\
    ' AppleWebKit/537.36 (KHTML, like Gecko)' +\
    ' Chrome/60.0.3112.113 Safari/537.36'
DEFAULT_RETRY_MAX_TRIES: int = 4
DEFAULT_RETRY_MAX_TIME: int = 30
DEFAULT_VERBOSE: bool = False
DEFAULT_EXCLUDE_PREFIX: List[str] = ['mailto:', 'tel:']


class UrlTarget():
    def __init__(self, home, url):
        self.home = home
        self.url = url


class UrlFetchResponse():
    def __init__(
            self, urlTarget: UrlTarget,
            status: str, elapsed: str, html: str):
        self.urlTarget = urlTarget
        self.status = status
        self.elapsed = elapsed
        self.html = html


class DeadSeekerConfig:
    def __init__(self) -> None:
        self.verbose: bool = DEFAULT_VERBOSE
        self.max_time: int = DEFAULT_RETRY_MAX_TIME
        self.max_tries: int = DEFAULT_RETRY_MAX_TRIES
        self.linkacceptor: LinkAcceptor = \
            LinkAcceptorBuilder()\
            .addExcludePrefix(*DEFAULT_EXCLUDE_PREFIX).build()
        self.agent: str = DEFAULT_WEB_AGENT


class DeadSeeker:
    def __init__(self, config: DeadSeekerConfig) -> None:
        self.config = config

    async def _getUrlFetchResponse(
            self,
            session: aiohttp.ClientSession,
            urlTarget: UrlTarget) -> UrlFetchResponse:
        start = time.time()  # measure load time (HEAD only)
        url = urlTarget.url
        html = ''
        status = 'unknown'
        end: float = -1
        try:
            async with session.head(
                    url,
                    headers={'User-Agent': self.config.agent}) as headResponse:
                end = time.time()
                statusNum = headResponse.status
                status = str(statusNum)
                if statusNum == 200:
                    isHtml = 'html' in headResponse.headers['Content-Type']
                    onSite = urlTarget.home in url
                    if(isHtml and onSite):
                        async with session.get(
                                url,
                                headers={'User-Agent': self.config.agent}
                                ) as getResponse:
                            html = await getResponse.text(encoding="utf-8")
        except aiohttp.ClientResponseError as e:
            status = str(e.status)
        except aiohttp.ClientResponseError as e:
            status = str(e)
        if end < 0:
            end = time.time()
        elapsed = "{0:.2f} ms".format((end - start)*1000)
        return UrlFetchResponse(urlTarget, status, elapsed, html)

    async def _main(self, urls: List[str]) -> int:
        num_failures = 0
        visited: Set[str] = set()
        targets: Deque[UrlTarget] = Deque()
        for url in urls:
            visited.add(url)
            targets.appendleft(UrlTarget(url, url))
        linkparser = LinkParser(self.config.linkacceptor)
        retry_options = ExponentialRetry(
                            attempts=self.config.max_tries,
                            exceptions=[aiohttp.ClientError])
        async with RetryClient(
                raise_for_status=True, retry_options=retry_options) as session:
            while targets:
                tasks = []
                while targets:
                    urlTarget = targets.pop()
                    tasks.append(
                        asyncio.create_task(
                            self._getUrlFetchResponse(session, urlTarget)))
                for task in asyncio.as_completed(tasks):  # completed first
                    resp = await task
                    status = resp.status
                    url = resp.urlTarget.url
                    elapsed = resp.elapsed
                    self._log(f'{status} - {url} - {elapsed}')
                    if(resp.html):
                        home = resp.urlTarget.home
                        linkparser.reset()
                        linkparser.feed(resp.html)
                        for newurl in linkparser.links:
                            if not bool(
                                    urlparse(newurl).netloc):  # relative link?
                                newurl = urljoin(resp.urlTarget.home, newurl)
                            if newurl not in visited:
                                visited.add(newurl)
                                targets.appendleft(UrlTarget(home, newurl))
        return num_failures

    def _log(self, message: str) -> None:
        if self.config.verbose:
            print(message)

    def seek(self, urls: List[str]) -> int:
        start = time.time()
        num_failures = asyncio.run(self._main(urls))
        end = time.time()
        elapsedTime = "{0:.2f} ms".format((end - start)*1000)
        self._log(f'Process took {elapsedTime}')
        return num_failures
