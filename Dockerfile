# Container image that runs your code
FROM python:3.11-slim-buster

# pip
ENV PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

# poetry
ENV POETRY_VERSION=1.2.2 \
    POETRY_NO_INTERACTION=1 \
    POETRY_CACHE_DIR='/var/cache/pypoetry' \
    PYSETUP_PATH="/opt/pysetup" \
    VENV_PATH="/opt/pysetup/.venv" \
    PATH="$VENV_PATH/bin:$PATH:/root/.local/bin"


RUN python3.11 -m pip install pipx
RUN pipx install "poetry==$POETRY_VERSION"
# We need to ensure taht poetry is available (alternative: RUN pipx ensurepath)
# ENV PATH="{PATH}:/root/.local/bin" 
RUN pipx ensurepath

# We copy just the pyproject.toml and pyproject.lock first to leverage Docker cache
COPY pyproject.toml poetry.lock ./
RUN poetry install --only main --no-root --no-interaction --no-ansi -v

# Copies your code file from your action repository to the filesystem path `/` of the container
COPY deadseeker /modules/deadseeker/

# Adds our module to sys.path so python can find it
ENV PYTHONPATH "${PYTHONPATH}:/modules/"

# Code file to execute when the docker container starts up (`deadseeker.py`)
ENTRYPOINT [ "poetry", "run", "python", "-m", "deadseeker.action" ]
