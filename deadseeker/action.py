from .inputvalidator import InputValidator
from .deadseeker import DeadSeeker
from .common import SeekerConfig
from .loggingresponsehandler import LoggingUrlFetchResponseHandler
import sys
import os
import logging
from typing import Union

"""
This file works with inputvalidator to bridge
the inputs from the git workflow action configuration
and convert into the inputs required for the
deadseeker class
"""

logger = logging.getLogger(__name__)


def run_action() -> None:
    inputvalidator = InputValidator(dict(os.environ))

    verbosity: Union[bool, int] = inputvalidator.get_verbosity()
    if(isinstance(verbosity, bool)):
        if(verbosity):
            logging.basicConfig(
                level=logging.INFO,
                format='%(message)s')
        else:
            logging.basicConfig(
                level=logging.CRITICAL,
                format='%(message)s')
    else:
        logging.basicConfig(level=verbosity)

    config = SeekerConfig()
    config.max_concurrequests = inputvalidator.get_maxconcurrequests()
    config.max_tries = inputvalidator.get_retry_maxtries()
    config.max_time = inputvalidator.get_retry_maxtime()
    config.alwaysgetonsite = inputvalidator.get_alwaysgetonsite()
    for inclusion in ['in', 'ex']:
        for strategy in ['prefix', 'suffix', 'contained']:
            attrname = f'{inclusion}clude{strategy}'
            getmethodname = f'get_{attrname}'
            getmethod = getattr(inputvalidator, getmethodname)
            value = getmethod()
            setattr(config, attrname, value)
    config.max_depth = inputvalidator.get_maxdepth()
    urls = inputvalidator.get_urls()
    seeker = DeadSeeker(config)
    responsehandler = LoggingUrlFetchResponseHandler()
    if(len(seeker.seek(urls, responsehandler).failures, ) > 0):
        logger.critical("::error ::Found some broken links!")
        sys.exit(1)


if __name__ == '__main__':  # pragma: no mutate
    run_action()
