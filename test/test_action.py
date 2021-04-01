import unittest
from unittest.mock import patch
import os
from deadseeker.deadseeker import DeadSeeker


class TestAction(unittest.TestCase):

    @patch.dict(
        os.environ,
        {
            "INPUT_WEBSITE_URL": "https://www.ncpilgrimage.org",
            "INPUT_MAX_RETRIES": "",
            "INPUT_MAX_RETRY_TIME": "",
            "INPUT_VERBOSE": "true",
            "INPUT_INCLUDE_URL_PREFIX": "",
            "INPUT_EXCLUDE_URL_PREFIX": "mailto:,tel:,/cdn-cgi/",
            "INPUT_INCLUDE_URL_SUFFIX": "",
            "INPUT_EXCLUDE_URL_SUFFIX": "",
            "INPUT_INCLUDE_URL_CONTAINED": "",
            "INPUT_EXCLUDE_URL_CONTAINED": "",
            "INPUT_WEB_AGENT_STRING": "",
        })
    @patch.object(DeadSeeker, 'seek')
    def test_testAction(self, SeekMock):
        SeekMock.return_value = 0
        self.import_action()
        SeekMock.assert_called()

    def import_action(self):
        import deadseeker.action    # noqa: F401

