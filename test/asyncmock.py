from unittest.mock import Mock


# The normal Mock class doesn't specifically declare
# the expected functions provided by an asynchronous
# context manager, so we have to declare a special class
# for the python code to recognize the object as an
# async context manager.
# Special thanks to PAWEŁ FERTYK for this one:
# https://pfertyk.me/2017/06/testing-asynchronous-context-managers-in-python/
class AsyncContextManagerMock(Mock):
    async def __aenter__(self):
        return self.aenter

    async def __aexit__(self, *args):
        pass
