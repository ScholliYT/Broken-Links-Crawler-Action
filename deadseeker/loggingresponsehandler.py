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
            if status:
                logger.error(f'::error ::{errortype}: {status} - {url}')
            else:
                logger.error(
                    f'::error ::{errortype}: {str(error)} - {url}')
            logger.debug("The following exception occured", exc_info=error)
        else:
            logger.info(f'{status} - {url} - {elapsedstr}')
