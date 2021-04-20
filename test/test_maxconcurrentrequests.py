import aiounittest
from aiounittest import AsyncTestCase
from unittest.mock import Mock, patch, AsyncMock, call
from aiohttp import (
    TraceConfig,
    TraceRequestStartParams,
    ClientSession
)
from deadseeker.common import SeekerConfig
from deadseeker.maxconcurrentrequests import (
    MaxConcurrentRequestsTraceConfigBinder
)
import logging
from types import SimpleNamespace


class TestMaxConcurrentRequestsTraceConfigBinder(AsyncTestCase):

    def setUp(self):
        self.testobj = MaxConcurrentRequestsTraceConfigBinder()
        self.config = Mock(spec=SeekerConfig)
        self.trace_config = Mock(spec=TraceConfig)
        self.session = Mock(spec=ClientSession)
        self.trace_config_ctx = Mock(spec=SimpleNamespace)
        self.params = Mock(spec=TraceRequestStartParams)
        self.sema_patch = \
            patch('deadseeker.maxconcurrentrequests.BoundedSemaphore')
        self.sema_class = self.sema_patch.start()
        logger = logging.getLogger('deadseeker.maxconcurrentrequests')
        self.debug_patch = patch.object(logger, 'debug')
        self.debug = self.debug_patch.start()

    def tearDown(self):
        self.sema_patch.stop()
        self.debug.stop()

    def test_when_max_concurrequests_not_valued(self):
        self.config.max_concurrequests = 0
        self.testobj.bind(self.trace_config, self.config)
        self.sema_class.assert_not_called()
        self.trace_config.on_request_start.append.assert_not_called()
        self.trace_config.on_request_end.append.assert_not_called()
        self.trace_config.on_request_exception.append.assert_not_called()

    def test_when_max_concurrequests_valued(self):
        self.config.max_concurrequests = 1
        self.testobj.bind(self.trace_config, self.config)
        self.sema_class.assert_called_with(self.config.max_concurrequests)
        self.trace_config.on_request_start.append.assert_called_once()
        self.trace_config.on_request_end.append.assert_called_once()
        self.trace_config.on_request_exception.append.assert_called_once()

    def test_request_end_same_as_request_exception(self):
        self.config.max_concurrequests = 2
        self.testobj.bind(self.trace_config, self.config)
        end_func = self.get_inner_func(self.trace_config.on_request_end)
        except_func = \
            self.get_inner_func(self.trace_config.on_request_exception)
        self.assertIs(end_func, except_func)

    async def test_request_start(self):
        self.config.max_concurrequests = 3
        self.sema_class.return_value.acquire = AsyncMock()
        self.sema_class.return_value.__repr__ = \
            Mock(return_value='[semaphore]')
        self.testobj.bind(self.trace_config, self.config)
        start_func = self.get_inner_func(self.trace_config.on_request_start)
        await start_func(self.session, self.trace_config_ctx, self.params)
        self.sema_class.return_value.acquire.assert_awaited_once()
        self.debug.assert_has_calls([
            call('Attempting to acquire lock: [semaphore]'),
            call('Acquired lock: [semaphore]')
        ])

    async def test_request_end(self):
        self.config.max_concurrequests = 3
        self.sema_class.return_value.acquire = AsyncMock()
        self.sema_class.return_value.__repr__ = \
            Mock(return_value='[semaphore]')
        self.testobj.bind(self.trace_config, self.config)
        end_func = self.get_inner_func(self.trace_config.on_request_end)
        await end_func(self.session, self.trace_config_ctx, self.params)
        self.sema_class.return_value.release.assert_called_once()
        self.debug.assert_called_once_with('Released lock: [semaphore]')

    def get_inner_func(self, event):
        event.append.assert_called_once()
        return event.append.call_args.args[0]


if __name__ == '__main__':
    aiounittest.main()
