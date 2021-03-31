from deadseeker.input_validator import InputValidator, ValidatedInput
import os
import unittest
from unittest.mock import patch


class TestInputValidator(unittest.TestCase):

    def setUp(self):
        self.testObj = InputValidator()
        self.env = dict()

    def test_emptyUrlThrowsException(self):
        with self.assertRaises(Exception) as context:
            self.validateInput()
        self.assertTrue(
            '\'INPUT_WEBSITE_URL\' environment' +
            ' variable expected to be provided!'
            in str(context.exception))

    def test_badUrlThrowsException(self):
        self.env['INPUT_WEBSITE_URL'] = 'bananas'
        with self.assertRaises(Exception) as context:
            self.validateInput()
        self.assertTrue(
            'Invalid url provided: bananas'
            in str(context.exception))

    def test_goodUrlReturned(self):
        url = 'https://www.google.com'
        self.env['INPUT_WEBSITE_URL'] = url
        self.validateInput()
        self.assertEqual(1, len(self.result.website_urls))
        self.assertTrue(url in self.result.website_urls)

    def test_multipleGoodUrlsReturned(self):
        url = 'https://www.google.com,https://www.apple.com'
        self.env['INPUT_WEBSITE_URL'] = url
        self.validateInput()
        self.assertEqual(2, len(self.result.website_urls))
        self.assertTrue('https://www.google.com' in self.result.website_urls)
        self.assertTrue('https://www.apple.com' in self.result.website_urls)

    def validateInput(self):
        with patch.dict(os.environ, self.env):
            self.result = self.testObj.validateInput()


if __name__ == '__main__':
    unittest.main()
