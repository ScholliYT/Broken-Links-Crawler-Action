import unittest
from unittest.mock import patch, MagicMock
from deadseeker.common import (
    SeekResults,
    SeekerConfig
)
from deadseeker.inputvalidator import InputValidator
from logging import DEBUG, INFO, WARN, ERROR, CRITICAL
import logging
from deadseeker.action import run_action

TEST_URLS = ['http://test.com/']
TEST_MAX_DEPTH = 2
TEST_MAX_TRIES = 3
TEST_MAX_TIME = 30
TEST_INCLUDE_PREFIX = ['includeprefix']
TEST_EXCLUDE_PREFIX = ['excludeprefix']
TEST_INCLUDE_SUFFIX = ['includesuffix']
TEST_EXCLUDE_SUFFIX = ['excludesuffix']
TEST_INCLUDE_CONTAINED = ['includecontained']
TEST_EXCLUDE_CONTAINED = ['excludecontained']
TEST_ALWAYS_GET_ONSITE = True
TEST_MAX_CONCUR_REQUESTS = 3


class TestAction(unittest.TestCase):

    def setUp(self):
        self.inputvalidator_patch = patch('deadseeker.action.InputValidator')
        self.inputvalidator_class = self.inputvalidator_patch.start()
        self.inputvalidator: InputValidator = \
            self.inputvalidator_class.return_value
        self.inputvalidator.get_urls.return_value = TEST_URLS
        self.inputvalidator.get_maxdepth.return_value = TEST_MAX_DEPTH
        self.inputvalidator.get_retry_maxtime.return_value = TEST_MAX_TIME
        self.inputvalidator.get_retry_maxtries.return_value = TEST_MAX_TRIES
        self.inputvalidator.get_maxconcurrequests.return_value = \
            TEST_MAX_CONCUR_REQUESTS
        self.inputvalidator.get_includeprefix.return_value = \
            TEST_INCLUDE_PREFIX
        self.inputvalidator.get_excludeprefix.return_value = \
            TEST_EXCLUDE_PREFIX
        self.inputvalidator.get_includesuffix.return_value = \
            TEST_INCLUDE_SUFFIX
        self.inputvalidator.get_excludesuffix.return_value = \
            TEST_EXCLUDE_SUFFIX
        self.inputvalidator.get_includecontained.return_value = \
            TEST_INCLUDE_CONTAINED
        self.inputvalidator.get_excludecontained.return_value = \
            TEST_EXCLUDE_CONTAINED
        self.inputvalidator.get_alwaysgetonsite.return_value = \
            TEST_ALWAYS_GET_ONSITE
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
        self.inputvalidator_patch.stop()
        self.deadseeker_patch.stop()
        self.exit_patch.stop()
        self.critical_mock.stop()
        self.loggingresponsehandler_patch.stop()

    def test_no_exit_when_no_failed(self):
        self.seek.return_value = self.seekresults
        run_action()
        self.seek.assert_called_with(
            TEST_URLS,
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
            TEST_URLS,
            self.loggingresponsehandler())
        self.exit.assert_called_with(1)

    def test_log_critical_when_failed(self):
        self.seekresults.failures.append(MagicMock())
        self.seek.return_value = self.seekresults
        run_action()
        self.critical.assert_called_with('::error ::Found some broken links!')

    def test_verboseTrueSetsLoggingToDebug(self):
        self.inputvalidator.get_verbosity.return_value = True
        with patch.object(logging, 'basicConfig') as mock_debug:
            run_action()
            mock_debug.assert_called_once_with(
                level=logging.INFO,
                format='%(message)s')

    def test_verboseFalseSetsLoggingToSevere(self):
        self.inputvalidator.get_verbosity.return_value = False
        with patch.object(logging, 'basicConfig') as mock_debug:
            run_action()
            mock_debug.assert_called_once_with(
                level=logging.CRITICAL,
                format='%(message)s')

    def test_verboseLogLevelSetsLoggingToSevere(self):
        for level in [DEBUG, INFO, WARN, ERROR, CRITICAL]:
            self.inputvalidator.get_verbosity.return_value = level
            with patch.object(logging, 'basicConfig') as mock_debug:
                run_action()
                mock_debug.assert_called_once_with(
                    level=level)

    def test_config_values(self):
        run_action()
        self.deadseeker.assert_called_once()
        config: SeekerConfig = self.deadseeker.call_args.args[0]
        self.assertEqual(config.max_tries, TEST_MAX_TRIES)
        self.assertEqual(config.max_time, TEST_MAX_TIME)
        self.assertEqual(config.max_depth, TEST_MAX_DEPTH)
        self.assertEqual(config.includeprefix, TEST_INCLUDE_PREFIX)
        self.assertEqual(
            config.excludeprefix, TEST_EXCLUDE_PREFIX)
        self.assertEqual(config.includesuffix, TEST_INCLUDE_SUFFIX)
        self.assertEqual(config.excludesuffix, TEST_EXCLUDE_SUFFIX)
        self.assertEqual(config.includecontained, TEST_INCLUDE_CONTAINED)
        self.assertEqual(config.excludecontained, TEST_EXCLUDE_CONTAINED)
        self.assertEqual(config.alwaysgetonsite, TEST_ALWAYS_GET_ONSITE)
        self.assertEqual(config.max_concurrequests, TEST_MAX_CONCUR_REQUESTS)
