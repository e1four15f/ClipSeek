FROM python:3.9-buster as builder

RUN pip install poetry==1.8.3

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_INSTALLER_PARALLEL=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

COPY LanguageBind /LanguageBind

WORKDIR /app

COPY backend ./
RUN touch README.md

RUN poetry install --without dev && rm -rf $POETRY_CACHE_DIR

# The runtime image, used to just run the code provided its virtual environment
FROM nvidia/cuda:11.6.1-base-ubuntu20.04 as runtime
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ffmpeg libgl1-mesa-glx libglib2.0-0

WORKDIR /app
ENV VIRTUAL_ENV=/app/.venv \
    PATH="$VIRTUAL_ENV/bin:$PATH"
COPY --from=builder $VIRTUAL_ENV $VIRTUAL_ENV

RUN ln -s $VIRTUAL_ENV/bin/python /bin/python && \
    ln -s $VIRTUAL_ENV/bin/pip /bin/pip

RUN pip install poetry==1.8.3

COPY LanguageBind /LanguageBind
COPY backend ./
COPY config.yaml ../

CMD ["python", "app.py"]
