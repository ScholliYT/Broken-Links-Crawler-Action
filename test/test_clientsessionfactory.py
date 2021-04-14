import unittest
from unittest.mock import MagicMock
# from asynctest import MagicMock, patch  # type: ignore
# from aiohttp import ClientSession
from deadseeker.clientsessionfactory import ClientSessionFactory
import asyncio
from aiohttp_retry import RetryClient  # type: ignore


TEST_AGENT = 'TEST_AGENT'


# class AsyncContextManagerMock(MagicMock):
#     async def __aenter__(self):
#         return self.aenter

#     async def __aexit__(self, *args):
#         pass


class TestClientSessionFactory(unittest.TestCase):

    def setUp(self):
        self.testObj = ClientSessionFactory()
        self.config = MagicMock()
        self.config.agent.return_value = TEST_AGENT

    def test_retryClientIsReturned(self):
        self.run_coro()
        self.assertTrue(isinstance(self.actualResult, RetryClient))

    def run_coro(self):
        asyncio.run(self.coro_helper())

    async def coro_helper(self):
        async with self.testObj.createClientSession(
                self.config) as actualResult:
            self.actualResult = actualResult


if __name__ == '__main__':
    unittest.main()
