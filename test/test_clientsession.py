import unittest
from aiounittest import AsyncTestCase
from unittest.mock import Mock, patch
from deadseeker.clientsession import DefaultClientSessionFactory
from deadseeker.common import SeekerConfig
import aiohttp
from types import SimpleNamespace
from aiohttp import ClientSession, TraceRequestStartParams
import logging


TEST_AGENT = 'TEST_AGENT'


class TestDefaultClientSessionFactory(AsyncTestCase):

    def setUp(self):
        self.testObj = DefaultClientSessionFactory()
        self.config = Mock(spec=SeekerConfig)
        self.config.agent = TEST_AGENT
        self.config.max_tries = 3
        self.config.max_time = 45
        self.retryclient_mock = patch('deadseeker.clientsession.RetryClient')
        self.retryclient = self.retryclient_mock.start()
        self.exponentialretry_mock = patch(
            'deadseeker.clientsession.ExponentialRetry')
        self.exponentialretry = self.exponentialretry_mock.start()
        self.traceconfig_mock = patch(
            'deadseeker.clientsession.TraceConfig')
        self.traceconfig = self.traceconfig_mock.start()
        self.maxconcurrentrequestsbinder_patch = patch(
            'deadseeker.clientsession.MaxConcurrentRequestsTraceConfigBinder')
        self.maxconcurrentrequestsbinder = \
            self.maxconcurrentrequestsbinder_patch.start()

    def tearDown(self):
        self.retryclient_mock.stop()
        self.exponentialretry_mock.stop()
        self.traceconfig_mock.stop()
        self.maxconcurrentrequestsbinder_patch.stop()

    def test_retryclient_returned(self):
        actualresult = self.testObj.get_client_session(
                self.config)
        self.assertIs(actualresult, self.retryclient.return_value)
        self.retryclient.assert_called_with(
                raise_for_status=True,
                headers={'User-Agent': TEST_AGENT},
                retry_options=self.exponentialretry.return_value,
                trace_configs=[self.traceconfig.return_value])

    def test_retry_options_configuration(self):
        self.testObj.get_client_session(
                self.config)
        self.exponentialretry.assert_called_with(
                            attempts=self.config.max_tries,
                            max_timeout=self.config.max_time,
                            exceptions=[aiohttp.ClientError])

    async def test_traceconfig_configuration(self):
        self.testObj.get_client_session(
                self.config)
        self.traceconfig.assert_called_once()
        instance = self.traceconfig.return_value
        append = instance.on_request_start.append
        append.assert_called_once()
        thecall = append.call_args_list[0]
        func = thecall.args[0]
        session = Mock(spec=ClientSession)
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

    def test_maxconcurrequests_bind_called(self):
        self.testObj.get_client_session(
                self.config)
        instance = self.maxconcurrentrequestsbinder.return_value
        instance.bind.assert_called_with(
            self.traceconfig.return_value, self.config)


if __name__ == '__main__':
    unittest.main()
