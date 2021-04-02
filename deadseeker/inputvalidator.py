import validators  # type: ignore
from typing import List, Dict, Union
import re
import logging
from .deadseeker import (
    DEFAULT_RETRY_MAX_TRIES,
    DEFAULT_RETRY_MAX_TIME,
    DEFAULT_WEB_AGENT,
    DEFAULT_MAX_DEPTH
)


class InputValidator:
    def __init__(self, inputs: Dict[str, str]):
        self.inputs = inputs

    def get_urls(self) -> List[str]:
        website_urls = self._splitAndTrim('INPUT_WEBSITE_URL')
        assert website_urls, \
            "'INPUT_WEBSITE_URL' environment variable expected to be provided!"
        for url in website_urls:
            assert validators.url(url), \
                "'INPUT_WEBSITE_URL' environment variable" +\
                f" expected to contain valid url: {url}"
        return website_urls

    def get_retry_maxtries(self) -> int:
        return self._numeric('INPUT_MAX_RETRIES', DEFAULT_RETRY_MAX_TRIES)

    def get_retry_maxtime(self) -> int:
        return self._numeric('INPUT_MAX_RETRY_TIME', DEFAULT_RETRY_MAX_TIME)

    def get_maxdepth(self) -> int:
        return self._numeric('INPUT_MAX_DEPTH', DEFAULT_MAX_DEPTH)

    def get_verbosity(self) -> Union[bool, int]:
        verboseStr = self.inputs.get('INPUT_VERBOSE')
        if(verboseStr):
            truepattern = '^t|true|y|yes|on$'
            if(re.search(truepattern, verboseStr, flags=re.IGNORECASE)):
                return True
            levelpattern = '^(debug|info|warn|warning|error|critical)$'
            levelmatch = re.search(
                levelpattern, verboseStr, flags=re.IGNORECASE)
            if(levelmatch):
                levelname = levelmatch.group(0).upper()
                return logging.getLevelName(levelname)
        return False

    def get_includeprefix(self) -> List[str]:
        return self._splitAndTrim('INPUT_INCLUDE_URL_PREFIX')

    def get_excludeprefix(self) -> List[str]:
        return self._splitAndTrim('INPUT_EXCLUDE_URL_PREFIX')

    def get_includesuffix(self) -> List[str]:
        return self._splitAndTrim('INPUT_INCLUDE_URL_SUFFIX')

    def get_excludesuffix(self) -> List[str]:
        return self._splitAndTrim('INPUT_EXCLUDE_URL_SUFFIX')

    def get_includecontained(self) -> List[str]:
        return self._splitAndTrim('INPUT_INCLUDE_URL_CONTAINED')

    def get_excludecontained(self) -> List[str]:
        return self._splitAndTrim('INPUT_EXCLUDE_URL_CONTAINED')

    def get_webagent(self) -> str:
        valueStr = self.inputs.get('INPUT_WEB_AGENT_STRING')
        if valueStr:
            return valueStr
        return DEFAULT_WEB_AGENT

    def _numeric(self, name: str, default: int) -> int:
        valueStr = self.inputs.get(name)
        if valueStr:
            assert valueStr.lstrip('-').isdigit(), \
                    f"'{name}' environment variable" +\
                    " expected to be a number"
            return int(valueStr)
        return default

    def _splitAndTrim(self, name) -> List[str]:
        valueStr = self.inputs.get(name)
        return [] if not valueStr else [x.strip() for x in valueStr.split(',')]
