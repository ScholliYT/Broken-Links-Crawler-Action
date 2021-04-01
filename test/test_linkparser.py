from deadseeker.linkparser import LinkParser
import unittest
from unittest.mock import MagicMock
import os

TESTFILE_LOC = os.path.join(os.path.dirname(__file__), "test.html")


class TestLinkParser(unittest.TestCase):

    def setUp(self):
        with open(TESTFILE_LOC) as f:
            self.html = f.read()
        self.linkacceptor = MagicMock()
        self.testobj: LinkParser = LinkParser(self.linkacceptor)

    def test_find_links_all_true(self):
        self.linkacceptor.accepts.return_value = True
        self.testobj.feed(self.html)
        actuallinks = self.testobj.links
        expectedlinks = [
            '/this-is-a-manifest-link.webmanifest',
            '/this-is-an-icon-link.png',
            '/this-is-a-stylesheet-link.css',
            '/this-is-a-javascript-link.js',
            'this-is-a-relative-javascript-link.js',
            '/this-is-a-link.html',
            '/this-is-a-link.jpeg',
            'https://www.google-analytics.com/analytics.js'
        ]
        self.assertEqual(expectedlinks, actuallinks)

    def test_find_links_all_false(self):
        self.linkacceptor.accepts.return_value = False
        self.testobj.feed(self.html)
        actuallinks = self.testobj.links
        self.assertEqual([], actuallinks)

    def test_find_links_picky(self):
        self.linkacceptor.accepts = lambda link: link.endswith('.js')
        self.testobj.feed(self.html)
        actuallinks = self.testobj.links
        expectedlinks = [
            '/this-is-a-javascript-link.js',
            'this-is-a-relative-javascript-link.js',
            'https://www.google-analytics.com/analytics.js'
        ]
        self.assertEqual(expectedlinks, actuallinks)


if __name__ == '__main__':
    unittest.main()
