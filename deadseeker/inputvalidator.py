import validators  # type: ignore
from typing import List, Dict, Union, Optional, Set
import re
import logging
from deadseeker.common import (
    DEFAULT_RETRY_MAX_TRIES,
    DEFAULT_RETRY_MAX_TIME,
    DEFAULT_SEARCH_ATTRS,
    DEFAULT_WEB_AGENT,
    DEFAULT_MAX_DEPTH,
    DEFAULT_CONNECT_LIMIT_PER_HOST,
    DEFAULT_TIMEOUT
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

    def get_search_attrs(self) -> Set[str]:
        search_attrs = self._splitAndTrim('INPUT_SEARCH_ATTRS')
        if search_attrs:
            return set(search_attrs)
        return DEFAULT_SEARCH_ATTRS

    def get_retry_maxtries(self) -> int:
        return self._numeric('INPUT_MAX_RETRIES', DEFAULT_RETRY_MAX_TRIES)

    def get_retry_maxtime(self) -> int:
        return self._numeric('INPUT_MAX_RETRY_TIME', DEFAULT_RETRY_MAX_TIME)

    def get_maxdepth(self) -> int:
        return self._numeric('INPUT_MAX_DEPTH', DEFAULT_MAX_DEPTH)

    def get_connect_limit_per_host(self) -> int:
        return self._numeric(
            'INPUT_CONNECT_LIMIT_PER_HOST', DEFAULT_CONNECT_LIMIT_PER_HOST)

    def get_timeout(self) -> int:
        return self._numeric('INPUT_TIMEOUT', DEFAULT_TIMEOUT)

    def get_verbosity(self) -> Union[bool, int]:
        verboseStr = self.inputs.get('INPUT_VERBOSE')
        if (verboseStr):
            if (self._get_boolean(verboseStr)):
                return True
            levelpattern = '^debug|info|warn(?:ing)?|error|critical$'
            levelmatch = re.search(
                levelpattern, verboseStr, flags=re.IGNORECASE)
            if (levelmatch):
                levelname = levelmatch.group(0).upper()
                return logging.getLevelName(levelname)
        return False

    def get_alwaysgetonsite(self) -> bool:
        return self._get_boolean(self.inputs.get('INPUT_ALWAYS_GET_ONSITE'))

    def get_resolvebeforefilter(self) -> bool:
        return self._get_boolean(
            self.inputs.get('INPUT_RESOLVE_BEFORE_FILTERING'))

    def _get_boolean(self, valueStr: Optional[str]) -> bool:
        truepattern = '^t|true|y|yes|on$'
        return bool(
                valueStr and
                re.search(truepattern, valueStr, flags=re.IGNORECASE))

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
            numpattern = '^-?\\d+$'
            assert re.search(numpattern, valueStr), \
                f"'{name}' environment variable" +\
                " expected to be a number"
            return int(valueStr)
        return default

    def _splitAndTrim(self, name: str) -> List[str]:
        valueStr = self.inputs.get(name)
        return [] if not valueStr else [x.strip() for x in valueStr.split(',')]
