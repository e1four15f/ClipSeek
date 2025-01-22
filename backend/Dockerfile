ARG CUDA_VERSION
FROM nvcr.io/nvidia/cuda:${CUDA_VERSION}-base-ubuntu18.04
RUN echo "Building with CUDA_VERSION=${CUDA_VERSION}"
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache \
    VIRTUAL_ENV=/app/.venv \
    DEBIAN_FRONTEND=noninteractive \
    PYTHON_VERSION=3.9.16 \
    HOME="/root"

WORKDIR ${HOME}
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      ffmpeg \
      curl git make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev \
      libsqlite3-dev wget llvm libncurses5-dev libncursesw5-dev xz-utils tk-dev liblzma-dev \
      libffi-dev liblzma-dev libgl1-mesa-glx libglib2.0-0 && \
      curl https://pyenv.run | bash

ENV PYENV_ROOT="${HOME}/.pyenv"
ENV PATH="/app/.venv/bin:${PYENV_ROOT}/shims:${PYENV_ROOT}/bin:${PATH}"

RUN pyenv install ${PYTHON_VERSION} && \
    pyenv global ${PYTHON_VERSION} && \
    pip install poetry==1.8.3

WORKDIR /app

COPY LanguageBind /LanguageBind
COPY backend/pyproject.toml backend/poetry.lock ./
RUN poetry install --without dev && rm -rf $POETRY_CACHE_DIR

COPY backend ./

CMD ["python", "app.py"]
