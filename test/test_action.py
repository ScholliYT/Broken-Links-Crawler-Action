import unittest
from unittest.mock import patch, MagicMock
import os
from deadseeker import DeadSeeker, SeekResults
from importlib import reload
from logging import DEBUG, INFO, WARN, ERROR, CRITICAL
import logging


class TestAction(unittest.TestCase):

    def setUp(self):
        self.env = {
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
        }
        self.environ_patch = \
            patch.dict(os.environ, self.env)
        self.environ_patch.start()
        self.seek_patch = patch.object(DeadSeeker, 'seek')
        self.seek = self.seek_patch.start()
        self.exit_patch = patch('sys.exit')
        self.exit = self.exit_patch.start()
        self.seekresults = SeekResults()

    def tearDown(self):
        self.environ_patch.stop()
        self.seek_patch.stop()
        self.exit_patch.stop()

    def test_testActionNoExitWhenNoFailed(self):
        self.seek.return_value = self.seekresults
        self.import_action()
        self.seek.assert_called()
        self.exit.assert_not_called()

    def test_testActionExitWhenFailed(self):
        self.seekresults.failures.append(MagicMock())
        self.seek.return_value = self.seekresults
        self.import_action()
        self.seek.assert_called()
        self.exit.assert_called_with(1)

    def test_verboseTrueSetsLoggingToDebug(self):
        with patch.dict(os.environ, {'INPUT_VERBOSE': 'true'}),\
                patch.object(logging, 'basicConfig') as mock_debug:
            self.import_action()
            mock_debug.assert_called_once_with(
                level=logging.INFO,
                format='%(message)s')

    def test_verboseFalseSetsLoggingToSevere(self):
        with patch.dict(os.environ, {'INPUT_VERBOSE': 'false'}),\
                patch.object(logging, 'basicConfig') as mock_debug:
            self.import_action()
            mock_debug.assert_called_once_with(
                level=logging.CRITICAL,
                format='%(message)s')

    def test_verboseLogLevelSetsLoggingToSevere(self):
        for level in [DEBUG, INFO, WARN, ERROR, CRITICAL]:
            levelname = logging.getLevelName(level)
            with patch.dict(os.environ, {'INPUT_VERBOSE': levelname.lower()}),\
                    patch.object(logging, 'basicConfig') as mock_debug:
                self.import_action()
                mock_debug.assert_called_once_with(
                    level=level)

    def import_action(self):
        import deadseeker.action
        # must realod because import caches
        reload(deadseeker.action)
