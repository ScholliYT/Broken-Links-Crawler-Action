# Container image that runs your code
FROM python:3.11-slim-buster

RUN python3.8 -m pip install pipx
RUN pipx install "poetry==1.2.2"
# We need to ensure taht poetry is available (alternative: RUN pipx ensurepath)
ENV PATH="{PATH}:/root/.local/bin" 


# We copy just the pyproject.toml and pyproject.lock first to leverage Docker cache
COPY pyproject.toml poetry.lock ./
RUN poetry install --only main --no-root --no-interaction --no-ansi -v

# Copies your code file from your action repository to the filesystem path `/` of the container
COPY deadseeker /modules/deadseeker/

# Adds our module to sys.path so python can find it
ENV PYTHONPATH "${PYTHONPATH}:/modules/"

# Code file to execute when the docker container starts up (`deadseeker.py`)
ENTRYPOINT [ "poetry", "run", "python", "-m", "deadseeker.action" ]
