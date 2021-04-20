import unittest
from unittest.mock import patch, MagicMock
import os
from deadseeker.common import (
    SeekResults,
    SeekerConfig
)
from logging import DEBUG, INFO, WARN, ERROR, CRITICAL
import logging
from deadseeker.action import run_action


class TestAction(unittest.TestCase):

    def setUp(self):
        self.env = {
            "INPUT_WEBSITE_URL": "https://www.ncpilgrimage.org",
            "INPUT_MAX_RETRIES": "3",
            "INPUT_MAX_RETRY_TIME": "30",
            "INPUT_MAX_DEPTH": "2",
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
        self.deadseeker_patch = patch('deadseeker.action.DeadSeeker')
        self.deadseeker = self.deadseeker_patch.start()
        self.seek = self.deadseeker.return_value.seek
        self.exit_patch = patch('sys.exit')
        self.exit = self.exit_patch.start()
        self.seekresults = SeekResults()
        logger = logging.getLogger('deadseeker.action')
        self.critical_mock = patch.object(logger, 'critical')
        self.critical = self.critical_mock.start()
        self.loggingresponsehandler_patch = \
            patch('deadseeker.action.LoggingUrlFetchResponseHandler')
        self.loggingresponsehandler = self.loggingresponsehandler_patch.start()

    def tearDown(self):
        self.environ_patch.stop()
        self.deadseeker_patch.stop()
        self.exit_patch.stop()
        self.critical_mock.stop()
        self.loggingresponsehandler_patch.stop()

    def test_no_exit_when_no_failed(self):
        self.seek.return_value = self.seekresults
        run_action()
        self.seek.assert_called_with(
            ['https://www.ncpilgrimage.org'],
            self.loggingresponsehandler())
        self.exit.assert_not_called()

    def test_no_log_critical_when_no_failed(self):
        self.seek.return_value = self.seekresults
        run_action()
        self.critical.assert_not_called()

    def test_testActionExitWhenFailed(self):
        self.seekresults.failures.append(MagicMock())
        self.seek.return_value = self.seekresults
        run_action()
        self.seek.assert_called_with(
            ['https://www.ncpilgrimage.org'],
            self.loggingresponsehandler())
        self.exit.assert_called_with(1)

    def test_log_critical_when_failed(self):
        self.seekresults.failures.append(MagicMock())
        self.seek.return_value = self.seekresults
        run_action()
        self.critical.assert_called_with('::error ::Found some broken links!')

    def test_verboseTrueSetsLoggingToDebug(self):
        with patch.dict(os.environ, {'INPUT_VERBOSE': 'true'}),\
                patch.object(logging, 'basicConfig') as mock_debug:
            run_action()
            mock_debug.assert_called_once_with(
                level=logging.INFO,
                format='%(message)s')

    def test_verboseFalseSetsLoggingToSevere(self):
        with patch.dict(os.environ, {'INPUT_VERBOSE': 'false'}),\
                patch.object(logging, 'basicConfig') as mock_debug:
            run_action()
            mock_debug.assert_called_once_with(
                level=logging.CRITICAL,
                format='%(message)s')

    def test_verboseLogLevelSetsLoggingToSevere(self):
        for level in [DEBUG, INFO, WARN, ERROR, CRITICAL]:
            levelname = logging.getLevelName(level)
            with patch.dict(os.environ, {'INPUT_VERBOSE': levelname.lower()}),\
                    patch.object(logging, 'basicConfig') as mock_debug:
                run_action()
                mock_debug.assert_called_once_with(
                    level=level)

    def test_config_values(self):
        run_action()
        self.deadseeker.assert_called_once()
        config: SeekerConfig = self.deadseeker.call_args.args[0]
        self.assertEqual(config.max_tries, 3)
        self.assertEqual(config.max_time, 30)
        self.assertEqual(config.max_depth, 2)
        self.assertEqual(config.includeprefix, [])
        self.assertEqual(
            config.excludeprefix, ['mailto:', 'tel:', '/cdn-cgi/'])
        self.assertEqual(config.includesuffix, [])
        self.assertEqual(config.excludesuffix, [])
        self.assertEqual(config.includecontained, [])
        self.assertEqual(config.excludecontained, [])
