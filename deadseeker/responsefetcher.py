from .common import UrlFetchResponse, UrlTarget, SeekerConfig
from aiohttp import ClientSession
from abc import abstractmethod, ABC
from .timer import Timer
import aiohttp


class ResponseFetcher:
    async def fetch_response(
            self,
            session: ClientSession,
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
        if(config.alwaysgetonsite):
            return AlwaysGetIfOnSiteResponseFetcher()
        return HeadThenGetIfHtmlResponseFetcher()


class AbstractResponseFetcher(ResponseFetcher, ABC):

    async def fetch_response(
            self,
            session: ClientSession,
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
            session: ClientSession,
            resp: UrlFetchResponse,
            urltarget: UrlTarget,
            timer: Timer) -> None:
        pass


# Optimized approach: Use HEAD request first, then only
# use a GET request if the url is onsite and has html body
class HeadThenGetIfHtmlResponseFetcher(AbstractResponseFetcher):

    async def _inner_fetch(
            self,
            session: ClientSession,
            resp: UrlFetchResponse,
            urltarget: UrlTarget,
            timer: Timer) -> None:
        url = urltarget.url
        async with session.head(url) as headresponse:
            timer.stop()
            resp.status = headresponse.status
            has_html = ('Content-Type' in headresponse.headers and
                        'html' in headresponse.headers['Content-Type'])
            onsite = urltarget.home in url
            if(has_html and onsite):
                async with session.get(url) as getresponse:
                    resp.html = await getresponse.text()


# Always uses GET requests for onsite urls, but will continue
# to use HEAD requests for offsite urls
class AlwaysGetIfOnSiteResponseFetcher(HeadThenGetIfHtmlResponseFetcher):

    async def _inner_fetch(
            self,
            session: ClientSession,
            resp: UrlFetchResponse,
            urltarget: UrlTarget,
            timer: Timer) -> None:
        url = urltarget.url
        onsite = urltarget.home in url
        if(onsite):
            async with session.get(url) as getresponse:
                resp.status = getresponse.status
                has_html = ('Content-Type' in getresponse.headers and
                            'html' in getresponse.headers['Content-Type'])
                if(has_html):
                    resp.html = await getresponse.text()
                timer.stop()
        else:
            await super()._inner_fetch(
                session,
                resp,
                urltarget,
                timer)
