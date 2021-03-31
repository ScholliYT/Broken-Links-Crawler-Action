from deadseeker.input_validator import InputValidator
import os
import unittest
from unittest.mock import patch
from typing import Dict

INCLUDE_EXCLUDE_METHODS_BY_VARNAME: Dict[str, str] = {
    'INPUT_INCLUDE_URL_PREFIX': 'getValidatedIncludePrefix',
    'INPUT_EXCLUDE_URL_PREFIX': 'getValidatedExcludePrefix',
    'INPUT_INCLUDE_URL_SUFFIX': 'getValidatedIncludeSuffix',
    'INPUT_EXCLUDE_URL_SUFFIX': 'getValidatedExcludeSuffix',
    'INPUT_INCLUDE_URL_CONTAINED': 'getValidatedIncludeContained',
    'INPUT_EXCLUDE_URL_CONTAINED': 'getValidatedExcludeContained',
}


class TestInputValidator(unittest.TestCase):

    def setUp(self):
        self.testObj = InputValidator()
        self.env = dict()

    def test_emptyUrlThrowsException(self):
        with self.assertRaises(Exception) as context:
            self.testObj.getValidatedUrl()
        self.assertTrue(
            '\'INPUT_WEBSITE_URL\' environment' +
            ' variable expected to be provided!'
            in str(context.exception))

    @patch.dict(os.environ, {'INPUT_WEBSITE_URL': 'bananas'})
    def test_badUrlThrowsException(self):
        with self.assertRaises(Exception) as context:
            self.testObj.getValidatedUrl()
        self.assertTrue(
            'Invalid url provided: bananas'
            in str(context.exception))

    @patch.dict(os.environ, {'INPUT_WEBSITE_URL': 'https://www.google.com'})
    def test_goodUrlReturned(self):
        self.testObj.getValidatedUrl()
        urls = self.testObj.getValidatedUrl()
        self.assertEqual(1, len(urls))
        self.assertTrue('https://www.google.com' in urls)

    @patch.dict(os.environ,
                {'INPUT_WEBSITE_URL':
                    'https://www.google.com,https://www.apple.com'})
    def test_multipleGoodUrlsReturned(self):
        urls = self.testObj.getValidatedUrl()
        self.assertEqual(2, len(urls))
        self.assertTrue('https://www.google.com' in urls)
        self.assertTrue('https://www.apple.com' in urls)

    def test_verboseFalseByDefault(self):
        self.assertFalse(
            self.testObj.getValidatedVerbosFlag(),
            'Expected default value for verbos to be False')

    def test_verboseTrueWhenTrue(self):
        for verboseStr in [
                'true', 't', 'yes', 'y', 'True',
                'T', 'Yes', 'Y', 'TRUE', 'YES']:
            with patch.dict(
                    os.environ,
                    {'INPUT_VERBOSE': verboseStr}):
                self.assertTrue(
                    self.testObj.getValidatedVerbosFlag(),
                    'Expected value to evaluate to' +
                    f' verbose true: {verboseStr}')

    def test_verboseFalseWhenFalse(self):
        for verboseStr in [
                'false', 'f', 'no', 'n', 'False',
                'F', 'No', 'N', 'FALSE', 'NO']:
            with patch.dict(
                    os.environ,
                    {'INPUT_VERBOSE': verboseStr}):
                self.assertFalse(
                    self.testObj.getValidatedVerbosFlag(),
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
            with patch.dict(
                    os.environ,
                    {varName: 'a,b,c,d,e'}):
                results = method()
                self.assertEqual(
                    5, len(results))


if __name__ == '__main__':
    unittest.main()
