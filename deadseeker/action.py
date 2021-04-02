from .inputvalidator import InputValidator
from .linkacceptor import LinkAcceptorBuilder
from .deadseeker import DeadSeekerConfig, DeadSeeker
import sys
import logging

"""
This file works with inputvalidator to bridge
the inputs from the git workflow action configuration
and convert into the inputs required for the
deadseeker class
"""
inputvalidator = InputValidator()
config = DeadSeekerConfig()
config.max_tries = inputvalidator.getRetryMaxTries()
config.max_time = inputvalidator.getRetryMaxTime()
config.verbose = inputvalidator.isVerbos()
config.linkacceptor = LinkAcceptorBuilder()\
                        .addIncludePrefix(
                            *inputvalidator.getIncludePrefix())\
                        .addExcludePrefix(
                            *inputvalidator.getExcludePrefix())\
                        .addIncludeSuffix(
                            *inputvalidator.getIncludeSuffix())\
                        .addExcludeSuffix(
                            *inputvalidator.getExcludeSuffix())\
                        .addIncludeContained(
                            *inputvalidator.getIncludeContained())\
                        .addExcludeContained(
                            *inputvalidator.getExcludeContained())\
                        .build()
config.max_depth = inputvalidator.getMaxDepth()
urls = inputvalidator.getUrls()
seeker = DeadSeeker(config)
if(config.verbose):
    logging.basicConfig(
        level=logging.DEBUG)
if(len(seeker.seek(urls).failures) > 0):
    logging.critical("::error ::Found some broken links!")
    sys.exit(1)
