from typing import List
from .linkacceptor import LinkAcceptorBuilder, LinkAcceptor

DEFAULT_WEB_AGENT: str = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)' +\
    ' AppleWebKit/537.36 (KHTML, like Gecko)' +\
    ' Chrome/60.0.3112.113 Safari/537.36'
DEFAULT_RETRY_MAX_TRIES: int = 4
DEFAULT_RETRY_MAX_TIME: int = 30
DEFAULT_EXCLUDE_PREFIX: List[str] = ['mailto:', 'tel:']
DEFAULT_MAX_DEPTH: int = -1


class DeadSeekerConfig:
    def __init__(self) -> None:
        self.max_time: int = DEFAULT_RETRY_MAX_TIME
        self.max_tries: int = DEFAULT_RETRY_MAX_TRIES
        self.max_depth: int = DEFAULT_MAX_DEPTH
        self.linkacceptor: LinkAcceptor = \
            LinkAcceptorBuilder()\
            .addExcludePrefix(*DEFAULT_EXCLUDE_PREFIX).build()
        self.agent: str = DEFAULT_WEB_AGENT
