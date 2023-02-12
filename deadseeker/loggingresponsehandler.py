from .common import UrlFetchResponse, UrlFetchResponseHandler
import logging

logger = logging.getLogger(__name__)


class LoggingUrlFetchResponseHandler(UrlFetchResponseHandler):
    def handle_response(self, resp: UrlFetchResponse) -> None:
        status = resp.status
        url = resp.urltarget.url
        elapsed = resp.elapsed
        elapsedstr = f'{elapsed:.2f} ms'
        error = resp.error
        if error:
            errortype = type(error).__name__

            navigation_path = " -> ".join(resp.urltarget.parent_urls())
            navigation_path_msg = ""
            if navigation_path:
                navigation_path_msg = " found by navigating through: " + navigation_path

            if status:
                logger.error(f'::error ::{errortype}: {status} - {url}{navigation_path_msg}')
            else:
                logger.error(
                    f'::error ::{errortype}: {str(error)} - {url}{navigation_path_msg}')
            logger.debug("The following exception occured", exc_info=error)
        else:
            logger.info(f'{status} - {url} - {elapsedstr}')
