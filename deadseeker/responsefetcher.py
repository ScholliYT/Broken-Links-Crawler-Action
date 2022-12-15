from .common import UrlFetchResponse, UrlTarget, SeekerConfig
from aiohttp import ClientResponse
from aiohttp_retry.types import ClientType
from abc import abstractmethod, ABC
from .timer import Timer
import aiohttp


class ResponseFetcher:
    async def fetch_response(  # type: ignore [empty-body]
            self,
            session: ClientType,
            urltarget: UrlTarget) -> UrlFetchResponse:
        pass


class ResponseFetcherFactory(ABC):
    @abstractmethod  # pragma: no mutate
    def get_response_fetcher(
            self,
            config: SeekerConfig) -> ResponseFetcher:
        pass


class DefaultResponseFetcherFactory(ResponseFetcherFactory):
    def get_response_fetcher(
            self,
            config: SeekerConfig) -> ResponseFetcher:
        if (config.alwaysgetonsite):
            return AlwaysGetIfOnSiteResponseFetcher()
        return HeadThenGetIfHtmlResponseFetcher()


class AbstractResponseFetcher(ResponseFetcher, ABC):

    async def fetch_response(
            self,
            session: ClientType,
            urltarget: UrlTarget) -> UrlFetchResponse:
        resp = UrlFetchResponse(urltarget)
        timer = Timer()
        try:
            await self._inner_fetch(session, resp, urltarget, timer)
        except aiohttp.ClientResponseError as e:
            resp.status = e.status
            resp.error = e
        except Exception as e:
            resp.error = e
        resp.elapsed = timer.stop()*1000
        return resp

    @abstractmethod  # pragma: no mutate
    async def _inner_fetch(
            self,
            session: ClientType,
            resp: UrlFetchResponse,
            urltarget: UrlTarget,
            timer: Timer) -> None:
        pass

    async def _do_get(
            self,
            session: ClientType,
            resp: UrlFetchResponse,
            urltarget: UrlTarget,
            timer: Timer) -> None:
        url = urltarget.url
        async with session.get(url) as response:
            timer.stop()
            resp.status = response.status
            if has_html(response) and is_onsite(urltarget):
                resp.html = await response.text()


def has_html(response: ClientResponse) -> bool:
    return ('Content-Type' in response.headers and
            'html' in response.content_type)


def is_onsite(urltarget: UrlTarget) -> bool:
    return urltarget.home in urltarget.url


# Optimized approach: Use HEAD request first, then only
# use a GET request if the url is onsite and has html body
class HeadThenGetIfHtmlResponseFetcher(AbstractResponseFetcher):

    async def _inner_fetch(
            self,
            session: ClientType,
            resp: UrlFetchResponse,
            urltarget: UrlTarget,
            timer: Timer) -> None:
        head_not_allowed = False  # pragma: no mutate
        is_html_content = False  # pragma: no mutate
        try:
            async with session.head(urltarget.url) as response:
                timer.stop()
                resp.status = response.status
                is_html_content = has_html(response)
        except aiohttp.ClientResponseError as e:
            # Fixes ScholliYT/Broken-Links-Crawler-Action#8
            if e.status == 405:
                head_not_allowed = True
            else:
                raise e

        if head_not_allowed or (is_onsite(urltarget) and is_html_content):
            await self._do_get(session, resp, urltarget, timer)


# Always uses GET requests for onsite urls, but will continue
# to use HEAD requests for offsite urls
class AlwaysGetIfOnSiteResponseFetcher(HeadThenGetIfHtmlResponseFetcher):

    async def _inner_fetch(
            self,
            session: ClientType,
            resp: UrlFetchResponse,
            urltarget: UrlTarget,
            timer: Timer) -> None:
        if (is_onsite(urltarget)):
            await self._do_get(session, resp, urltarget, timer)
        else:
            await super()._inner_fetch(
                session,
                resp,
                urltarget,
                timer)
