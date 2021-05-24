# Container image that runs your code
# based on:
# https://pythonspeed.com/articles/activate-virtualenv-dockerfile/
FROM python:3.8-slim-buster

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# We copy just the requirements.txt first to leverage Docker cache
COPY ./requirements.txt .
RUN python -m pip install --upgrade pip && pip install -r requirements.txt

# Copies your code file from your action repository to the filesystem path `/` of the container
COPY deadseeker ./deadseeker

# Code file to execute when the docker container starts up (`deadseeker.py`)
ENTRYPOINT [ "python", "-m", "deadseeker.action" ]
