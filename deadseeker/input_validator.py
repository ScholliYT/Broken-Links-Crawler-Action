import validators
import os
from typing import List


class InputValidator:
    def getValidatedUrl(self) -> List[str]:
        website_urls = self.splitAndTrim('INPUT_WEBSITE_URL')
        assert website_urls, \
            "'INPUT_WEBSITE_URL' environment variable expected to be provided!"
        for url in website_urls:
            assert validators.url(url), \
                f"Invalid url provided: {url}"
        return website_urls

    def getValidatedVerbosFlag(self) -> bool:
        verboseStr = os.environ.get('INPUT_VERBOSE') or 'false'
        verbose = bool(
            verboseStr and
            verboseStr.lower() in ['true', 't', 'yes', 'y'])
        return verbose

    def getValidatedIncludePrefix(self) -> List[str]:
        return self.splitAndTrim('INPUT_INCLUDE_URL_PREFIX')

    def getValidatedExcludePrefix(self) -> List[str]:
        return self.splitAndTrim('INPUT_EXCLUDE_URL_PREFIX')

    def getValidatedIncludeSuffix(self) -> List[str]:
        return self.splitAndTrim('INPUT_INCLUDE_URL_SUFFIX')

    def getValidatedExcludeSuffix(self) -> List[str]:
        return self.splitAndTrim('INPUT_EXCLUDE_URL_SUFFIX')

    def getValidatedIncludeContained(self) -> List[str]:
        return self.splitAndTrim('INPUT_INCLUDE_URL_CONTAINED')

    def getValidatedExcludeContained(self) -> List[str]:
        return self.splitAndTrim('INPUT_EXCLUDE_URL_CONTAINED')

    def splitAndTrim(self, name) -> List[str]:
        valueStr = os.environ.get(name)
        return [] if not valueStr else [x.strip() for x in valueStr.split(',')]
