# Adapted from:
# https://realpython.com/testing-third-party-apis-with-mock-servers/
import unittest
from unittest.mock import patch
from http.server import HTTPServer, SimpleHTTPRequestHandler
from http import HTTPStatus
from deadseeker.deadseeker import DeadSeeker, DeadSeekerConfig
from deadseeker.linkacceptor import LinkAcceptorBuilder
import socket
from threading import Thread
import os
from typing import ClassVar
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
        cls.url = f'http://localhost:{port}/'

    def setUp(self):
        self.config = DeadSeekerConfig()

    def test_request_response(self):
        self.config.linkacceptor = \
            LinkAcceptorBuilder().addExcludePrefix(
                    'https://www.google.com').build()
        seeker = DeadSeeker(self.config)
        logger = logging.getLogger('deadseeker.DeadSeeker')
        with patch.object(logger, 'getEffectiveLevel') as log_level:
            log_level.return_value = DEBUG
            response = seeker.seek([self.url])
            actualfailed = len(response.failures)
            self.assertEqual(2, actualfailed)


if __name__ == '__main__':
    unittest.main()
