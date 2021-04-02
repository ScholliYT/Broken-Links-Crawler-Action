from .inputvalidator import InputValidator
from .linkacceptor import LinkAcceptorBuilder
from .deadseeker import DeadSeeker
from .common import SeekerConfig
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
config.max_tries = inputvalidator.get_retry_maxtries()
config.max_time = inputvalidator.get_retry_maxtime()
config.linkacceptor = LinkAcceptorBuilder()\
                        .addIncludePrefix(
                            *inputvalidator.get_includeprefix())\
                        .addExcludePrefix(
                            *inputvalidator.get_excludeprefix())\
                        .addIncludeSuffix(
                            *inputvalidator.get_includesuffix())\
                        .addExcludeSuffix(
                            *inputvalidator.get_excludesuffix())\
                        .addIncludeContained(
                            *inputvalidator.get_includecontained())\
                        .addExcludeContained(
                            *inputvalidator.get_excludecontained())\
                        .build()
config.max_depth = inputvalidator.get_maxdepth()
urls = inputvalidator.get_urls()
seeker = DeadSeeker(config)

if(len(seeker.seek(urls).failures) > 0):
    logging.critical("::error ::Found some broken links!")
    sys.exit(1)
