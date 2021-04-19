import unittest
from unittest.mock import Mock, patch
from typing import List
from .asyncmock import AsyncContextManagerMock
from deadseeker.common import (
    SeekerConfig,
    UrlFetchResponseHandler,
    UrlFetchResponse,
    UrlTarget
)
from deadseeker.deadseeker import DeadSeeker
from deadseeker.clientsession import ClientSessionFactory
from deadseeker.responsefetcher import ResponseFetcherFactory, ResponseFetcher
from deadseeker.linkacceptor import LinkAcceptorFactory, LinkAcceptor
from deadseeker.linkparser import LinkParserFactory, LinkParser
from deadseeker.timer import Timer
from aiohttp import ClientSession, ClientResponseError, ClientError


# Preparing test data to represent two web sites, test1.com and test2.com
# test1 will only have links to itself, but will us various types of links
# (i.e. absolute and relative)
# test2 will have fewer pages, but one of the pages will link to site1
# to experiment
TEST1_URL_HOME = 'http://www.test1.com/'
TEST1_HTML_HOME = 'test1_home'
TEST1_URL_PAGE1 = 'http://www.test1.com/page1.html'
TEST1_HTML_PAGE1 = 'test1_page1'
TEST1_URL_PAGE2 = 'http://www.test1.com/page2.html'
TEST1_HTML_PAGE2 = 'test1_page2'
TEST1_URL_PAGE3 = 'http://www.test1.com/page3.html'
TEST1_HTML_PAGE3 = 'test1_page3'
TEST1_URL_PAGE4 = 'http://www.test1.com/page4.html'
TEST1_HTML_PAGE4 = 'test1_page4'
TEST1_URL_PAGE5 = 'http://www.test1.com/page5.html'
TEST1_HTML_PAGE5 = 'test1_page5'
TEST1_URL_FAVICON = 'http://www.test1.com/favicon.ico'
TEST1_URL_LOGO = 'http://www.test1.com/logo.png'

TEST2_URL_HOME = 'http://www.test2.com/'
TEST2_HTML_HOME = 'tes2_home'
TEST2_URL_PAGE1 = 'http://www.test2.com/page1.html'
TEST2_HTML_PAGE1 = 'tes2_page1'
TEST2_URL_PAGE2 = 'http://www.test2.com/page2.html'
TEST2_HTML_PAGE2 = 'tes2_page2'
TEST2_URL_PAGE3 = 'http://www.test2.com/page3.html'
TEST2_HTML_PAGE3 = 'tes2_page3'
TEST2_URL_FAVICON = 'http://www.test2.com/favicon.ico'
TEST2_URL_LOGO = 'http://www.test2.com/logo.png'

ERROR_404 = ClientResponseError(None, None, status=404)
ERROR_CONNECTION = ClientError()


# This class assists with mocking fetch responses,
# can be reused multiple times to generate different
# response instances, although the code should only
# ever fetch a given url once
class MockedResponseCreator:
    def __init__(
            self, html: str = None,
            error: Exception = None):
        self.html = html
        self.error = error

    def make_response(self, urltarget: UrlTarget):
        result = Mock(spec=UrlFetchResponse)
        result.urltarget = urltarget
        result.error = self.error
        self.status = None
        if isinstance(self.error, ClientResponseError):
            result.status = self.error.status
        elif not isinstance(self.error, ClientError):
            result.status = 200
        result.html = None
        if urltarget.home in urltarget.url:
            result.html = self.html
        return result


TEST_RESPONSES_BY_URL = {
    TEST1_URL_HOME: MockedResponseCreator(html=TEST1_HTML_HOME),
    TEST1_URL_PAGE1:
        MockedResponseCreator(html=TEST1_HTML_PAGE1),
    TEST1_URL_PAGE2:
        MockedResponseCreator(html=TEST1_HTML_PAGE2),
    TEST1_URL_PAGE3:
        MockedResponseCreator(html=TEST1_HTML_PAGE3),
    TEST1_URL_PAGE4:
        MockedResponseCreator(html=TEST1_HTML_PAGE4),
    TEST1_URL_PAGE5:
        MockedResponseCreator(html=TEST1_HTML_PAGE5),
    TEST1_URL_FAVICON: MockedResponseCreator(),
    TEST1_URL_LOGO: MockedResponseCreator(),
    TEST2_URL_HOME: MockedResponseCreator(html=TEST2_HTML_HOME),
    TEST2_URL_PAGE1:
        MockedResponseCreator(html=TEST2_HTML_PAGE1),
    TEST2_URL_PAGE2:
        MockedResponseCreator(html=TEST2_HTML_PAGE2),
    TEST2_URL_PAGE3:
        MockedResponseCreator(html=TEST2_HTML_PAGE3),
    TEST2_URL_FAVICON: MockedResponseCreator(error=ERROR_CONNECTION),
    TEST2_URL_LOGO: MockedResponseCreator(error=ERROR_404)
}

TEST_PARSE_RESULTS_BY_HTML = {
    TEST1_HTML_HOME: [
        TEST1_URL_FAVICON,
        TEST1_URL_LOGO,
        TEST1_URL_PAGE1,
    ],
    TEST1_HTML_PAGE1: [
        TEST1_URL_FAVICON,
        TEST1_URL_LOGO,
        '/page2.html',  # relative link, type 1
    ],
    TEST1_HTML_PAGE2: [
        TEST1_URL_FAVICON,
        TEST1_URL_LOGO,
        'page3.html',  # relative link, type 2
        TEST1_URL_PAGE4
    ],
    TEST1_HTML_PAGE3: [
        TEST1_URL_FAVICON,
        TEST1_URL_LOGO,
        TEST1_URL_HOME,
        TEST1_URL_PAGE1,
    ],
    TEST1_HTML_PAGE4: [
        TEST1_URL_FAVICON,
        TEST1_URL_LOGO,
        TEST1_URL_PAGE5,
    ],
    TEST1_HTML_PAGE5: [
        TEST1_URL_FAVICON,
        TEST1_URL_LOGO,
        TEST1_URL_HOME,
    ],
    TEST2_HTML_HOME: [
        TEST2_URL_FAVICON,
        TEST2_URL_LOGO,
        TEST2_URL_PAGE1,
    ],
    TEST2_HTML_PAGE1: [
        TEST2_URL_FAVICON,
        TEST2_URL_LOGO,
        TEST2_URL_PAGE2,
    ],
    TEST2_HTML_PAGE2: [
        TEST2_URL_FAVICON,
        TEST2_URL_LOGO,
        TEST2_URL_PAGE3
    ],
    TEST2_HTML_PAGE3: [
        TEST2_URL_FAVICON,
        TEST2_URL_LOGO,
        TEST2_URL_HOME,
        TEST1_URL_HOME  # external link to test site 1
    ],
}


def get_urls(urltargets: List[UrlTarget]):
    return list(map(lambda x: x.urltarget.url, urltargets))


class TestDeadSeeker(unittest.TestCase):

    def setUp(self):
        self.config = Mock(spec=SeekerConfig)
        self.config.max_depth = -1
        self.testobj = DeadSeeker(self.config)
        self.testobj.clientsession = Mock(spec=ClientSessionFactory)
        self.session = AsyncContextManagerMock()
        self.testobj.clientsession.get_client_session.return_value = \
            self.session
        self.testobj.responsefetcherfactory = Mock(spec=ResponseFetcherFactory)
        self.responsefetcher = Mock(spec=ResponseFetcher)
        self.testobj.responsefetcherfactory\
            .get_response_fetcher.return_value = self.responsefetcher

        def fetch_response_mock(session: ClientSession, urltarget: UrlTarget):
            response_creator = TEST_RESPONSES_BY_URL.get(urltarget.url)
            self.assertIsNotNone(
                response_creator,
                f'Unexpected request for url "{urltarget.url}"')
            return response_creator.make_response(urltarget)

        self.responsefetcher.fetch_response.side_effect = fetch_response_mock
        self.testobj.linkacceptorfactory = Mock(spec=LinkAcceptorFactory)
        self.linkacceptor = Mock(spec=LinkAcceptor)
        self.testobj.linkacceptorfactory.get_link_acceptor.return_value = \
            self.linkacceptor
        self.testobj.linkparserfactory = Mock(spec=LinkParserFactory)

        def parse_mock(html: str):
            links = TEST_PARSE_RESULTS_BY_HTML.get(html)
            self.assertIsNotNone(
                html,
                f'unexpected html provided: {html}'
            )
            return links

        linkparser = Mock(spec=LinkParser)
        linkparser.parse.side_effect = parse_mock

        self.testobj.linkparserfactory.get_link_parser.return_value = \
            linkparser
        self.responsehandler = Mock(spec=UrlFetchResponseHandler)
        self.timer_stop_patch = patch.object(Timer, 'stop')
        self.timer_stop = self.timer_stop_patch.start()
        self.timer_stop.return_value = 4.0

    def tearDown(self):
        self.timer_stop_patch.stop()

    def test_site1_is_fully_crawled(self):
        results = self.testobj.seek(TEST1_URL_HOME)
        successes = get_urls(results.successes)
        self.assertEqual(successes, [
            TEST1_URL_HOME,
            TEST1_URL_FAVICON,
            TEST1_URL_LOGO,
            TEST1_URL_PAGE1,
            TEST1_URL_PAGE2,
            TEST1_URL_PAGE3,
            TEST1_URL_PAGE4,
            TEST1_URL_PAGE5
        ])
        failures = get_urls(results.failures)
        self.assertEqual(failures, [])
        self.assertEqual(4000.0, results.elapsed)

    def test_site2_crawls_all_if_2_but_only_home_of_1(self):
        results = self.testobj.seek(TEST2_URL_HOME)
        successes = get_urls(results.successes)
        self.assertEqual(successes, [
            TEST2_URL_HOME,
            TEST2_URL_PAGE1,
            TEST2_URL_PAGE2,
            TEST2_URL_PAGE3,
            TEST1_URL_HOME
        ])
        failures = get_urls(results.failures)
        self.assertEqual(failures, [
            TEST2_URL_FAVICON,
            TEST2_URL_LOGO,
        ])
        self.assertEqual(4000.0, results.elapsed)

    def test_site1_and_site2_crawls_all(self):
        results = self.testobj.seek([TEST1_URL_HOME, TEST2_URL_HOME])
        successes = get_urls(results.successes)
        self.assertEqual(successes, [
            TEST1_URL_HOME,
            TEST2_URL_HOME,
            TEST1_URL_FAVICON,
            TEST1_URL_LOGO,
            TEST1_URL_PAGE1,
            TEST2_URL_PAGE1,
            TEST1_URL_PAGE2,
            TEST2_URL_PAGE2,
            TEST1_URL_PAGE3,
            TEST1_URL_PAGE4,
            TEST2_URL_PAGE3,
            TEST1_URL_PAGE5
        ])
        failures = get_urls(results.failures)
        self.assertEqual(failures, [
            TEST2_URL_FAVICON,
            TEST2_URL_LOGO,
        ])
        self.assertEqual(4000.0, results.elapsed)

    def test_site1_is_partially_crawled_with_max_depth(self):
        self.config.max_depth = 2
        results = self.testobj.seek(TEST1_URL_HOME)
        successes = get_urls(results.successes)
        self.assertEqual(successes, [
            TEST1_URL_HOME,
            TEST1_URL_FAVICON,
            TEST1_URL_LOGO,
            TEST1_URL_PAGE1,
            TEST1_URL_PAGE2
        ])
        failures = get_urls(results.failures)
        self.assertEqual(failures, [])
        self.assertEqual(4000.0, results.elapsed)

    def test_response_handler_is_Called(self):
        results = self.testobj.seek(
            [TEST1_URL_HOME, TEST2_URL_HOME], self.responsehandler)
        for result in results.successes:
            self.responsehandler.handle_response.assert_any_call(result)
        for result in results.failures:
            self.responsehandler.handle_response.assert_any_call(result)


if __name__ == '__main__':
    unittest.main()
