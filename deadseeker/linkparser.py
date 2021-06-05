from .linkacceptor import LinkAcceptor
from html.parser import HTMLParser
from urllib.parse import urljoin
from typing import List, Tuple, Optional
import logging
from .common import SeekerConfig, UrlFetchResponse
from abc import abstractmethod, ABC

logger = logging.getLogger(__name__)


class LinkParser(ABC):
    @abstractmethod  # pragma: no mutate
    def parse(self, resp: UrlFetchResponse) -> List[str]:
        pass


class LinkParserFactory(ABC):
    @abstractmethod  # pragma: no mutate
    def get_link_parser(
            self,
            config: SeekerConfig,
            linkacceptor: LinkAcceptor) -> LinkParser:
        pass


class DefaultLinkParser(LinkParser):
    def __init__(
            self,
            config: SeekerConfig,
            linkacceptor: LinkAcceptor) -> None:
        self.config = config
        self.linkacceptor = linkacceptor

    def parse(self, resp: UrlFetchResponse) -> List[str]:
        parser = LinkHtmlParser(resp, self.config, self.linkacceptor)
        parser.parse()
        return parser.links


class DefaultLinkParserFactory(LinkParserFactory):
    def get_link_parser(
            self,
            config: SeekerConfig,
            linkacceptor: LinkAcceptor) -> LinkParser:
        return DefaultLinkParser(config, linkacceptor)


class LinkHtmlParser(HTMLParser):
    def __init__(
            self,
            resp: UrlFetchResponse,
            config: SeekerConfig,
            linkacceptor: LinkAcceptor):
        self.resp = resp
        self.config = config
        self.linkacceptor = linkacceptor
        self.links: List[str] = list()
        super().__init__()

    def reset(self) -> None:
        super().reset()
        self.links.clear()

    def handle_starttag(
            self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        '''Override parent method and check tag for our attributes'''
        for attr in attrs:
            # ('href', 'http://google.com')
            if attr[0] in self.config.search_attrs:
                url = attr[1]
                if url:
                    if self.config.resolvebeforefilter:
                        url = urljoin(self.resp.urltarget.url, url)
                    if self.linkacceptor.accepts(url):
                        logger.debug(f'Accepting url: {url}')
                        self.links.append(url)
                    else:
                        logger.debug(f'Skipping url: {url}')

    def parse(self) -> None:
        if self.resp.html:
            super().feed(self.resp.html)
