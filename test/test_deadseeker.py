# Adapted from:
# https://realpython.com/testing-third-party-apis-with-mock-servers/
import unittest
from unittest.mock import patch
from http.server import HTTPServer, SimpleHTTPRequestHandler
from http import HTTPStatus
from deadseeker import DeadSeeker, SeekerConfig, LinkAcceptorBuilder
import socket
from threading import Thread
import os
from typing import ClassVar, List
from logging import DEBUG
import logging

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


class TestDeadSeeker(unittest.TestCase):
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
        self.config = SeekerConfig()
        self.logger = logging.getLogger('deadseeker.deadseeker')
        self.builder = LinkAcceptorBuilder()

    def test_numberFailedIs2(self):
        self.builder.addExcludePrefix('https://www.google.com')
        response = self._seek_with_logging()
        actualfailed = len(response.failures)
        self.assertEqual(2, actualfailed)

    def test_numberFailedIs0WithMoreExcludes(self):
        self.builder.addExcludePrefix(
            'https://www.google.com',
            '/page3.html',
            '/page4.html')
        response = self._seek_with_logging()
        actualfailed = len(response.failures)
        self.assertEqual(0, actualfailed)

    def test_messagesLogged(self):
        self.builder.addExcludePrefix('https://www.google.com')
        with patch.object(self.logger, 'error') as error_mock,\
                patch.object(self.logger, 'info') as info_mock:
            self._seek_with_logging()
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
                f'200 - {self.url}/subpages/subpage2.html - '
            ]
            actual_infos: List[str] = []
            for call in info_mock.call_args_list:
                args, kwargs = call
                actual_infos.append(args[0])
            self.assertEqual(len(expected_info_prefixes), len(actual_infos))
            for expected_prefix, actual \
                    in zip(expected_info_prefixes, actual_infos):
                self.assertTrue(actual.startswith(expected_prefix))

    def _seek_with_logging(self):
        self.config.linkacceptor = self.builder.build()
        seeker = DeadSeeker(self.config)
        with patch.object(self.logger, 'getEffectiveLevel') as log_level:
            log_level.return_value = DEBUG
            return seeker.seek([self.url])


if __name__ == '__main__':
    unittest.main()
