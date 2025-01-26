FROM python:3.11-slim-buster

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    postgresql-client \
    libpq-dev \
    libffi-dev \
    libssl-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

ENV POETRY_VERSION=1.8.2 \
    POETRY_HOME=/opt/poetry \
    POETRY_VIRTUALENVS_IN_PROJECT=false \
    POETRY_CACHE_DIR=/opt/.cache \
    # pip:
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    # python:
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONHASHSEED=random \
    PYTHONPATH=/app


RUN pip install poetry==${POETRY_VERSION}

WORKDIR ${PYTHONPATH}

COPY poetry.lock pyproject.toml ./
RUN poetry check
COPY . ${PYTHONPATH}
RUN poetry install --without dev

RUN chmod +x registration_app/docker_run.sh