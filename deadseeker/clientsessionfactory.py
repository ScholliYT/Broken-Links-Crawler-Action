from .deadseekerconfig import DeadSeekerConfig
import aiohttp
from aiohttp_retry import RetryClient, ExponentialRetry  # type: ignore


def createClientSession(config: DeadSeekerConfig):
    retry_options = ExponentialRetry(
                        attempts=config.max_tries,
                        max_timeout=config.max_time,
                        exceptions=[aiohttp.ClientError])
    return RetryClient(
            raise_for_status=True,
            headers={'User-Agent': config.agent},
            retry_options=retry_options)
