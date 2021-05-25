from deadseeker.common import (
    DEFAULT_RETRY_MAX_TRIES,
    DEFAULT_RETRY_MAX_TIME,
    DEFAULT_WEB_AGENT,
    DEFAULT_MAX_DEPTH,
    DEFAULT_CONNECT_LIMIT_PER_HOST,
    DEFAULT_TIMEOUT
)
from deadseeker.inputvalidator import InputValidator
import unittest
from logging import DEBUG, INFO, WARN, ERROR, CRITICAL
import logging
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
        self.assert_exception_message(
            context,
            '\'INPUT_WEBSITE_URL\' environment' +
            ' variable expected to be provided!')

    def test_badUrlThrowsException(self):
        self.env['INPUT_WEBSITE_URL'] = 'bananas'
        with self.assertRaises(Exception) as context:
            self.testObj.get_urls()
        self.assert_exception_message(
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
            self.testObj.get_verbosity(),
            'Expected default value for verbos to be False')

    def test_verboseTrueWhenTrue(self):
        for verboseStr in [
                'true', 't', 'True', 'T', 'TRUE',
                'yes', 'y', 'Yes', 'Y', 'YES',
                'on', 'On', 'ON']:
            self.env['INPUT_VERBOSE'] = verboseStr
            self.assertTrue(
                self.testObj.get_verbosity(),
                'Expected value to evaluate to' +
                f' verbose true: {verboseStr}')

    def test_verboseFalseWhenFalse(self):
        for verboseStr in [
                '', 'false', 'f', 'False', 'F', 'FALSE',
                'no', 'n', 'No', 'N', 'NO',
                'off', 'Off', 'OFF']:
            self.env['INPUT_VERBOSE'] = verboseStr
            self.assertFalse(
                self.testObj.get_verbosity(),
                'Expected value to evaluate to' +
                f' verbose false: {verboseStr}')

    def test_alwaysgetonsite_true(self):
        for valueStr in [
                'true', 't', 'True', 'T', 'TRUE',
                'yes', 'y', 'Yes', 'Y', 'YES',
                'on', 'On', 'ON']:
            self.env['INPUT_ALWAYS_GET_ONSITE'] = valueStr
            self.assertTrue(
                self.testObj.get_alwaysgetonsite(),
                'Expected value to evaluate to' +
                f' verbose true: {valueStr}')

    def test_alwaysgetonsite_false(self):
        for valueStr in [
                '', 'false', 'f', 'False', 'F', 'FALSE',
                'no', 'n', 'No', 'N', 'NO',
                'off', 'Off', 'OFF']:
            self.env['INPUT_ALWAYS_GET_ONSITE'] = valueStr
            self.assertFalse(
                self.testObj.get_alwaysgetonsite(),
                'Expected value to evaluate to' +
                f' verbose false: {valueStr}')

    def test_verboseLogLevel(self):
        levelsByString: Dict[str, int] = {
            'debug': DEBUG, 'Debug': DEBUG, 'DEBUG': DEBUG,
            'info': INFO, 'Info': INFO, 'INFO': INFO,
            'warn': WARN, 'Warn': WARN, 'WARN': WARN,
            'warning': WARN, 'Warning': WARN, 'WARNING': WARN,
            'error': ERROR, 'Error': ERROR, 'ERROR': ERROR,
            'critical': CRITICAL, 'Critical': CRITICAL, 'CRITICAL': CRITICAL
        }
        for verboseStr in levelsByString:
            self.env['INPUT_VERBOSE'] = verboseStr
            actual = self.testObj.get_verbosity()
            expected = levelsByString[verboseStr]
            self.assertEqual(
                actual,
                expected,
                'Expected value to evaluate to' +
                f' level {logging.getLevelName(expected)}: {verboseStr}')

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
        self.assert_exception_message(
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
        self.assert_exception_message(
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
        self.assert_exception_message(
            context,
            "'INPUT_MAX_DEPTH' environment variable" +
            " expected to be a number")

    def test_connect_limit_per_host_default(self):
        self.assertEqual(
            DEFAULT_CONNECT_LIMIT_PER_HOST,
            self.testObj.get_connect_limit_per_host())

    def test_connect_limit_per_host_good(self):
        self.env['INPUT_CONNECT_LIMIT_PER_HOST'] = '6'
        self.assertEqual(
            6, self.testObj.get_connect_limit_per_host())

    def test_connect_limit_per_host_bad(self):
        self.env['INPUT_CONNECT_LIMIT_PER_HOST'] = 'apples'
        with self.assertRaises(Exception) as context:
            self.testObj.get_connect_limit_per_host()
        self.assert_exception_message(
            context,
            "'INPUT_CONNECT_LIMIT_PER_HOST' environment variable" +
            " expected to be a number")

    def test_timeout_default(self):
        self.assertEqual(
            DEFAULT_TIMEOUT,
            self.testObj.get_timeout())

    def test_timeout_good(self):
        self.env['INPUT_TIMEOUT'] = '6'
        self.assertEqual(
            6, self.testObj.get_timeout())

    def test_timeout_bad(self):
        self.env['INPUT_TIMEOUT'] = 'apples'
        with self.assertRaises(Exception) as context:
            self.testObj.get_timeout()
        self.assert_exception_message(
            context,
            "'INPUT_TIMEOUT' environment variable" +
            " expected to be a number")

    def test_defaultWebAgent(self):
        self.assertEqual(
            DEFAULT_WEB_AGENT, self.testObj.get_webagent())

    def test_webAgentOverrideValue(self):
        self.env['INPUT_WEB_AGENT_STRING'] = 'My Awesome Web Agent 1.0'
        self.assertEqual(
            'My Awesome Web Agent 1.0', self.testObj.get_webagent())

    def assert_exception_message(self, context, expected: str):
        actual = str(context.exception)
        self.assertEqual(
            expected, actual,
            'Expected exception message to be ' +
            f'"{expected}", but was "{actual}"')


if __name__ == '__main__':
    unittest.main()
