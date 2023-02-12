import unittest
from unittest.mock import patch
from deadseeker.common import UrlFetchResponse, UrlTarget
from deadseeker.loggingresponsehandler import LoggingUrlFetchResponseHandler
from aiohttp import ClientError
import logging

TEST_URL = 'http://testing.test.com/'
TEST_SUBPAGE_URL = 'http://subpage.testing.test.com/'


class TestLoggingResponseHandler(unittest.TestCase):

    def setUp(self):
        self.testobj = LoggingUrlFetchResponseHandler()
        target = UrlTarget(TEST_URL, TEST_URL, 0)

        self.resp = UrlFetchResponse(target)
        self.resp.elapsed = 1234.1234

        subpage_target = target.child(TEST_SUBPAGE_URL).child(TEST_SUBPAGE_URL + 'page1')
        self.subpage_response = UrlFetchResponse(subpage_target)
        self.subpage_response.elapsed = 12.12

        self.logger = logging.getLogger('deadseeker.loggingresponsehandler')

    def test_info_logs_when_success(self):
        self.resp.status = 200
        with patch.object(self.logger, 'error') as error_mock,\
                patch.object(self.logger, 'info') as info_mock:
            self.testobj.handle_response(self.resp)
            expected = '200 - http://testing.test.com/ - 1234.12 ms'
            info_mock.assert_called_with(expected)
            error_mock.assert_not_called()

    def test_error_logs_when_responseerror(self):
        self.resp.status = 400
        self.resp.error = ClientError()
        with patch.object(self.logger, 'error') as error_mock,\
                patch.object(self.logger, 'info') as info_mock,\
                patch.object(self.logger, 'debug') as debug_mock:
            self.testobj.handle_response(self.resp)
            expected_error = '::error ::ClientError: 400' +\
                ' - http://testing.test.com/'
            expected_debug = 'The following exception occured'
            error_mock.assert_called_with(expected_error)
            debug_mock.assert_called_with(expected_debug,
                                          exc_info=self.resp.error)
            info_mock.assert_not_called()

    def test_error_logs_when_responseerror_including_navigationpath(self):
        self.subpage_response.status = 400
        self.subpage_response.error = ClientError()
        with patch.object(self.logger, 'error') as error_mock,\
                patch.object(self.logger, 'info') as info_mock,\
                patch.object(self.logger, 'debug') as debug_mock:
            self.testobj.handle_response(self.subpage_response)
            expected_error = '::error ::ClientError: 400' +\
                ' - http://subpage.testing.test.com/page1' +\
                ' found by navigating through: http://testing.test.com/ ' +\
                '-> http://subpage.testing.test.com/'
            expected_debug = 'The following exception occured'
            error_mock.assert_called_with(expected_error)
            debug_mock.assert_called_with(expected_debug,
                                          exc_info=self.subpage_response.error)
            info_mock.assert_not_called()

    def test_error_logs_when_no_status_error(self):
        self.resp.error = ClientError('test error')
        with patch.object(self.logger, 'error') as error_mock,\
                patch.object(self.logger, 'info') as info_mock,\
                patch.object(self.logger, 'debug') as debug_mock:
            self.testobj.handle_response(self.resp)
            expected = '::error ::ClientError: test error' +\
                ' - http://testing.test.com/'
            expected_debug = 'The following exception occured'
            error_mock.assert_called_with(expected)
            debug_mock.assert_called_with(expected_debug,
                                          exc_info=self.resp.error)
            info_mock.assert_not_called()


if __name__ == '__main__':
    unittest.main()
