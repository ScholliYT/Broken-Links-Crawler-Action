# Adapted from:
# https://realpython.com/testing-third-party-apis-with-mock-servers/
import unittest
from unittest.mock import patch
from http.server import HTTPServer, SimpleHTTPRequestHandler
from http import HTTPStatus
import socket
from threading import Thread
import os
import sys
from typing import ClassVar, List
import logging
import pytest
from deadseeker.action import run_action

DIRECTORY = os.path.join(os.path.dirname(__file__), "mock_server")


class MockServerRequestHandler(SimpleHTTPRequestHandler):
    def translate_path(self, path):
        return DIRECTORY + path

    def do_HEAD(self):
        if not self.check_error():
            super().do_HEAD()

    def do_GET(self):
        if not self.check_error():
            super().do_GET()

    def check_error(self):
        if self.path.endswith('/page4.html'):
            self.send_response(HTTPStatus.INTERNAL_SERVER_ERROR)
            self.end_headers()
            return True
        return False


def get_free_port():
    s = socket.socket(socket.AF_INET, type=socket.SOCK_STREAM)
    s.bind(('localhost', 0))
    address, port = s.getsockname()
    s.close()
    return port


@pytest.mark.integrationtest
class TestIntegration(unittest.TestCase):
    url: ClassVar[str]
    mock_server: ClassVar[HTTPServer]
    mock_server_thread: ClassVar[Thread]

    @classmethod
    def setUpClass(cls):
        # Configure mock server.
        port = get_free_port()
        cls.mock_server = HTTPServer(
            ('localhost', port), MockServerRequestHandler)

        # Start running mock server in a separate thread.
        # Daemon threads automatically shut down when the main process exits.
        cls.mock_server_thread = Thread(target=cls.mock_server.serve_forever)
        cls.mock_server_thread.setDaemon(True)
        cls.mock_server_thread.start()
        cls.url = f'http://localhost:{port}'

    def setUp(self):
        self.logger = logging.getLogger('deadseeker.loggingresponsehandler')
        self.env = {
            "INPUT_WEBSITE_URL": self.url,
            "INPUT_MAX_RETRIES": "3",
            "INPUT_MAX_RETRY_TIME": "30",
            "INPUT_VERBOSE": "true"
        }
        self.exit_patch = patch.object(sys, 'exit')
        self.exit = self.exit_patch.start()

    def tearDown(self):
        self.exit_patch.stop()

    def test_works(self):
        self.env['INPUT_EXCLUDE_URL_PREFIX'] = \
            'https://www.google.com,/page3.html,/page4.html'
        with patch.dict(os.environ, self.env):
            run_action()
        self.exit.assert_not_called()

    def test_exit_1_on_any_failure(self):
        self.env['INPUT_EXCLUDE_URL_PREFIX'] = \
            'https://www.google.com'
        with patch.dict(os.environ, self.env):
            run_action()
        self.exit.assert_called_with(1)

    def test_messagesLogged(self):
        self.env['INPUT_EXCLUDE_URL_PREFIX'] = \
            'https://www.google.com'
        with \
                patch.dict(os.environ, self.env),\
                patch.object(self.logger, 'error') as error_mock,\
                patch.object(self.logger, 'info') as info_mock:
            run_action()
            expected_errors = [
                f'::error ::ClientResponseError: 500 - {self.url}/page4.html',
                f'::error ::ClientResponseError: 404 - {self.url}/page3.html'
            ]
            actual_errors: List[str] = []
            for call in error_mock.call_args_list:
                args, kwargs = call
                actual_errors.append(args[0])
            self.assertEqual(expected_errors, actual_errors)

            expected_info_prefixes = [
                f'200 - {self.url} - ',
                f'200 - {self.url}/page1.html - ',
                f'200 - {self.url}/subpages/subpage1.html - ',
                f'200 - {self.url}/page2.html - ',
                f'200 - {self.url}/subpages/subpage2.html - ',
                f'200 - {self.url}/index.html - '
            ]
            actual_infos: List[str] = []
            for call in info_mock.call_args_list:
                args, kwargs = call
                actual_infos.append(args[0])
            self.assertEqual(len(expected_info_prefixes), len(actual_infos))
            for expected_prefix in expected_info_prefixes:
                found = False
                for actual in actual_infos:
                    if(actual.startswith(expected_prefix)):
                        actual_infos.remove(actual)
                        found = True
                        break
                self.assertTrue(
                    found,
                    'Did not find actual result beginning' +
                    ' with "{expected_prefix}"')
            self.assertFalse(
                actual_infos,
                f'Unexpected actual responses: {actual_infos}')


if __name__ == '__main__':
    unittest.main()
