from deadseeker.linkparser import DefaultLinkParser, DefaultLinkParserFactory
from deadseeker.linkacceptor import LinkAcceptor
from deadseeker.common import SeekerConfig
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
        with open(TESTFILE_LOC) as f:
            self.html = f.read()
        self.config = Mock(specf=SeekerConfig)
        self.linkacceptor = Mock(spec=LinkAcceptor)
        self.testobj: DefaultLinkParser = \
            DefaultLinkParser(self.config, self.linkacceptor)

    def test_find_links_all_true(self):
        self.config.search_attrs = TEST_SEARCH_ATTRS
        self.linkacceptor.accepts.return_value = True
        actuallinks = self.testobj.parse(self.html)
        expectedlinks = [
            '/this-is-a-manifest-link.webmanifest',
            '/this-is-an-icon-link.png',
            '/this-is-a-stylesheet-link.css',
            '/this-is-a-javascript-link.js',
            'this-is-a-relative-javascript-link.js',
            '/this-is-a-link.html',
            '/this-is-a-link.jpeg',
            '/this-is-lazy-loaded.png',
            'https://www.google-analytics.com/analytics.js'
        ]
        self.assertEqual(expectedlinks, actuallinks)

    def test_find_links_all_false(self):
        self.config.search_attrs = TEST_SEARCH_ATTRS
        self.linkacceptor.accepts.return_value = False
        actuallinks = self.testobj.parse(self.html)
        self.assertEqual([], actuallinks)

    def test_find_links_picky(self):
        self.config.search_attrs = TEST_SEARCH_ATTRS
        self.linkacceptor.accepts = lambda link: link.endswith('.js')
        actuallinks = self.testobj.parse(self.html)
        expectedlinks = [
            '/this-is-a-javascript-link.js',
            'this-is-a-relative-javascript-link.js',
            'https://www.google-analytics.com/analytics.js'
        ]
        self.assertEqual(expectedlinks, actuallinks)


if __name__ == '__main__':
    unittest.main()
