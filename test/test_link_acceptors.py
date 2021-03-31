import unittest
from deadseeker.link_acceptors import LinkAcceptorBuilder

STRING_1 = 'bananas'
STRING_1_PREFIX = STRING_1[0:3]  # ban
STRING_1_SUFFIX = STRING_1[len(STRING_1)-3:]  # nas
STRING_1_INNER = STRING_1[2:5]  # nan
STRING_2 = 'apples'


class TestLinkAcceptor(unittest.TestCase):

    def setUp(self):
        self.builder = LinkAcceptorBuilder()

    def test_defaultAcceptsAll(self):
        self.assertAccepted(STRING_1)
        self.assertAccepted(STRING_2)

    def test_include_prefix(self):
        self.builder.addIncludePrefix(STRING_1_PREFIX)
        self.assertAccepted(STRING_1)
        self.assertNotAccepted(STRING_2)

    def test_exclude_prefix(self):
        self.builder.addExcludePrefix(STRING_1_PREFIX)
        self.assertNotAccepted(STRING_1)
        self.assertAccepted(STRING_2)

    def test_include_suffix(self):
        self.builder.addIncludeSuffix(STRING_1_SUFFIX)
        self.assertAccepted(STRING_1)
        self.assertNotAccepted(STRING_2)

    def test_exclude_suffix(self):
        self.builder.addExcludeSuffix(STRING_1_SUFFIX)
        self.assertNotAccepted(STRING_1)
        self.assertAccepted(STRING_2)

    def test_include_contained(self):
        self.builder.addIncludeContained(STRING_1_INNER)
        self.assertAccepted(STRING_1)
        self.assertNotAccepted(STRING_2)

    def test_exclude_contained(self):
        self.builder.addExcludeContained(STRING_1_INNER)
        self.assertNotAccepted(STRING_1)
        self.assertAccepted(STRING_2)

    def assertAccepted(self, value: str) -> None:
        self.assertTrue(self.accepts(value))

    def assertNotAccepted(self, value: str) -> None:
        self.assertFalse(self.accepts(value))

    def accepts(self, value: str):
        return self.builder.build().accepts(value)


if __name__ == '__main__':
    unittest.main()
