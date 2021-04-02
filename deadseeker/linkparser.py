from .linkacceptor import LinkAcceptor
from html.parser import HTMLParser
from typing import List
import logging


search_attrs = set(['href', 'src'])
logger = logging.getLogger(__name__)


class LinkParser(HTMLParser):
    def __init__(self, linkacceptor: LinkAcceptor):
        self.linkacceptor = linkacceptor
        self.links: List[str] = list()
        super().__init__()

    def reset(self):
        super().reset()
        self.links.clear()

    def handle_starttag(self, tag, attrs):
        '''Override parent method and check tag for our attributes'''
        for attr in attrs:
            # ('href', 'http://google.com')
            if attr[0] in search_attrs:
                url = attr[1]
                if self.linkacceptor.accepts(url):
                    logger.debug(f'Accepting url: {url}')
                    self.links.append(attr[1])
                else:
                    logger.debug(f'Skipping url: {url}')
