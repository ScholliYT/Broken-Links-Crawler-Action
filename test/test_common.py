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

    def test_default_connect_limit_per_host(self):
        self.assertEqual(
            self.testobj.connect_limit_per_host, 0)

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


if __name__ == '__main__':
    unittest.main()
