# Container image that runs your code
FROM python:3.8-slim-buster

# We copy just the requirements.txt first to leverage Docker cache
COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip3 install -r requirements.txt

# Copies your code file from your action repository to the filesystem path `/` of the container
COPY deadseeker.py /app/deadseeker.py

# Code file to execute when the docker container starts up (`deadseeker.py`)
CMD [ "python", "/app/deadseeker.py" ]
