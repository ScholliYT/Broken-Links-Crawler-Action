import unittest
from unittest.mock import patch
from deadseeker.common import UrlFetchResponse, UrlTarget
from deadseeker.loggingresponsehandler import LoggingUrlFetchResponseHandler
from logging import DEBUG, INFO, WARNING, ERROR, CRITICAL
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

    def test_no_logs_when_level_over_info(self):
        for level in [WARNING, ERROR, CRITICAL]:
            with patch.object(self.logger, 'error') as error_mock,\
                    patch.object(self.logger, 'info') as info_mock:
                self.logger.setLevel(level)
                self.testobj.handle_response(self.resp)
                self.assertFalse(
                    info_mock.called,
                    f'Did not expect any logs with level set to: {level}')
                self.assertFalse(
                    error_mock.called,
                    f'Did not expect any logs with level set to: {level}')

    def test_info_logs_when_level_at_or_under_info_and_success(self):
        self.resp.status = 200
        for level in [DEBUG, INFO]:
            with patch.object(self.logger, 'error') as error_mock,\
                    patch.object(self.logger, 'info') as info_mock:
                self.logger.setLevel(level)
                self.testobj.handle_response(self.resp)
                expected = '200 - http://testing.test.com/ - 1234.12ms'
                self.assertTrue(
                    info_mock.called_with_args(expected),
                    f'Expected info message to be logged: {expected}')
                self.assertFalse(
                    error_mock.called,
                    'Did not expect any error logs!')

    def test_error_logs_when_level_at_or_under_info_and_responseerror(self):
        self.resp.status = 400
        self.resp.error = ClientError()
        for level in [DEBUG, INFO]:
            with patch.object(self.logger, 'error') as error_mock,\
                    patch.object(self.logger, 'info') as info_mock:
                self.logger.setLevel(level)
                self.testobj.handle_response(self.resp)
                expected = '::error ::ClientError: 400' +\
                    ' - http://testing.test.com/'
                self.assertTrue(
                    error_mock.called_with_args(expected),
                    f'Expected error message to be logged: {expected}')
                self.assertFalse(
                    info_mock.called,
                    'Did not expect any info logs!')

    def test_error_logs_when_level_at_or_under_info_and_no_status_error(self):
        self.resp.error = ClientError('test error')
        for level in [DEBUG, INFO]:
            with patch.object(self.logger, 'error') as error_mock,\
                    patch.object(self.logger, 'info') as info_mock:
                self.logger.setLevel(level)
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
