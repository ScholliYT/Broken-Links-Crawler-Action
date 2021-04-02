from .deadseekerconfig import DeadSeekerConfig
import aiohttp
import logging
from types import SimpleNamespace
from aiohttp import ClientSession, TraceConfig, TraceRequestStartParams
from aiohttp_retry import RetryClient, ExponentialRetry  # type: ignore

logger = logging.getLogger(__name__)


async def _on_request_start(
    session: ClientSession,
    trace_config_ctx: SimpleNamespace,
    params: TraceRequestStartParams,
) -> None:
    current_attempt = trace_config_ctx.trace_request_ctx['current_attempt']
    if(current_attempt > 1):
        logger.warning(
            f'::warn ::Retry Attempt #{current_attempt}: {params.url}')


def createClientSession(config: DeadSeekerConfig):
    trace_config = TraceConfig()
    trace_config.on_request_start.append(_on_request_start)
    retry_options = ExponentialRetry(
                        attempts=config.max_tries,
                        max_timeout=config.max_time,
                        exceptions=[aiohttp.ClientError])
    return RetryClient(
            raise_for_status=True,
            headers={'User-Agent': config.agent},
            retry_options=retry_options,
            trace_configs=[trace_config])
