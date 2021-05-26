from .linkacceptor import LinkAcceptor
from html.parser import HTMLParser
from typing import List, Tuple, Optional, Set
import logging
from .common import SeekerConfig
from abc import abstractmethod, ABC

logger = logging.getLogger(__name__)


class LinkParser(ABC):
    @abstractmethod  # pragma: no mutate
    def parse(self, html: str) -> List[str]:
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

    def parse(self, html: str) -> List[str]:
        parser = LinkHtmlParser(self.config.search_attrs, self.linkacceptor)
        parser.feed(html)
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
            search_attrs: Set[str],
            linkacceptor: LinkAcceptor):
        self.search_attrs = search_attrs
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
            if attr[0] in self.search_attrs:
                url = attr[1]
                if url:
                    if self.linkacceptor.accepts(url):
                        logger.debug(f'Accepting url: {url}')
                        self.links.append(url)
                    else:
                        logger.debug(f'Skipping url: {url}')
