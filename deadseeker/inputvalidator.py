import validators  # type: ignore
import os
from typing import List
from .deadseeker import (
    DEFAULT_RETRY_MAX_TRIES,
    DEFAULT_RETRY_MAX_TIME,
    DEFAULT_WEB_AGENT
)


class InputValidator:
    def getUrls(self) -> List[str]:
        website_urls = self._splitAndTrim('INPUT_WEBSITE_URL')
        assert website_urls, \
            "'INPUT_WEBSITE_URL' environment variable expected to be provided!"
        for url in website_urls:
            assert validators.url(url), \
                "'INPUT_WEBSITE_URL' environment variable" +\
                f" expected to contain valid url: {url}"
        return website_urls

    def getRetryMaxTries(self) -> int:
        return self._numeric('INPUT_MAX_RETRIES', DEFAULT_RETRY_MAX_TRIES)

    def getRetryMaxTime(self) -> int:
        return self._numeric('INPUT_MAX_RETRY_TIME', DEFAULT_RETRY_MAX_TIME)

    def isVerbos(self) -> bool:
        verboseStr = os.environ.get('INPUT_VERBOSE') or 'false'
        verbose = bool(
            verboseStr and
            verboseStr.lower() in ['true', 't', 'yes', 'y'])
        return verbose

    def getIncludePrefix(self) -> List[str]:
        return self._splitAndTrim('INPUT_INCLUDE_URL_PREFIX')

    def getExcludePrefix(self) -> List[str]:
        return self._splitAndTrim('INPUT_EXCLUDE_URL_PREFIX')

    def getIncludeSuffix(self) -> List[str]:
        return self._splitAndTrim('INPUT_INCLUDE_URL_SUFFIX')

    def getExcludeSuffix(self) -> List[str]:
        return self._splitAndTrim('INPUT_EXCLUDE_URL_SUFFIX')

    def getIncludeContained(self) -> List[str]:
        return self._splitAndTrim('INPUT_INCLUDE_URL_CONTAINED')

    def getExcludeContained(self) -> List[str]:
        return self._splitAndTrim('INPUT_EXCLUDE_URL_CONTAINED')

    def getWebAgent(self) -> str:
        valueStr = os.environ.get('INPUT_WEB_AGENT_STRING')
        if valueStr:
            return valueStr
        return DEFAULT_WEB_AGENT

    def _numeric(self, name: str, default: int) -> int:
        valueStr = os.environ.get(name)
        if valueStr:
            assert valueStr.isnumeric(), \
                    f"'{name}' environment variable" +\
                    " expected to be numeric"
            return int(valueStr)
        return default

    def _splitAndTrim(self, name) -> List[str]:
        valueStr = os.environ.get(name)
        return [] if not valueStr else [x.strip() for x in valueStr.split(',')]
