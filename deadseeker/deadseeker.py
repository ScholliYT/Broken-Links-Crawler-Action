import asyncio
import aiohttp
from urllib.parse import urlparse, urljoin
from .linkparser import LinkParser
from typing import List, Set, Deque
import time
import logging
from .clientsessionfactory import ClientSessionFactory
from .common import (
    SeekerConfig,
    UrlFetchResponse,
    UrlTarget,
    SeekResults
)

logger = logging.getLogger(__name__)


class DeadSeeker:
    def __init__(self, config: SeekerConfig) -> None:
        self.config = config
        self.clientSessionFactory = ClientSessionFactory()

    async def _get_urlfetchresponse(
            self,
            session: aiohttp.ClientSession,
            urltarget: UrlTarget) -> UrlFetchResponse:
        resp = UrlFetchResponse(urltarget)
        start = time.time()  # measure load time (HEAD only)
        url = urltarget.url
        end: float = -1
        try:
            async with session.head(url) as headresponse:
                end = time.time()
                resp.status = headresponse.status
                has_html = 'html' in headresponse.headers['Content-Type']
                onsite = urltarget.home in url
                if(has_html and onsite):
                    async with session.get(url) as getresponse:
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
        async with self.clientSessionFactory.createClientSession(
                self.config) as session:
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
                                newurl = urljoin(url, newurl)
                            if newurl not in visited:
                                visited.add(newurl)
                                targets.appendleft(
                                    UrlTarget(home, newurl, depth - 1))
        results.elapsed = (time.time() - start) * 1000
        return results

    def _log_result(self, resp: UrlFetchResponse):
        if logging.INFO >= logger.getEffectiveLevel():
            status = resp.status
            url = resp.urltarget.url
            elapsed = f'{resp.elapsed:.2f} ms'
            error = resp.error
            if error:
                errortype = type(error).__name__
                if status:
                    logger.error(f'::error ::{errortype}: {status} - {url}')
                else:
                    logger.error(
                        f'::error ::{errortype}: {str(error)} - {url}')
            else:
                logger.info(f'{status} - {url} - {elapsed}')

    def seek(self, urls: List[str]) -> SeekResults:
        results = asyncio.run(self._main(urls))
        logger.debug(f'Process took {results.elapsed:.2f}')
        return results
