import unittest
from aiounittest import AsyncTestCase
from asyncio import TimeoutError
from aiohttp import (
    ClientResponseError,
    ClientError
)
from aiohttp_retry import RetryClient
from unittest.mock import Mock, patch
from aioresponses import aioresponses
from deadseeker.common import SeekerConfig
from deadseeker.timer import Timer
from deadseeker.responsefetcher import (
    DefaultResponseFetcherFactory,
    HeadThenGetIfHtmlResponseFetcher,
    AlwaysGetIfOnSiteResponseFetcher
)


class TestDefaultResponseFetcherFactory(unittest.TestCase):

    def setUp(self):
        self.testobj = DefaultResponseFetcherFactory()
        self.config = SeekerConfig()

    def test_head_first_is_default(self):
        result = self.testobj.get_response_fetcher(self.config)
        self.assertTrue(isinstance(result, HeadThenGetIfHtmlResponseFetcher))

    def test_always_get_is_returned_when_enabled(self):
        self.config.alwaysgetonsite = True
        result = self.testobj.get_response_fetcher(self.config)
        self.assertTrue(isinstance(result, AlwaysGetIfOnSiteResponseFetcher))


TEST_HOME_URL = 'http://testing.test.com/'
TEST_OTHER_URL = 'http://testing.test2.com/'
TEST_BODY = 'bananas'
TYPE_HTML = 'text/html'
TYPE_JSON = 'application/json'
TEST_EXPECTED_ELAPSED = 4000.0


class TestHeadThenGetIfHtmlResponseFetcher(AsyncTestCase):

    def setUp(self):
        self.testobj = HeadThenGetIfHtmlResponseFetcher()
        self.urltarget = Mock()
        self.urltarget.home = TEST_HOME_URL
        self.timer_stop_patch = patch.object(Timer, 'stop')
        self.timer_stop = self.timer_stop_patch.start()
        self.timer_stop.return_value = 4.0

    def tearDown(self):
        self.timer_stop_patch.stop()

    @aioresponses()
    async def test_if_same_site_and_html(self,  m):
        self._prep_request(m, TEST_HOME_URL, content_type=TYPE_HTML)
        async with RetryClient() as session:
            response = await self.testobj.fetch_response(
                    session, self.urltarget)
            self.assertIs(self.urltarget, response.urltarget)
            self.assertEqual(200, response.status)
            self.assertEqual(TEST_BODY, response.html)
            self.assertIsNone(response.error)
            self.assertEqual(TEST_EXPECTED_ELAPSED, response.elapsed)

    # Test for ScholliYT/Broken-Links-Crawler-Action#8
    @aioresponses()
    async def test_if_same_site_and_html_head_not_supported(self,  m):
        exception = ClientResponseError(None, None, status=405)
        self._prep_request(
            m,
            TEST_HOME_URL,
            headexception=exception,
            content_type=TYPE_HTML)
        async with RetryClient() as session:
            response = await self.testobj.fetch_response(
                    session, self.urltarget)
            self.assertIs(self.urltarget, response.urltarget)
            self.assertEqual(200, response.status)
            self.assertEqual(TEST_BODY, response.html)
            self.assertIsNone(response.error)
            self.assertEqual(TEST_EXPECTED_ELAPSED, response.elapsed)

    # Test for ScholliYT/Broken-Links-Crawler-Action#8
    @aioresponses()
    async def test_if_same_site_and_not_html_head_not_supported(self,  m):
        exception = ClientResponseError(None, None, status=405)
        self._prep_request(
            m,
            TEST_HOME_URL,
            headexception=exception,
            content_type=TYPE_JSON)
        async with RetryClient() as session:
            response = await self.testobj.fetch_response(
                    session, self.urltarget)
            self.assertIs(self.urltarget, response.urltarget)
            self.assertEqual(200, response.status)
            self.assertIsNone(response.html)
            self.assertIsNone(response.error)
            self.assertEqual(TEST_EXPECTED_ELAPSED, response.elapsed)

    # Test for ScholliYT/Broken-Links-Crawler-Action#8
    @aioresponses()
    async def test_if_other_site_and_html_head_not_supported(self,  m):
        exception = ClientResponseError(None, None, status=405)
        self._prep_request(
            m,
            TEST_OTHER_URL,
            headexception=exception,
            content_type=TYPE_HTML)
        async with RetryClient() as session:
            response = await self.testobj.fetch_response(
                    session, self.urltarget)
            self.assertIs(self.urltarget, response.urltarget)
            self.assertEqual(200, response.status)
            self.assertIsNone(response.html)
            self.assertIsNone(response.error)
            self.assertEqual(TEST_EXPECTED_ELAPSED, response.elapsed)

    @aioresponses()
    async def test_if_other_site_and_html(
            self, m):
        self._prep_request(m, TEST_OTHER_URL, content_type=TYPE_HTML)
        async with RetryClient() as session:
            response = await self.testobj.fetch_response(
                    session, self.urltarget)
            self.assertIs(self.urltarget, response.urltarget)
            self.assertEqual(200, response.status)
            self.assertIsNone(response.html)
            self.assertIsNone(response.error)
            self.assertEqual(TEST_EXPECTED_ELAPSED, response.elapsed)

    @aioresponses()
    async def test_if_same_site_and_not_html(
            self,  m):
        self._prep_request(m, TEST_HOME_URL, content_type=TYPE_JSON)
        async with RetryClient() as session:
            response = await self.testobj.fetch_response(
                    session, self.urltarget)
            self.assertIs(self.urltarget, response.urltarget)
            self.assertEqual(200, response.status)
            self.assertIsNone(response.html)
            self.assertIsNone(response.error)
            self.assertEqual(TEST_EXPECTED_ELAPSED, response.elapsed)

    @aioresponses()
    async def test_if_other_site_and_not_html(
            self, m):
        self._prep_request(m, TEST_OTHER_URL, content_type=TYPE_JSON)
        async with RetryClient() as session:
            response = await self.testobj.fetch_response(
                    session, self.urltarget)
            self.assertIs(self.urltarget, response.urltarget)
            self.assertEqual(200, response.status)
            self.assertIsNone(response.html)
            self.assertIsNone(response.error)
            self.assertEqual(TEST_EXPECTED_ELAPSED, response.elapsed)

    @aioresponses()
    async def test_if_response_error(
            self, m):
        exception = ClientResponseError(None, None, status=404)
        self._prep_request(m, TEST_HOME_URL, headexception=exception)
        async with RetryClient() as session:
            response = await self.testobj.fetch_response(
                    session, self.urltarget)
            self.assertIs(self.urltarget, response.urltarget)
            self.assertEqual(404, response.status)
            self.assertIsNone(response.html)
            self.assertIs(exception, response.error)
            self.assertEqual(TEST_EXPECTED_ELAPSED, response.elapsed)

    @aioresponses()
    async def test_if_connection_error(
            self, m):
        exception = ClientError()
        self._prep_request(m, TEST_HOME_URL, headexception=exception)
        async with RetryClient() as session:
            response = await self.testobj.fetch_response(
                    session, self.urltarget)
            self.assertIs(self.urltarget, response.urltarget)
            self.assertEqual(0, response.status)
            self.assertIsNone(response.html)
            self.assertIs(exception, response.error)
            self.assertEqual(TEST_EXPECTED_ELAPSED, response.elapsed)

    @aioresponses()
    async def test_if_timeout_error(
            self, m):
        exception = TimeoutError()
        self._prep_request(m, TEST_HOME_URL, headexception=exception)
        async with RetryClient() as session:
            response = await self.testobj.fetch_response(
                    session, self.urltarget)
            self.assertIs(self.urltarget, response.urltarget)
            self.assertEqual(0, response.status)
            self.assertIsNone(response.html)
            self.assertIs(exception, response.error)
            self.assertEqual(TEST_EXPECTED_ELAPSED, response.elapsed)

    def _prep_request(
            self,
            mockresponses,
            url: str,
            content_type: str = None,
            headexception: Exception = None):
        self.urltarget.url = url
        mockresponses.head(
            url,
            content_type=content_type,
            exception=headexception
        )
        mockresponses.get(
            url,
            content_type=content_type,
            body=TEST_BODY
        )


class TestAlwaysGetIfOnSiteResponseFetcher(AsyncTestCase):

    def setUp(self):
        self.testobj = AlwaysGetIfOnSiteResponseFetcher()
        self.urltarget = Mock()
        self.urltarget.home = TEST_HOME_URL
        self.timer_stop_patch = patch.object(Timer, 'stop')
        self.timer_stop = self.timer_stop_patch.start()
        self.timer_stop.return_value = 4.0

    def tearDown(self):
        self.timer_stop_patch.stop()

    @aioresponses()
    async def test_if_same_site_and_html(self,  m):
        self._prep_request(m, TEST_HOME_URL, content_type=TYPE_HTML)
        async with RetryClient() as session:
            response = await self.testobj.fetch_response(
                    session, self.urltarget)
            self.assertIs(self.urltarget, response.urltarget)
            self.assertEqual(200, response.status)
            self.assertEqual(TEST_BODY, response.html)
            self.assertIsNone(response.error)
            self.assertEqual(TEST_EXPECTED_ELAPSED, response.elapsed)

    @aioresponses()
    async def test_if_other_site_and_html(
            self, m):
        self._prep_request(
            m, TEST_OTHER_URL, method='HEAD', content_type=TYPE_HTML)
        async with RetryClient() as session:
            response = await self.testobj.fetch_response(
                    session, self.urltarget)
            self.assertIs(self.urltarget, response.urltarget)
            self.assertEqual(200, response.status)
            self.assertIsNone(response.html)
            self.assertIsNone(response.error)
            self.assertEqual(TEST_EXPECTED_ELAPSED, response.elapsed)

    @aioresponses()
    async def test_if_same_site_and_not_html(
            self,  m):
        self._prep_request(m, TEST_HOME_URL, content_type=TYPE_JSON)
        async with RetryClient() as session:
            response = await self.testobj.fetch_response(
                    session, self.urltarget)
            self.assertIs(self.urltarget, response.urltarget)
            self.assertEqual(200, response.status)
            self.assertIsNone(response.html)
            self.assertIsNone(response.error)
            self.assertEqual(TEST_EXPECTED_ELAPSED, response.elapsed)

    @aioresponses()
    async def test_if_other_site_and_not_html(
            self, m):
        self._prep_request(
            m, TEST_OTHER_URL, method='HEAD', content_type=TYPE_JSON)
        async with RetryClient() as session:
            response = await self.testobj.fetch_response(
                    session, self.urltarget)
            self.assertIs(self.urltarget, response.urltarget)
            self.assertEqual(200, response.status)
            self.assertIsNone(response.html)
            self.assertIsNone(response.error)
            self.assertEqual(TEST_EXPECTED_ELAPSED, response.elapsed)

    @aioresponses()
    async def test_if_response_error(
            self, m):
        exception = ClientResponseError(None, None, status=404)
        self._prep_request(m, TEST_HOME_URL, exception=exception)
        async with RetryClient() as session:
            response = await self.testobj.fetch_response(
                    session, self.urltarget)
            self.assertIs(self.urltarget, response.urltarget)
            self.assertEqual(404, response.status)
            self.assertIsNone(response.html)
            self.assertIs(exception, response.error)
            self.assertEqual(TEST_EXPECTED_ELAPSED, response.elapsed)

    @aioresponses()
    async def test_if_connection_error(
            self, m):
        exception = ClientError()
        self._prep_request(m, TEST_HOME_URL, exception=exception)
        async with RetryClient() as session:
            response = await self.testobj.fetch_response(
                    session, self.urltarget)
            self.assertIs(self.urltarget, response.urltarget)
            self.assertEqual(0, response.status)
            self.assertIsNone(response.html)
            self.assertIs(exception, response.error)
            self.assertEqual(TEST_EXPECTED_ELAPSED, response.elapsed)

    @aioresponses()
    async def test_if_timeout_error(
            self, m):
        exception = TimeoutError()
        self._prep_request(m, TEST_HOME_URL, exception=exception)
        async with RetryClient() as session:
            response = await self.testobj.fetch_response(
                    session, self.urltarget)
            self.assertIs(self.urltarget, response.urltarget)
            self.assertEqual(0, response.status)
            self.assertIsNone(response.html)
            self.assertIs(exception, response.error)
            self.assertEqual(TEST_EXPECTED_ELAPSED, response.elapsed)

    def _prep_request(
            self,
            mockresponses,
            url: str,
            method: str = 'GET',
            **kwargs):
        self.urltarget.url = url
        mockresponses.add(
            url,
            method,
            body=TEST_BODY,
            **kwargs
        )


if __name__ == '__main__':
    unittest.main()
