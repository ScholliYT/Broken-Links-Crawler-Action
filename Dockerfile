# Container image that runs your code
FROM python:3.7-slim-buster

# Copies your code file from your action repository to the filesystem path `/` of the container
COPY deadseeker.py /deadseeker.py

# Code file to execute when the docker container starts up (`deadseeker.py`)
CMD [ "python", "deadseeker.py" ]