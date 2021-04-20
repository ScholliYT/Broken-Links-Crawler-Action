from aiohttp import (
    TraceConfig,
    TraceRequestStartParams,
    TraceRequestEndParams,
    TraceRequestExceptionParams,
    ClientSession
)
from asyncio import BoundedSemaphore
from .common import SeekerConfig
import logging
from types import SimpleNamespace
from typing import Union

logger = logging.getLogger(__name__)


class MaxConcurrentRequestsTraceConfigBinder:
    def bind(
            self,
            trace_config: TraceConfig,
            config: SeekerConfig) -> None:
        if(config.max_concurrequests > 0):
            sema = BoundedSemaphore(config.max_concurrequests)

            async def _acquire(
                session: ClientSession,
                trace_config_ctx: SimpleNamespace,
                params: TraceRequestStartParams
            ) -> None:
                logger.debug(f'Attempting to acquire lock: {sema!r}')
                await sema.acquire()
                logger.debug(f'Acquired lock: {sema!r}')

            async def _release(
                session: ClientSession,
                trace_config_ctx: SimpleNamespace,
                params: Union[
                    TraceRequestEndParams, TraceRequestExceptionParams]
            ) -> None:
                sema.release()
                logger.debug(f'Released lock: {sema!r}')
            trace_config.on_request_start.append(_acquire)
            trace_config.on_request_end.append(_release)
            trace_config.on_request_exception.append(_release)
