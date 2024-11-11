FROM python:3.9-buster

RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg libgl1-mesa-glx libglib2.0-0 && \
    pip install poetry==1.8.3

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache \
    VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

COPY LanguageBind /LanguageBind
COPY backend ./
COPY config.yaml ../

RUN poetry install --without dev && rm -rf $POETRY_CACHE_DIR
CMD ["python", "app.py"]
