from .linkacceptor import LinkAcceptor
from html.parser import HTMLParser
from typing import List, Tuple, Optional
import logging
from abc import abstractmethod, ABC


search_attrs = set(['href', 'src'])
logger = logging.getLogger(__name__)


class LinkParserFactory(ABC):
    @abstractmethod  # pragma: no mutate
    def get_link_parser(self, linkacceptor: LinkAcceptor) -> HTMLParser:
        pass


class LinkParser(ABC):
    @abstractmethod  # pragma: no mutate
    def parse(self, html: str) -> List[str]:
        pass


class DefaultLinkParserFactory(LinkParserFactory):
    def get_link_parser(self, linkacceptor: LinkAcceptor) -> LinkParser:
        return DefaultLinkParser(linkacceptor)


class DefaultLinkParser:
    def __init__(self, linkacceptor: LinkAcceptor) -> None:
        self.linkacceptor = linkacceptor

    def parse(self, html: str):
        parser = LinkHtmlParser(self.linkacceptor)
        parser.feed(html)
        return parser.links


class LinkHtmlParser(HTMLParser):
    def __init__(self, linkacceptor: LinkAcceptor):
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
            if attr[0] in search_attrs:
                url = attr[1]
                if url:
                    if self.linkacceptor.accepts(url):
                        logger.debug(f'Accepting url: {url}')
                        self.links.append(url)
                    else:
                        logger.debug(f'Skipping url: {url}')
