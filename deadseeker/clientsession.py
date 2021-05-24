from .common import SeekerConfig
import aiohttp
import asyncio
import logging
from types import SimpleNamespace
from aiohttp import (
    ClientSession,
    TraceConfig,
    TraceRequestStartParams,
    TCPConnector,
    ClientTimeout
)
from aiohttp_retry import RetryClient, ExponentialRetry  # type: ignore
from abc import abstractmethod, ABC

logger = logging.getLogger(__name__)


class ClientSessionFactory(ABC):
    @abstractmethod  # pragma: no mutate
    def get_client_session(self, config: SeekerConfig) -> ClientSession:
        pass


class DefaultClientSessionFactory(ClientSessionFactory):

    def get_client_session(self, config: SeekerConfig) -> ClientSession:
        async def _on_request_start(
            session: ClientSession,
            trace_config_ctx: SimpleNamespace,
            params: TraceRequestStartParams
        ) -> None:
            current_attempt = \
                trace_config_ctx.trace_request_ctx['current_attempt']
            if(current_attempt > 1):
                logger.warning(
                    f'::warn ::Retry Attempt #{current_attempt} ' +
                    f'of {config.max_tries}: {params.url}')
        trace_config = TraceConfig()
        trace_config.on_request_start.append(_on_request_start)
        limit_per_host = max(0, config.connect_limit_per_host)
        connector = TCPConnector(
            limit_per_host=limit_per_host,
            ttl_dns_cache=600  # 10-minute DNS cache
        )
        retry_options = ExponentialRetry(
                            attempts=config.max_tries,
                            max_timeout=config.max_time,
                            exceptions=[
                                aiohttp.ClientError,
                                asyncio.TimeoutError
                            ])
        return RetryClient(
                raise_for_status=True,
                connector=connector,
                timeout=ClientTimeout(total=60),
                headers={'User-Agent': config.agent},
                retry_options=retry_options,
                trace_configs=[trace_config])
