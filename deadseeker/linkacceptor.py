from typing import List, TypeVar, Generic
from abc import abstractmethod, ABC

T = TypeVar('T')


class LinkAcceptor(ABC):
    @abstractmethod
    def accepts(self, link: str) -> bool:
        pass


class AbstractLinkAcceptor(LinkAcceptor, Generic[T]):
    def __init__(self, values: List[T]) -> None:
        self.values = tuple(values)


class NotLinkAcceptor(LinkAcceptor):
    def __init__(self, source: LinkAcceptor) -> None:
        self.source = source

    def accepts(self, link: str) -> bool:
        return not self.source.accepts(link)


class CompositeLinkAcceptor(AbstractLinkAcceptor[LinkAcceptor]):
    def __init__(self, acceptors: List[LinkAcceptor]) -> None:
        self.acceptors = tuple(acceptors)

    def accepts(self, link: str) -> bool:
        for acceptor in self.acceptors:
            if not acceptor.accepts(link):
                return False
        return True


class IncludePrefixLinkAcceptor(AbstractLinkAcceptor[str]):
    def accepts(self, link: str) -> bool:
        return link.startswith(self.values)


class IncludeSuffixLinkAcceptor(AbstractLinkAcceptor[str]):
    def accepts(self, link: str) -> bool:
        return link.endswith(self.values)


class IncludeContainedLinkAcceptor(AbstractLinkAcceptor[str]):
    def accepts(self, link: str) -> bool:
        return any(s in link for s in self.values)


class AcceptAllLinkAcceptor(LinkAcceptor):
    def accepts(self, link: str) -> bool:
        return True


class LinkAcceptorBuilder:
    def __init__(self) -> None:
        self.acceptors: List[LinkAcceptor] = []

    def addIncludePrefix(self, *args: str):
        if args:
            self.acceptors.append(IncludePrefixLinkAcceptor(list(args)))
        return self

    def addExcludePrefix(self, *args: str):
        if args:
            self.acceptors.append(NotLinkAcceptor(
                IncludePrefixLinkAcceptor(list(args))))
        return self

    def addIncludeSuffix(self, *args: str):
        if args:
            self.acceptors.append(IncludeSuffixLinkAcceptor(list(args)))
        return self

    def addExcludeSuffix(self, *args: str):
        if args:
            self.acceptors.append(NotLinkAcceptor(
                IncludeSuffixLinkAcceptor(list(args))))
        return self

    def addIncludeContained(self, *args: str):
        if args:
            self.acceptors.append(IncludeContainedLinkAcceptor(list(args)))
        return self

    def addExcludeContained(self, *args: str):
        if args:
            self.acceptors.append(NotLinkAcceptor(
                IncludeContainedLinkAcceptor(list(args))))
        return self

    def build(self) -> LinkAcceptor:
        if self.acceptors:
            return CompositeLinkAcceptor(self.acceptors)
        return AcceptAllLinkAcceptor()
