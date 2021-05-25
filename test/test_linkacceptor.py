import unittest
from unittest.mock import Mock, patch
from deadseeker.linkacceptor import (
    LinkAcceptorBuilder,
    LinkAcceptor,
    DefaultLinkAcceptorFactory,
    AcceptAllLinkAcceptor
)
from deadseeker.common import SeekerConfig
from typing import List

STRING_1 = 'bananas'
STRING_1_PREFIX = STRING_1[0:3]  # ban
STRING_1_SUFFIX = STRING_1[len(STRING_1)-3:]  # nas
STRING_1_INNER = STRING_1[2:5]  # nan
STRING_2 = 'apples'

ALL_METHODS: List[str] = [
    'addIncludePrefix',
    'addExcludePrefix',
    'addIncludeSuffix',
    'addExcludeSuffix',
    'addIncludeContained',
    'addExcludeContained',
]


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

    def test_AcceptAllIsReturnedWhenOnlyBlanksAreProvided(self):
        for methodName in ALL_METHODS:
            method = getattr(self.builder, methodName)
            method()
            result = self.builder.build()
            self.assertTrue(isinstance(result, AcceptAllLinkAcceptor))
            self.assertTrue(result.accepts(STRING_1))
            self.assertTrue(result.accepts(STRING_2))

    def assertAccepted(self, value: str) -> None:
        self.assertTrue(self.accepts(value))

    def assertNotAccepted(self, value: str) -> None:
        self.assertFalse(self.accepts(value))

    def accepts(self, value: str):
        return self.builder.build().accepts(value)


class TestDefaultLinkAcceptorFactory(unittest.TestCase):

    def setUp(self):
        self.config = Mock(spec=SeekerConfig)
        self.testobj = DefaultLinkAcceptorFactory()

    @patch('deadseeker.linkacceptor.LinkAcceptorBuilder')
    def test_returns_link_acceptor(self, mock_class):
        for inclusion in ['in', 'ex']:
            for strategy in ['prefix', 'suffix', 'contained']:
                attrname = f'{inclusion}clude{strategy}'
                setattr(self.config, attrname, [attrname])
        mock_instance = mock_class()
        mock_instance.addIncludePrefix.return_value = mock_instance
        mock_instance.addExcludePrefix.return_value = mock_instance
        mock_instance.addIncludeSuffix.return_value = mock_instance
        mock_instance.addExcludeSuffix.return_value = mock_instance
        mock_instance.addIncludeContained.return_value = mock_instance
        mock_instance.addExcludeContained.return_value = mock_instance
        expected = Mock(spec=LinkAcceptor)
        mock_instance.build.return_value = expected
        actual = self.testobj.get_link_acceptor(self.config)
        self.assertIs(expected, actual)

        for inclusion in ['In', 'Ex']:
            for strategy in ['Prefix', 'Suffix', 'Contained']:
                attrname = f'{inclusion}clude{strategy}'.lower()
                methodname = f'add{inclusion}clude{strategy}'
                method = getattr(mock_instance, methodname)
                method.assert_any_call(attrname)


if __name__ == '__main__':
    unittest.main()
