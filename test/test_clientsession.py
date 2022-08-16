import unittest
from aiounittest import AsyncTestCase
from unittest.mock import Mock, patch
from deadseeker.clientsession import DefaultClientSessionFactory
from deadseeker.common import SeekerConfig
import aiohttp
import asyncio
from types import SimpleNamespace
from aiohttp import TraceRequestStartParams
from aiohttp_retry.types import ClientType
import logging


TEST_AGENT = 'TEST_AGENT'


class TestDefaultClientSessionFactory(AsyncTestCase):

    def setUp(self):
        self.testObj = DefaultClientSessionFactory()
        self.config = Mock(spec=SeekerConfig)
        self.config.agent = TEST_AGENT
        self.config.max_tries = 3
        self.config.max_time = 45
        self.config.connect_limit_per_host = 0
        self.config.timeout = 60
        self.retryclient_mock = patch('deadseeker.clientsession.RetryClient')
        self.retryclient = self.retryclient_mock.start()
        self.exponentialretry_mock = patch(
            'deadseeker.clientsession.ExponentialRetry')
        self.exponentialretry = self.exponentialretry_mock.start()
        self.traceconfig_mock = patch(
            'deadseeker.clientsession.TraceConfig')
        self.traceconfig = self.traceconfig_mock.start()
        self.tcpconnector_patch = patch(
            'deadseeker.clientsession.TCPConnector')
        self.tcpconnector = \
            self.tcpconnector_patch.start()
        self.clienttimeout_patch = patch(
            'deadseeker.clientsession.ClientTimeout')
        self.clienttimeout = self.clienttimeout_patch.start()

    def tearDown(self):
        self.retryclient_mock.stop()
        self.exponentialretry_mock.stop()
        self.traceconfig_mock.stop()
        self.tcpconnector_patch.stop()
        self.clienttimeout_patch.stop()

    def test_retryclient_returned(self):
        actualresult = self.testObj.get_client_session(
                self.config)
        self.assertIs(actualresult, self.retryclient.return_value)
        self.clienttimeout.assert_called_with(total=60)
        self.retryclient.assert_called_with(
                raise_for_status=True,
                connector=self.tcpconnector.return_value,
                timeout=self.clienttimeout.return_value,
                headers={'User-Agent': TEST_AGENT},
                retry_options=self.exponentialretry.return_value,
                trace_configs=[self.traceconfig.return_value])

    def test_retry_options_configuration(self):
        self.testObj.get_client_session(
                self.config)
        self.exponentialretry.assert_called_with(
                            attempts=self.config.max_tries,
                            max_timeout=self.config.max_time,
                            exceptions={
                                aiohttp.ClientError,
                                asyncio.TimeoutError
                            })

    async def test_traceconfig_configuration(self):
        self.testObj.get_client_session(
                self.config)
        self.traceconfig.assert_called_once()
        instance = self.traceconfig.return_value
        append = instance.on_request_start.append
        append.assert_called_once()
        thecall = append.call_args_list[0]
        func = thecall.args[0]
        session = Mock(spec=ClientType)
        trace_config_ctx = Mock(spec=SimpleNamespace)
        ctx = dict()
        trace_config_ctx.trace_request_ctx = ctx
        params = Mock(spec=TraceRequestStartParams)
        params.url = 'http://test.com/'
        logger = logging.getLogger('deadseeker.clientsession')
        ctx['current_attempt'] = 1
        with patch.object(logger, 'warning') as warning_mock:
            await func(session, trace_config_ctx, params)
            warning_mock.assert_not_called()
        ctx['current_attempt'] = 2
        with patch.object(logger, 'warning') as warning_mock:
            await func(session, trace_config_ctx, params)
            warning_mock.assert_called_with(
                    '::warn ::Retry Attempt #2 ' +
                    'of 3: http://test.com/')
        ctx['current_attempt'] = 3
        with patch.object(logger, 'warning') as warning_mock:
            await func(session, trace_config_ctx, params)
            warning_mock.assert_called_with(
                    '::warn ::Retry Attempt #3 ' +
                    'of 3: http://test.com/')

    def test_zero_used_if_connect_limit_is_zero(self):
        self.config.connect_limit_per_host = 0
        self.testObj.get_client_session(
                self.config)
        self.tcpconnector.assert_called_with(
            limit_per_host=0,
            ttl_dns_cache=600
        )

    def test_zero_used_if_connect_limit_lt_zero(self):
        self.config.connect_limit_per_host = -100
        self.testObj.get_client_session(
                self.config)
        self.tcpconnector.assert_called_with(
            limit_per_host=0,
            ttl_dns_cache=600
        )

    def test_one_used_if_connect_limit_is_one(self):
        self.config.connect_limit_per_host = 1
        self.testObj.get_client_session(
                self.config)
        self.tcpconnector.assert_called_with(
            limit_per_host=1,
            ttl_dns_cache=600
        )


if __name__ == '__main__':
    unittest.main()
