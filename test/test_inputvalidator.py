from deadseeker.inputvalidator import InputValidator
from deadseeker.deadseeker import (
    DEFAULT_RETRY_MAX_TRIES,
    DEFAULT_RETRY_MAX_TIME,
    DEFAULT_WEB_AGENT,
    DEFAULT_MAX_DEPTH
)
import os
import unittest
from unittest.mock import patch
from typing import Dict

INCLUDE_EXCLUDE_METHODS_BY_VARNAME: Dict[str, str] = {
    'INPUT_INCLUDE_URL_PREFIX': 'get_includeprefix',
    'INPUT_EXCLUDE_URL_PREFIX': 'get_excludeprefix',
    'INPUT_INCLUDE_URL_SUFFIX': 'get_includesuffix',
    'INPUT_EXCLUDE_URL_SUFFIX': 'get_excludesuffix',
    'INPUT_INCLUDE_URL_CONTAINED': 'get_includecontained',
    'INPUT_EXCLUDE_URL_CONTAINED': 'get_excludecontained',
}


class TestInputValidator(unittest.TestCase):

    def setUp(self):
        self.env: Dict[str, str] = dict()
        self.testObj = InputValidator(self.env)

    def test_emptyUrlThrowsException(self):
        with self.assertRaises(Exception) as context:
            self.testObj.get_urls()
        self.assertExceptionContains(
            context,
            '\'INPUT_WEBSITE_URL\' environment' +
            ' variable expected to be provided!')

    def test_badUrlThrowsException(self):
        self.env['INPUT_WEBSITE_URL'] = 'bananas'
        with self.assertRaises(Exception) as context:
            self.testObj.get_urls()
        self.assertExceptionContains(
            context,
            "'INPUT_WEBSITE_URL' environment variable" +
            " expected to contain valid url: bananas")

    def test_goodUrlReturned(self):
        url = 'https://www.google.com'
        self.env['INPUT_WEBSITE_URL'] = url
        self.testObj.get_urls()
        urls = self.testObj.get_urls()
        self.assertEqual(1, len(urls))
        self.assertTrue(url in urls)

    def test_multipleGoodUrlsReturned(self):
        self.env['INPUT_WEBSITE_URL'] =\
            'https://www.google.com,https://www.apple.com'
        urls = self.testObj.get_urls()
        self.assertEqual(2, len(urls))
        self.assertTrue('https://www.google.com' in urls)
        self.assertTrue('https://www.apple.com' in urls)

    def test_verboseFalseByDefault(self):
        self.assertFalse(
            self.testObj.isVerbos(),
            'Expected default value for verbos to be False')

    def test_verboseTrueWhenTrue(self):
        for verboseStr in [
                'true', 't', 'yes', 'y', 'True',
                'T', 'Yes', 'Y', 'TRUE', 'YES']:
            self.env['INPUT_VERBOSE'] = verboseStr
            self.assertTrue(
                self.testObj.isVerbos(),
                'Expected value to evaluate to' +
                f' verbose true: {verboseStr}')

    def test_verboseFalseWhenFalse(self):
        for verboseStr in [
                'false', 'f', 'no', 'n', 'False',
                'F', 'No', 'N', 'FALSE', 'NO']:
            self.env['INPUT_VERBOSE'] = verboseStr
            self.assertFalse(
                self.testObj.isVerbos(),
                'Expected value to evaluate to' +
                f' verbose false: {verboseStr}')

    def test_defaultIncludeExcludeValueIsEmpty(self):
        for methodName in INCLUDE_EXCLUDE_METHODS_BY_VARNAME.values():
            method = getattr(self.testObj, methodName)
            results = method()
            self.assertFalse(
                results,
                f'Expected method named {methodName} to return empty list, ' +
                'but instead returned: {results}')

    def test_expectedIncludeExcludeValues(self):
        for varName, methodName in INCLUDE_EXCLUDE_METHODS_BY_VARNAME.items():
            method = getattr(self.testObj, methodName)
            self.env.clear()
            self.env[varName] = 'a,b,c,d,e'
            results = method()
            self.assertEqual(5, len(results))

    def test_defaultMaxTries(self):
        self.assertEqual(
            DEFAULT_RETRY_MAX_TRIES, self.testObj.get_retry_maxtries())

    def test_maxTriesMatchesGoodValue(self):
        self.env['INPUT_MAX_RETRIES'] = '5'
        self.assertEqual(
            5, self.testObj.get_retry_maxtries())

    def test_maxTriesRaisesWithBadValue(self):
        self.env['INPUT_MAX_RETRIES'] = 'apples'
        with self.assertRaises(Exception) as context:
            self.testObj.get_retry_maxtries()
        self.assertExceptionContains(
            context,
            "'INPUT_MAX_RETRIES' environment variable expected to be a number")

    def test_defaultMaxTime(self):
        self.assertEqual(
            DEFAULT_RETRY_MAX_TIME, self.testObj.get_retry_maxtime())

    def test_maxTimeMatchesGoodValue(self):
        self.env['INPUT_MAX_RETRY_TIME'] = '5'
        self.assertEqual(
            5, self.testObj.get_retry_maxtime())

    def test_maxTimeRaisesWithBadValue(self):
        self.env['INPUT_MAX_RETRY_TIME'] = 'apples'
        with self.assertRaises(Exception) as context:
            self.testObj.get_retry_maxtime()
        self.assertExceptionContains(
            context,
            "'INPUT_MAX_RETRY_TIME' environment variable" +
            " expected to be a number")

    def test_defaultMaxDepth(self):
        self.assertEqual(
            DEFAULT_MAX_DEPTH, self.testObj.get_maxdepth())

    def test_maxDepthMatchesGoodValue(self):
        self.env['INPUT_MAX_DEPTH'] = '5'
        self.assertEqual(
            5, self.testObj.get_maxdepth())

    def test_maxDepthRaisesWithBadValue(self):
        self.env['INPUT_MAX_DEPTH'] = 'apples'
        with self.assertRaises(Exception) as context:
            self.testObj.get_maxdepth()
        self.assertExceptionContains(
            context,
            "'INPUT_MAX_DEPTH' environment variable" +
            " expected to be a number")

    def test_defaultWebAgent(self):
        self.assertEqual(
            DEFAULT_WEB_AGENT, self.testObj.get_webagent())

    def test_webAgentOverrideValue(self):
        self.env['INPUT_WEB_AGENT_STRING'] = 'My Awesome Web Agent 1.0'
        self.assertEqual(
            'My Awesome Web Agent 1.0', self.testObj.get_webagent())

    def assertExceptionContains(self, context, expected: str):
        actual = str(context.exception)
        self.assertTrue(
            expected in actual,
            f'Expected exception to contain "{expected}", but was "{actual}"')


if __name__ == '__main__':
    unittest.main()
