import unittest
from unittest.mock import patch
from deadseeker.common import UrlFetchResponse, UrlTarget
from deadseeker.loggingresponsehandler import LoggingUrlFetchResponseHandler
from aiohttp import ClientError
import logging

TEST_URL = 'http://testing.test.com/'


class TestLoggingResponseHandler(unittest.TestCase):

    def setUp(self):
        self.testobj = LoggingUrlFetchResponseHandler()
        target = UrlTarget(TEST_URL, TEST_URL, 0)
        self.resp = UrlFetchResponse(target)
        self.resp.elapsed = 1234.1234
        self.logger = logging.getLogger('deadseeker.loggingresponsehandler')

    def test_info_logs_when_success(self):
        self.resp.status = 200
        with patch.object(self.logger, 'error') as error_mock,\
                patch.object(self.logger, 'info') as info_mock:
            self.testobj.handle_response(self.resp)
            expected = '200 - http://testing.test.com/ - 1234.12ms'
            self.assertTrue(
                info_mock.called_with_args(expected),
                f'Expected info message to be logged: {expected}')
            self.assertFalse(
                error_mock.called,
                'Did not expect any error logs!')

    def test_error_logs_when_responseerror(self):
        self.resp.status = 400
        self.resp.error = ClientError()
        with patch.object(self.logger, 'error') as error_mock,\
                patch.object(self.logger, 'info') as info_mock:
            self.testobj.handle_response(self.resp)
            expected = '::error ::ClientError: 400' +\
                ' - http://testing.test.com/'
            self.assertTrue(
                error_mock.called_with_args(expected),
                f'Expected error message to be logged: {expected}')
            self.assertFalse(
                info_mock.called,
                'Did not expect any info logs!')

    def test_error_logs_when_no_status_error(self):
        self.resp.error = ClientError('test error')
        with patch.object(self.logger, 'error') as error_mock,\
                patch.object(self.logger, 'info') as info_mock:
            self.testobj.handle_response(self.resp)
            expected = '::error ::ClientError: test error' +\
                ' - http://testing.test.com/'
            self.assertTrue(
                error_mock.called_with_args(expected),
                f'Expected error message to be logged: {expected}')
            self.assertFalse(
                info_mock.called,
                'Did not expect any info logs!')


if __name__ == '__main__':
    unittest.main()
