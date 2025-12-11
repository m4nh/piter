# syntax=docker/dockerfile:1
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

COPY pyproject.toml README.md LICENSE.txt ./
COPY piter piter

RUN pip install --upgrade pip \
    && pip install --no-cache-dir .

ENTRYPOINT ["piter"]
CMD ["--help"]
