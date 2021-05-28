from deadseeker.linkparser import DefaultLinkParser, DefaultLinkParserFactory
from deadseeker.linkacceptor import LinkAcceptor
from deadseeker.common import SeekerConfig, UrlFetchResponse, UrlTarget
import unittest
from unittest.mock import Mock
import os

TESTFILE_LOC = os.path.join(os.path.dirname(__file__), "test_linkparser.html")


class TestDefaultLinkParserFactory(unittest.TestCase):

    def setUp(self):
        self.config = Mock(specf=SeekerConfig)
        self.linkacceptor = Mock(spec=LinkAcceptor)
        self.testobj = DefaultLinkParserFactory()

    def test_returns_defaultlinkparser(self):
        result = self.testobj.get_link_parser(self.config, self.linkacceptor)
        self.assertTrue(isinstance(result, DefaultLinkParser))


TEST_SEARCH_ATTRS = set(['href', 'src', 'data-src'])


class TestDefaultLinkParser(unittest.TestCase):

    def setUp(self):
        self.resp = Mock(spec=UrlFetchResponse)
        self.resp.urltarget = Mock(spec=UrlTarget)
        self.resp.urltarget.url = 'https://mysite.com/'
        with open(TESTFILE_LOC) as f:
            self.resp.html = f.read()
        self.config = Mock(spec=SeekerConfig)
        self.config.resolvebeforefilter = False
        self.config.search_attrs = TEST_SEARCH_ATTRS
        self.linkacceptor = Mock(spec=LinkAcceptor)
        self.linkacceptor.accepts.return_value = True
        self.testobj: DefaultLinkParser = \
            DefaultLinkParser(self.config, self.linkacceptor)

    def test_find_links_all_true(self):
        actuallinks = self.testobj.parse(self.resp)
        expectedlinks = [
            '/link-manifest-href.webmanifest',
            '/link-apple-touch-icon-href.png',
            '/link-stylesheet-href.css',
            '/script-src.js',
            'script-src-relative.js',
            '/a-href.html',
            '/img-src.jpeg',
            '/img-data-src.png',
            '//www.google-analytics.com/analytics.js'
        ]
        self.assertEqual(expectedlinks, actuallinks)

    def test_find_links_all_false(self):
        self.linkacceptor.accepts.return_value = False
        actuallinks = self.testobj.parse(self.resp)
        self.assertEqual([], actuallinks)

    def test_find_links_picky(self):
        self.linkacceptor.accepts = lambda link: link.endswith('.js')
        actuallinks = self.testobj.parse(self.resp)
        expectedlinks = [
            '/script-src.js',
            'script-src-relative.js',
            '//www.google-analytics.com/analytics.js'
        ]
        self.assertEqual(expectedlinks, actuallinks)

    def test_find_links_search_attrs(self):
        self.config.search_attrs = set(['href'])
        actuallinks = self.testobj.parse(self.resp)
        expectedlinks = [
            '/link-manifest-href.webmanifest',
            '/link-apple-touch-icon-href.png',
            '/link-stylesheet-href.css',
            '/a-href.html'
        ]
        self.assertEqual(expectedlinks, actuallinks)

    def test_find_links_all_true_resolve_before_filter(self):
        self.config.resolvebeforefilter = True
        actuallinks = self.testobj.parse(self.resp)
        expectedlinks = [
            'https://mysite.com/link-manifest-href.webmanifest',
            'https://mysite.com/link-apple-touch-icon-href.png',
            'https://mysite.com/link-stylesheet-href.css',
            'https://mysite.com/script-src.js',
            'https://mysite.com/script-src-relative.js',
            'https://mysite.com/a-href.html',
            'https://mysite.com/img-src.jpeg',
            'https://mysite.com/img-data-src.png',
            'https://www.google-analytics.com/analytics.js'
        ]
        self.assertEqual(expectedlinks, actuallinks)

    def test_everything_fine_if_no_html(self):
        self.resp.html = None
        actuallinks = self.testobj.parse(self.resp)
        self.assertEqual([], actuallinks)


if __name__ == '__main__':
    unittest.main()
