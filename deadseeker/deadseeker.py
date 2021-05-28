import asyncio
from urllib.parse import urljoin
from typing import List, Set, Deque, Optional, Union
from .timer import Timer
import logging
from .clientsession import ClientSessionFactory, DefaultClientSessionFactory
from .common import (
    SeekerConfig,
    UrlTarget,
    SeekResults,
    UrlFetchResponse,
    UrlFetchResponseHandler
)
from .responsefetcher import (
    ResponseFetcherFactory,
    DefaultResponseFetcherFactory
)
from .linkacceptor import (
    LinkAcceptorFactory,
    DefaultLinkAcceptorFactory
)
from .linkparser import (
    LinkParser,
    LinkParserFactory,
    DefaultLinkParserFactory
)

logger = logging.getLogger(__name__)


class DeadSeeker:
    def __init__(self, config: SeekerConfig) -> None:
        self.config = config
        self.clientsessionfactory: ClientSessionFactory =\
            DefaultClientSessionFactory()
        self.responsefetcherfactory: ResponseFetcherFactory =\
            DefaultResponseFetcherFactory()
        self.linkacceptorfactory: LinkAcceptorFactory =\
            DefaultLinkAcceptorFactory()
        self.linkparserfactory: LinkParserFactory =\
            DefaultLinkParserFactory()

    async def _main(
            self,
            urls: List[str],
            responsehandler: Optional[UrlFetchResponseHandler] = None
            ) -> SeekResults:
        timer = Timer()
        results = SeekResults()
        visited: Set[str] = set()
        targets: Deque[UrlTarget] = Deque[UrlTarget]()
        for url in urls:
            visited.add(url)
            targets.appendleft(UrlTarget(url, url, self.config.max_depth))
        linkacceptor = self.linkacceptorfactory.get_link_acceptor(self.config)
        linkparser = \
            self.linkparserfactory.get_link_parser(self.config, linkacceptor)
        responsefetcher = self.responsefetcherfactory.get_response_fetcher(
                                self.config)
        async with self.clientsessionfactory.get_client_session(
                self.config) as session:
            while targets:
                tasks = []
                while targets:
                    urltarget = targets.pop()  # pragma: no mutate
                    tasks.append(
                        asyncio.create_task(
                            responsefetcher.fetch_response(
                                session, urltarget)))
                for task in asyncio.as_completed(tasks):  # completed first
                    resp = await task
                    if responsehandler:
                        responsehandler.handle_response(resp)
                    if resp.error:
                        results.failures.append(resp)
                    else:
                        results.successes.append(resp)
                    self._parse_response(visited, targets, linkparser, resp)
        results.elapsed = timer.stop() * 1000
        return results

    def _parse_response(
            self,
            visited: Set[str],
            targets: Deque[UrlTarget],
            linkparser: LinkParser,
            resp: UrlFetchResponse) -> None:
        depth = resp.urltarget.depth
        if resp.html and depth != 0:
            links = linkparser.parse(resp)
            base = resp.urltarget.url
            for newurl in links:
                newurl = urljoin(base, newurl)
                if newurl not in visited:
                    visited.add(newurl)
                    targets.appendleft(
                        UrlTarget(resp.urltarget.home, newurl, depth - 1))

    def seek(
            self,
            urls: Union[str, List[str]],
            responsehandler: UrlFetchResponseHandler = None) -> SeekResults:
        url_list = [urls] if isinstance(urls, str) else urls
        results = asyncio.run(self._main(url_list, responsehandler))
        logger.debug(f'Process took {results.elapsed:.2f}')
        return results
