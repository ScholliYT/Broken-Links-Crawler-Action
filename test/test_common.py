import unittest
from unittest.mock import Mock
from deadseeker.common import (
    SeekerConfig,
    UrlFetchResponse,
    UrlTarget
)


class TestSeekerConfig(unittest.TestCase):

    def setUp(self):
        self.testobj = SeekerConfig()

    def test_default_agent(self):
        self.assertEqual(
            self.testobj.agent,
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64)' +
            ' AppleWebKit/537.36 (KHTML, like Gecko)' +
            ' Chrome/60.0.3112.113 Safari/537.36')

    def test_default_max_tries(self):
        self.assertEqual(
            self.testobj.max_tries, 4)

    def test_default_max_time(self):
        self.assertEqual(
            self.testobj.max_time, 30)

    def test_default_max_depth(self):
        self.assertEqual(
            self.testobj.max_depth, -1)

    def test_default_search_attrs(self):
        self.assertEqual(
            self.testobj.search_attrs,
            set(['href', 'src'])
        )

    def test_default_resolvebeforefilter(self):
        self.assertEqual(self.testobj.resolvebeforefilter, False)

    def test_default_connect_limit_per_host(self):
        self.assertEqual(
            self.testobj.connect_limit_per_host, 10)

    def test_default_timeout(self):
        self.assertEqual(
            self.testobj.timeout, 60)

    def test_default_include_prefix(self):
        self.assertEqual(
            self.testobj.includeprefix, [])

    def test_default_exclude_prefix(self):
        self.assertEqual(
            self.testobj.excludeprefix, ['mailto:', 'tel:'])

    def test_default_include_suffix(self):
        self.assertEqual(
            self.testobj.includesuffix, [])

    def test_default_exclude_suffix(self):
        self.assertEqual(
            self.testobj.excludesuffix, [])

    def test_default_include_contained(self):
        self.assertEqual(
            self.testobj.includecontained, [])

    def test_default_exclude_contained(self):
        self.assertEqual(
            self.testobj.excludecontained, [])

    def test_default_alwaysgetonsite(self):
        self.assertEqual(
            self.testobj.alwaysgetonsite, False)


class TestUrlFetchResponse(unittest.TestCase):

    def setUp(self):
        self.urltarget = Mock(spec=UrlTarget)
        self.testobj = UrlFetchResponse(self.urltarget)

    def test_urltarget(self):
        self.assertIs(self.testobj.urltarget, self.urltarget)

    def test_html(self):
        self.assertIsNone(self.testobj.html)


class TestUrlTarget(unittest.TestCase):

    def setUp(self):
        self.testobj = UrlTarget("https://example.com", "https://example.com", 5)

    def test_child_has_parent(self):
        child = self.testobj.child("https://test.com")
        self.assertEqual(self.testobj.home, child.home)
        self.assertEqual(self.testobj.depth - 1, child.depth)
        self.assertIsNone(self.testobj.parent)
        self.assertEqual(self.testobj, child.parent)
        self.assertEqual("https://test.com", child.url)

    def test_parent_urls_generates_only_urls_for_parents(self):
        child1 = self.testobj.child("https://example.com/1")
        child2 = child1.child("https://example.com/2")

        output = child2.parent_urls()
        expected_urls = [
            "https://example.com",
            "https://example.com/1"
        ]
        self.assertEqual(expected_urls, output)


if __name__ == '__main__':
    unittest.main()
